from pydantic import BaseModel

class WindowState(BaseModel):
    x: int = 0
    y: int = 0
    width: int = 800
    height: int = 600
    maximized: bool = False
    fullscreen: bool = False
