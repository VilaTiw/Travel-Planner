from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class PlaceBase(BaseModel):
    external_id: str
    notes: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None

class PlaceResponse(PlaceBase):
    id: int
    project_id: int
    is_visited: bool

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    places: Optional[List[str]] = Field(default=None, max_length=10, description="List of external IDs")

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectResponse(ProjectBase):
    id: int
    is_completed: bool
    places: List[PlaceResponse] = []

    class Config:
        from_attributes = True