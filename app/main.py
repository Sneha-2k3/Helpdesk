
from fastapi import FastAPI, Query
from app.api.routes.tickets import router as tickets_router
from app.api.routes.auth import router as auth_router

from app.database.base import Base
from app.database.connection import engine

# Import model so SQLAlchemy registers its table
from app.models.ticket import TicketModel
from app.models.user import UserModel
from app.core.logging_config import logger
import time


# Create database tables
Base.metadata.create_all(bind=engine)

# Create a FastAPI application instance
app = FastAPI(
    title="AI Helpdesk API",
    description="Backend API for managing IT support tickets",
    version="1.0.0"
)


@app.middleware("http")
async def log_requests(request, call_next):

    start_time = time.time()

    try:
        response = await call_next(request)

        duration = (time.time() - start_time) * 1000

        logger.info(
            "method=%s path=%s status_code=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration
        )

        return response

    except Exception:
        logger.exception(
            "Unhandled request error: method=%s path=%s",
            request.method,
            request.url.path
        )
        raise


#Register Ticket Router
app.include_router(tickets_router)
app.include_router(auth_router)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to AI Helpdesk API",
        "application": "AI Helpdesk Ticket Management System",
        "version": "1.0.0"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Application is running successfully"
    }


# Application information endpoint
@app.get("/about")
def about():
    return {
        "application": "AI Helpdesk API",
        "description": "An AI-powered IT support ticket management system",
        "framework": "FastAPI"
    }

@app.get("/tickets")
def get_tickets(
    status: str | None = None,
    limit: int = Query(default=10, ge=1, le=100)
):
    return {
        "status_filter": status,
        "limit": limit,
        "message": "Fetching tickets"
    }
@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    return {
        "ticket_id": ticket_id,
        "message": f"Fetching ticket with ID {ticket_id}"
    }