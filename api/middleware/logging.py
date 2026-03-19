import time
from urllib.parse import urlparse
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseCall
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

# Corrected import for Docker context
from database import log_request_to_db


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    This middleware logs incoming request data to the database.

    It captures request details, performance metrics, and custom headers
    for analytics and funnel tracking. The database write is performed
    in a non-blocking background task to ensure the response is not delayed.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseCall) -> Response:
        start_time = time.time()

        response = await call_next(request)

        log_data = {
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "recruiter_domain": self._extract_domain(request),
            "user_agent": request.headers.get("user-agent", ""),
            "client_ip": request.client.host if request.client else "",
            "status_code": response.status_code,
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "session_id": request.headers.get("x-session-id"),
            "search_campaign": request.headers.get("x-search-campaign"),
            "traffic_source": request.headers.get("x-traffic-source"),
            "funnel_stage": request.headers.get("x-funnel-stage"),
            "device_type": request.headers.get("x-device-type"),
            "geo_region": request.headers.get("x-geo-region"),
        }

        response.background = BackgroundTask(log_request_to_db, log_data)
        return response

    def _extract_domain(self, request: Request) -> str:
        """
        Extracts the domain from the Referer header.
        Returns "direct" if the header is not present.
        """
        referer = request.headers.get("referer", "")
        if referer:
            try:
                return urlparse(referer).netloc or "direct"
            except Exception:
                return "parsing_error"
        return "direct"
