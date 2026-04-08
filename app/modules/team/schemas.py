from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class TeamMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    document_number: str
    name: str
    email: str
    position_name: Optional[str]
    area: Optional[str]
    subarea: Optional[str]
    is_active: bool


class TeamMembersResponse(BaseModel):
    members: List[TeamMemberResponse]
