from pydantic import BaseModel
from gridplayer.models.grid_state import GridState

class Snapshot(BaseModel):
    grid_state: GridState  # example field

    class Config:
        arbitrary_types_allowed = True
