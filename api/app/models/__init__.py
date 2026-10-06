# Uvoz svih modela registrira ih u Base.metadata.
# autogenerate u Alembicu vidi samo modele koji su ovdje uvezeni.
from app.core.database import Base
from app.models.club import Club
from app.models.competition import Competition
from app.models.lifter import Lifter
from app.models.registration import Registration
from app.models.user import User

__all__ = ["Base", "Club", "Competition", "Lifter", "Registration", "User"]
