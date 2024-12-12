from enum import Enum


class AppealType(str, Enum):
    STATEMENT = "statement"
    CLAIM = "claim"
    COMPLAINT = "complaint"
    NOTICE = "notice"
    LETTER = "letter"
    PROPOSAL = "proposal"
    ACKNOWLEDGEMENT = "acknowledgement"
    CONSULTATION = "consultation"


class AppealStatus(str, Enum):
    ACCEPTED = "accepted"
    PERFORMED = "performed"
    RUN = "run"
    RECALLED = "recalled"


class AppealSource(str, Enum):
    TENANT = "tenant"
    DISPATCHER = "dispatcher"
    GIS = "gis"
