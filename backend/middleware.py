from fastapi import Request
from fastapi.responses import JSONResponse
from .utils import MAINTENANCE_MODE

# Routes toujours accessibles en maintenance
ALLOWED_IN_MAINTENANCE = {
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/me",
    "/api/admin/maintenance",
    "/docs",
    "/openapi.json",
}


async def maintenance_middleware(request: Request, call_next):
    """
    Bloque toutes les routes /api/* sauf celles de la whitelist
    quand MAINTENANCE_MODE=true OU que le flag DB est actif.
    """
    # Lecture dynamique depuis DB (prioritaire sur la var d'env)
    try:
        from .database import db
        flag = await db.config.find_one({"key": "maintenance_mode"}, {"_id": 0})
        is_maintenance = flag.get("value", False) if flag else MAINTENANCE_MODE
    except Exception:
        is_maintenance = MAINTENANCE_MODE

    if is_maintenance:
        path = request.url.path
        if path.startswith("/api") and path not in ALLOWED_IN_MAINTENANCE:
            return JSONResponse(
                status_code=503,
                content={"detail": "Le site est en maintenance. Revenez bientôt !"},
                headers={"Retry-After": "300"},
            )

    return await call_next(request)
