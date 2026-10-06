from datetime import date, datetime, timezone

from freezegun import freeze_time

from app.core.phases import Phase, get_competition_phase
from app.models import Competition

# Bez baze: funkcija samo uspoređuje trenutno vrijeme s rokovima
COMPETITION = Competition(
    name="Test Kup",
    location="Zadar",
    date=date(2026, 5, 16),
    prelim_deadline=datetime(2026, 4, 15, tzinfo=timezone.utc),
    final_deadline=datetime(2026, 5, 1, tzinfo=timezone.utc),
)


@freeze_time("2026-04-14 23:59:59")
def test_open_just_before_prelim_deadline():
    assert get_competition_phase(COMPETITION) == Phase.OPEN


@freeze_time("2026-04-15 00:00:00")
def test_prelim_passed_exactly_at_prelim_deadline():
    assert get_competition_phase(COMPETITION) == Phase.PRELIM_PASSED


@freeze_time("2026-04-30 23:59:59")
def test_prelim_passed_just_before_final_deadline():
    assert get_competition_phase(COMPETITION) == Phase.PRELIM_PASSED


@freeze_time("2026-05-01 00:00:00")
def test_closed_exactly_at_final_deadline():
    assert get_competition_phase(COMPETITION) == Phase.CLOSED


@freeze_time("2026-04-14 23:30:00+00:00")
def test_deadline_is_compared_in_utc():
    # 23:30 UTC je 01:30 sljedećeg dana po srednjoeuropskom ljetnom vremenu,
    # ali rok je trenutak: do njega je još pola sata
    assert get_competition_phase(COMPETITION) == Phase.OPEN
