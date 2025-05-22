"""Константы для тестов."""

# Тестовые данные пациентов
TEST_PATIENT_IIN = "070210653849"
TEST_PATIENT_NAME = "СЛОБОДЕНЮК АЙЖАН"
TEST_DEPARTMENT_CODE = "072"

# Тестовые даты
TEST_DATE_FROM = "2025-01-01"
TEST_DATE_TO = "2025-12-31"
TEST_REG_DATE = "2025-01-01T00:00:00"
TEST_BIRTH_DATE = "2025-01-01T00:00:00"
TEST_OUT_DATE = "2025-12-31T00:00:00"

# Название больницы
HOSPITAL_NAME = "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау"

# Статусы и коды
FEMALE_SEX_CODE = "200"
MALE_SEX_CODE = "100"
UNKNOWN_SEX_CODE = "000"

# Возрастные границы
NEWBORN_MAX_AGE_DAYS = 28
INFANT_MAX_AGE_MONTHS = 12
CHILD_MAX_AGE_YEARS = 18
ELDERLY_MIN_AGE_YEARS = 65

# Сообщения об ошибках
ERROR_NO_DATA_FOUND = "No data found"
ERROR_MOCK_DATA = "Mock data error"

# Текстовые маркеры
DEATH_MARKER = "смерть пациента"
MOTHER_INFO_MARKER = "С МАМОЙ"
REFUSAL_MARKER = "true"

# Пагинация
DEFAULT_PAGE_SIZE = 10
DEFAULT_PAGE_NUMBER = 1
TEST_PAGE_SIZE = 20
TEST_PAGE_NUMBER = 2
LARGE_DATASET_SIZE = 25

# HTTP статусы
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_INTERNAL_SERVER_ERROR = 500