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


APPEAL_TYPE_EN_RU = {
    AppealType.STATEMENT: "Заявление",
    AppealType.CLAIM: "Претензия",
    AppealType.COMPLAINT: "Жалоба",
    AppealType.NOTICE: "Уведомление",
    AppealType.LETTER: "Письмо",
    AppealType.PROPOSAL: "Предложение",
    AppealType.ACKNOWLEDGEMENT: "Благодарность",
    AppealType.CONSULTATION: "Консультации по общим вопросам ЖКХ",
}


class AppealStatus(str, Enum):
    NEW = "new"
    RUN = "run"
    PERFORMED = "performed"
    REVOKED = "revoked"


APPEAL_STATUS_EN_RU = {
    AppealStatus.NEW: "Принято",
    AppealStatus.PERFORMED: "Исполнено",
    AppealStatus.RUN: "В работе",
    AppealStatus.REVOKED: "Отозвано",
}


class AppealSource(str, Enum):
    TENANT = "tenant"
    DISPATCHER = "dispatcher"
    GIS = "gis"


APPEAL_SOURCE_EN_RU = {
    AppealSource.TENANT: "Самостоятельно жителем",
    AppealSource.DISPATCHER: "Через диспетчерскую",
    AppealSource.GIS: "Из ГИС",
}
