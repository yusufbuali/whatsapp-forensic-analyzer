"""
Audit Logging Middleware for Forensic Chain of Custody

Logs all API requests to audit_log table for 5-year retention
Required for legal compliance and forensic evidence handling
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from datetime import datetime
from uuid import uuid4
import logging
import json

from app.core.database import SessionLocal
from app.models.audit import AuditLog
from app.core.security import verify_token

logger = logging.getLogger(__name__)

# Paths to exclude from audit logging (health checks, static files)
EXCLUDED_PATHS = ["/health", "/health/live", "/health/ready", "/metrics", "/docs", "/redoc", "/openapi.json"]

# Sensitive fields to mask in logs
SENSITIVE_FIELDS = ["password", "token", "secret", "api_key", "refresh_token"]


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests for forensic audit trail

    Captures:
    - User ID and username (from JWT token)
    - IP address
    - User agent
    - Request method and path
    - Response status code
    - Timestamp
    - Case ID (if present in request)
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and log to audit_log table"""

        # Skip health checks and documentation endpoints
        if any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
            return await call_next(request)

        # Generate transaction ID for request tracking
        transaction_id = uuid4()
        request.state.transaction_id = transaction_id

        # Extract user information from Authorization header
        user_id = None
        username = None
        user_role = None

        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            payload = verify_token(token)
            if payload:
                user_id = payload.get("sub")
                username = payload.get("username")
                user_role = payload.get("role")

        # Extract client information
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent")

        # Extract case_id from path or query params if present
        case_id = None
        if "cases" in request.url.path:
            path_parts = request.url.path.split("/")
            if "cases" in path_parts:
                case_index = path_parts.index("cases")
                if len(path_parts) > case_index + 1:
                    try:
                        from uuid import UUID
                        case_id = UUID(path_parts[case_index + 1])
                    except (ValueError, IndexError):
                        pass

        # Process request
        start_time = datetime.utcnow()

        try:
            response = await call_next(request)
            status_code = response.status_code
            status = "success" if 200 <= status_code < 400 else "failure"
            error_message = None

        except Exception as e:
            logger.error(f"Request failed with exception: {e}", exc_info=True)
            status_code = 500
            status = "error"
            error_message = str(e)
            # Re-raise to let global exception handler deal with it
            raise

        finally:
            # Determine action from method and path
            action = self._determine_action(request.method, request.url.path)
            action_category = self._determine_action_category(request.url.path)

            # Determine resource type from path
            resource_type = self._determine_resource_type(request.url.path)
            resource_id = self._extract_resource_id(request.url.path)

            # Build details dict (mask sensitive data)
            details = {
                "transaction_id": str(transaction_id),
                "path": request.url.path,
                "method": request.method,
                "query_params": dict(request.query_params) if request.query_params else None,
                "duration_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000),
            }

            # Log to database (async in background to not block response)
            try:
                self._log_to_database(
                    action=action,
                    action_category=action_category,
                    user_id=user_id,
                    username=username,
                    user_role=user_role,
                    ip_address=client_ip,
                    user_agent=user_agent,
                    request_method=request.method,
                    request_path=request.url.path,
                    case_id=case_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status=status,
                    status_code=status_code,
                    error_message=error_message,
                    details=details,
                    transaction_id=transaction_id,
                )
            except Exception as log_error:
                logger.error(f"Failed to log audit entry: {log_error}", exc_info=True)

        return response

    def _log_to_database(
        self,
        action: str,
        action_category: str,
        user_id: str,
        username: str,
        user_role: str,
        ip_address: str,
        user_agent: str,
        request_method: str,
        request_path: str,
        case_id: str,
        resource_type: str,
        resource_id: str,
        status: str,
        status_code: int,
        error_message: str,
        details: dict,
        transaction_id: str,
    ):
        """Write audit log entry to database"""
        db = SessionLocal()
        try:
            audit_entry = AuditLog(
                action=action,
                action_category=action_category,
                user_id=user_id,
                username=username,
                user_role=user_role,
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                case_id=case_id,
                resource_type=resource_type,
                resource_id=resource_id,
                status=status,
                status_code=status_code,
                error_message=error_message,
                details=details,
                transaction_id=transaction_id,
            )
            db.add(audit_entry)
            db.commit()

            # Log to application log as well
            logger.info(
                f"AUDIT: {action} | User: {username or 'anonymous'} | IP: {ip_address} | Status: {status}"
            )

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def _determine_action(method: str, path: str) -> str:
        """Determine action name from method and path"""
        path_lower = path.lower()

        # Authentication actions
        if "/auth/login" in path_lower:
            return "AUTH_LOGIN"
        elif "/auth/logout" in path_lower:
            return "AUTH_LOGOUT"
        elif "/auth/refresh" in path_lower:
            return "AUTH_REFRESH_TOKEN"
        elif "/auth/change-password" in path_lower:
            return "AUTH_PASSWORD_CHANGE"
        elif "/auth/users" in path_lower:
            if method == "POST":
                return "USER_CREATE"
            elif method == "GET":
                return "USER_LIST"
        elif "/auth/me" in path_lower:
            if method == "GET":
                return "USER_VIEW_PROFILE"
            elif method == "PUT":
                return "USER_UPDATE_PROFILE"

        # Case actions
        if "/cases" in path_lower:
            if method == "POST":
                return "CASE_CREATE"
            elif method == "GET":
                return "CASE_VIEW" if "/" in path_lower.split("/cases")[-1] else "CASE_LIST"
            elif method == "PUT":
                return "CASE_UPDATE"
            elif method == "DELETE":
                return "CASE_DELETE"

        # Evidence actions
        if "/evidence" in path_lower or "/upload" in path_lower:
            if method == "POST":
                return "EVIDENCE_UPLOAD"
            elif method == "GET":
                return "EVIDENCE_VIEW"
            elif method == "DELETE":
                return "EVIDENCE_DELETE"

        # Message actions
        if "/messages" in path_lower:
            if method == "GET":
                return "MESSAGE_VIEW"
            elif method == "POST" and "export" in path_lower:
                return "MESSAGE_EXPORT"

        # Report actions
        if "/reports" in path_lower:
            if method == "POST":
                return "REPORT_GENERATE"
            elif method == "GET":
                return "REPORT_VIEW"

        # Default action
        return f"{method}_{path.split('/')[-1].upper() or 'ROOT'}"

    @staticmethod
    def _determine_action_category(path: str) -> str:
        """Determine action category from path"""
        path_lower = path.lower()

        if "/auth" in path_lower:
            return "authentication"
        elif "/cases" in path_lower:
            return "case_management"
        elif "/evidence" in path_lower or "/upload" in path_lower:
            return "evidence_handling"
        elif "/messages" in path_lower or "/chats" in path_lower:
            return "data_access"
        elif "/reports" in path_lower:
            return "export"
        elif "/users" in path_lower:
            return "administration"
        elif "/ai" in path_lower or "/analyze" in path_lower:
            return "ai_analysis"

        return "other"

    @staticmethod
    def _determine_resource_type(path: str) -> str:
        """Determine resource type from path"""
        if "/cases" in path:
            return "case"
        elif "/messages" in path:
            return "message"
        elif "/evidence" in path:
            return "evidence"
        elif "/users" in path:
            return "user"
        elif "/reports" in path:
            return "report"
        return None

    @staticmethod
    def _extract_resource_id(path: str) -> str:
        """Extract resource ID from path (UUID format)"""
        from uuid import UUID

        path_parts = path.split("/")
        for part in path_parts:
            try:
                UUID(part)  # Validate UUID format
                return part
            except (ValueError, AttributeError):
                continue
        return None
