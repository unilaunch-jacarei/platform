import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length = 1, max_length = 255)
    description: str | None = None
    
class TaskUpdate(BaseModel):
    title: str | None = Field(default = None, min_length = 1, max_length = 255)
    description: str | None = None
    completed: bool | None = None

class TaskRead(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    completed: bool
    user_id: uuid.UUID
    created_at: datetime
    update_at: datetime
    
    model_config  = ConfigDict(from_attributes = True)