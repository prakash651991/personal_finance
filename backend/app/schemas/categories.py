from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None


class CategoryOut(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    is_system: bool = False
    user_id: Optional[str] = None
