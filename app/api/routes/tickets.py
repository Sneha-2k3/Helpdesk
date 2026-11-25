
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Query,
    Depends
)

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.connection import get_db
from app.models.ticket import TicketModel
from app.models.user import UserModel

from app.api.dependencies import get_current_user

from app.schemas.ticket import (
    TicketCreate,
    TicketReplace,
    TicketStatusUpdate,
    TicketResponse,
    TicketStatus
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


# --------------------------------------------------
# CREATE TICKET - POST
# --------------------------------------------------

@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    new_ticket = TicketModel(
        title=ticket.title,
        description=ticket.description,
        category="general",
        priority="medium",
        status="open"
    )

    db.add(new_ticket)

    db.commit()

    db.refresh(new_ticket)

    return new_ticket


# --------------------------------------------------
# GET ALL TICKETS - GET
# --------------------------------------------------

@router.get("/", response_model=list[TicketResponse])
def get_all_tickets(
    status_filter: TicketStatus | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    statement = select(TicketModel)

    if status_filter is not None:
        statement = statement.where(
            TicketModel.status == status_filter.value
        )

    statement = (
        statement
        .order_by(TicketModel.id)
        .offset(offset)
        .limit(limit)
    )

    result = db.execute(statement)

    tickets = result.scalars().all()

    return tickets


# --------------------------------------------------
# GET SINGLE TICKET - GET
# --------------------------------------------------

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    ticket = db.get(TicketModel, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


# --------------------------------------------------
# REPLACE TICKET DETAILS - PUT
# --------------------------------------------------

@router.put("/{ticket_id}", response_model=TicketResponse)
def replace_ticket(
    ticket_id: int,
    ticket_data: TicketReplace,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    ticket = db.get(TicketModel, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    ticket.title = ticket_data.title
    ticket.description = ticket_data.description

    db.commit()

    db.refresh(ticket)

    return ticket


# --------------------------------------------------
# UPDATE TICKET STATUS - PATCH
# --------------------------------------------------

@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse
)
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    ticket = db.get(TicketModel, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    ticket.status = status_data.status.value

    db.commit()

    db.refresh(ticket)

    return ticket


# --------------------------------------------------
# DELETE TICKET - DELETE
# --------------------------------------------------

@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    ticket = db.get(TicketModel, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    db.delete(ticket)

    db.commit()

    return None
