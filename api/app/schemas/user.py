from pydantic import BaseModel


class UserResponse(BaseModel):
    # password_hash namjerno nije ovdje: polje kojeg nema u shemi ne može izaći
    id: int
    username: str
    role: str
    club_id: int | None
    is_active: bool

    model_config = {"from_attributes": True}
