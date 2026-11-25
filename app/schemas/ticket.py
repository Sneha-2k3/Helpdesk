
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator
)


# --------------------------------------------------
# ENUM DEFINITIONS
# --------------------------------------------------

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(str, Enum):
    TECHNICAL = "technical"
    ACCOUNT = "account"
    BILLING = "billing"
    GENERAL = "general"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# --------------------------------------------------
# COMMON TICKET INPUT VALIDATION
# --------------------------------------------------

class TicketFields(BaseModel):

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=5,
        max_length=100,
        description="Short title describing the issue"
    )

    description: str = Field(
        min_length=10,
        max_length=1000,
        description="Detailed description of the issue"
    )

    @field_validator("title", "description")
    @classmethod
    def remove_extra_whitespace(cls, value):

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Field cannot contain only spaces")

        return cleaned_value

    @model_validator(mode="after")
    def validate_ticket_content(self):

        if self.title.lower() == self.description.lower():
            raise ValueError(
                "Title and description cannot be identical"
            )

        return self


# --------------------------------------------------
# CREATE TICKET SCHEMA
# --------------------------------------------------

class TicketCreate(TicketFields):
    pass


# --------------------------------------------------
# REPLACE TICKET SCHEMA
# --------------------------------------------------

class TicketReplace(TicketFields):
    pass


# --------------------------------------------------
# UPDATE STATUS SCHEMA
# --------------------------------------------------

class TicketStatusUpdate(BaseModel):

    model_config = ConfigDict(extra="forbid")

    status: TicketStatus


# --------------------------------------------------
# RESPONSE SCHEMA
# --------------------------------------------------

class TicketResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
