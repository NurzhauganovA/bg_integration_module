from enum import Enum


class ServiceType(str, Enum):
    """Типы медицинских сервисов."""

    HOSPITAL = "hospital"  # Стационар
    AMBULANCE = "ambulance"  # Скорая помощь
    CLINIC = "clinic"  # Поликлиника
    MATERNITY = "maternity"  # Роддом
    NEWBORN = "newborn"  # Новорожденные
    DECEASED = "deceased"  # Умершие пациенты
    REJECTION = "rejection"  # Отказы от госпитализации


class FilterType(str, Enum):
    """Типы фильтрации данных."""

    ALL_RECORDS = "all_records"
    ACTIVE_ONLY = "active_only"
    COMPLETED_ONLY = "completed_only"
    DISCHARGED_ONLY = "discharged_only"
    WITH_REFUSAL = "with_refusal"
    FEMALE_ONLY = "female_only"
    MALE_ONLY = "male_only"
    RECENT_BIRTHS = "recent_births"


class SortDirection(str, Enum):
    """Направления сортировки."""

    ASC = "asc"
    DESC = "desc"


class SortField(str, Enum):
    """Поля для сортировки."""

    DATE = "date"
    PATIENT_NAME = "patient_name"
    DOCTOR_NAME = "doctor_name"
    DEPARTMENT = "department"
    STATUS = "status"


class SortType(str, Enum):
    """Типы сортировки для всех сервисов."""

    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    PATIENT_NAME_ASC = "patient_name_asc"
    PATIENT_NAME_DESC = "patient_name_desc"
    DOCTOR_NAME_ASC = "doctor_name_asc"
    DOCTOR_NAME_DESC = "doctor_name_desc"


class DepartmentCode(str, Enum):
    """Коды отделений."""

    ALL = "all"
    THERAPY = "072"


class PatientStatusCode(str, Enum):
    """Коды статусов пациентов."""

    ACTIVE = "active"
    DISCHARGED = "discharged"
    TRANSFERRED = "transferred"
    DECEASED = "deceased"
    REFUSED = "refused"
    WAITING = "waiting"
    HOSPITALIZED = "hospitalized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SCHEDULED = "scheduled"


class GenderCode(str, Enum):
    """Коды пола пациентов."""

    MALE = "100"
    FEMALE = "200"
    UNKNOWN = "000"


class AgeGroup(str, Enum):
    """Возрастные группы."""

    NEWBORN = "newborn"  # 0-28 дней
    INFANT = "infant"  # 1-12 месяцев
    CHILD = "child"  # 1-18 лет
    ADULT = "adult"  # 18-65 лет
    ELDERLY = "elderly"  # 65+ лет


class StatusColor(str, Enum):
    """Цвета статусов для UI."""

    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    RED = "red"
    GRAY = "gray"


class TreatmentOutcome(str, Enum):
    """Исходы лечения."""

    IMPROVEMENT = "Улучшение"
    RECOVERY = "Выздоровление"
    DEATH = "Смерть"
    TRANSFER = "Перевод"
    DISCHARGE = "Выписка"


class DischargeOutcome(str, Enum):
    """Исходы выписки."""

    DISCHARGED = "Выписан"
    DIED = "Умер"
    TRANSFERRED = "Переведен"
    LEFT_VOLUNTARILY = "Ушел добровольно"


class RefusalStatus(str, Enum):
    """Статусы отказов."""

    TRUE = "true"
    FALSE = "false"


class ConfirmStatus(str, Enum):
    """Статусы подтверждения."""

    TRUE = "true"
    FALSE = "false"


class ContactInfo(str, Enum):
    """Контактная информация по умолчанию."""

    DEFAULT_PHONE = "+77076098760"
    DEFAULT_ADDRESS = "г. Алматы мкр. Алмагуль 3 кв. 1"
    DEFAULT_EXECUTOR = "Нуржауганов Анварбек Кайыржанович"


class MedicalPersonnel(str, Enum):
    """Медицинский персонал по умолчанию."""

    DEFAULT_DOCTOR = "Александр Васильевич Пупкин"
    DEFAULT_SPECIALIST = "Александр Васильевич Пупкин"
    DEFAULT_SPECIALIZATION = "Терапевт"
    DEFAULT_DEPARTMENT_NAME = "Терапевтическое отделение"


class DeathMarker(str, Enum):
    """Маркеры смерти."""

    DEATH = "смерть"
    DIED = "умер"
    FATAL = "летальный"
    DECEASED = "скончался"


class PhonePattern(str, Enum):
    """Паттерны для поиска телефонов."""

    PHONE_REGEX = r'\+?[7][\d\s-]{10,}'
    MOTHER_REGEX = r'мать:?\s*([\w\s]+)'


class DefaultValues(str, Enum):
    """Значения по умолчанию."""

    DEPARTMENT_PREFIX = "№"
    DEPARTMENT_NUMBER = "072"
    MOTHER_NAME = "Мать"
    GENDER_UNKNOWN = "Неизвестно"
    REFUSAL_REASON = "Отказ от госпитализации"