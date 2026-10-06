import datetime as dt

from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from app.core.phases import Phase, get_competition_phase
from app.schemas.common import reject_null


class CompetitionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    date: dt.date
    # AwareDatetime traži oznaku zone, npr. 2027-02-14T23:59:00+01:00. Baza
    # vrijednost bez zone ne bi odbila, nego bi je tumačila u svojoj zoni
    prelim_deadline: AwareDatetime
    final_deadline: AwareDatetime

    @field_validator("final_deadline")
    @classmethod
    def final_after_prelim(cls, v, info):
        prelim = info.data.get("prelim_deadline")
        if prelim and v <= prelim:
            raise ValueError("final_deadline mora biti nakon prelim_deadline")
        return v

    @model_validator(mode="after")
    def deadlines_before_competition(self):
        if self.final_deadline.date() >= self.date:
            raise ValueError("Rokovi moraju isteći prije dana natjecanja")
        return self


class CompetitionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    location: str | None = Field(default=None, min_length=1, max_length=200)
    date: dt.date | None = None
    prelim_deadline: AwareDatetime | None = None
    final_deadline: AwareDatetime | None = None

    _not_null = field_validator(
        "name", "location", "date", "prelim_deadline", "final_deadline", mode="before"
    )(reject_null)


class CompetitionResponse(BaseModel):
    id: int
    name: str
    location: str
    date: dt.date
    prelim_deadline: dt.datetime
    final_deadline: dt.datetime

    model_config = {"from_attributes": True}

    # Izvedena vrijednost: frontend iz nje zna koje radnje ponuditi,
    # a pravila svejedno provodi backend
    @computed_field
    @property
    def phase(self) -> Phase:
        return get_competition_phase(self)
