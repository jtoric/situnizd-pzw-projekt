from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.competition import Competition


class Phase(str, Enum):
    OPEN = "open"  # prije nominacijskog roka
    PRELIM_PASSED = "prelim_passed"  # između nominacijskog i konačnog roka
    CLOSED = "closed"  # nakon konačnog roka


def get_competition_phase(competition: "Competition") -> Phase:
    """Faza se ne pohranjuje nego računa pri svakom zahtjevu, pa ne zaostaje
    za vremenom. Funkcija ne dira bazu i ne odlučuje što je dopušteno."""
    # Usporedba u UTC-u: rokovi su timestamptz, pa nose zonu
    now = datetime.now(timezone.utc)
    prelim = competition.prelim_deadline
    final = competition.final_deadline

    if now < prelim:
        return Phase.OPEN
    if now < final:
        return Phase.PRELIM_PASSED
    return Phase.CLOSED
