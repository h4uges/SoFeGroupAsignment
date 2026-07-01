from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict
from datetime import date

import Constants

class Gender(Enum):
    MALE = "m"
    FEMALE = "w"

@dataclass(frozen=True)
class Person:
    id: int
    first_name: str
    last_name: str
    birth_date: date
    gender: Gender
    klasse_nach_ferien: int
    wish_1: Optional[str]  # Vor- oder Nachname anderer Person (String)
    wish_2: Optional[str]
    bag: Dict[str, str] = field(default_factory=dict)

    @property
    def age(self) -> float:
        delta = Constants.cut_off_date - self.birth_date
        return round(delta.days / 365.25, 2)  # Using 365.25 to account for leap years