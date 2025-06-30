import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.requests.base_request import BaseFilter
from data_subjects.enums.service_enums import PhonePattern, ContactInfo, DefaultValues
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from tests.constants import *


class TestServiceImpl(JournalBaseService):
    """Реализация JournalBaseService для тестирования."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: BaseFilter) -> Dict:
        """Тестовая реализация трансформации данных."""
        return {
            "transformed": True,
            "items": data.get("referralItems", []),
            "page": filter_params.page,
            "limit": filter_params.limit
        }

    @classmethod
    def _get_empty_response(cls, filter_params: BaseFilter) -> Dict:
        """Тестовая реализация получения пустого ответа."""
        return {
            "transformed": True,
            "items": [],
            "page": filter_params.page,
            "limit": filter_params.limit
        }


class TestJournalBaseService:
    """Тесты для базового сервиса журнала."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_bg_referrals_handler, referrals_json_data):
        """Проверка успешного получения данных."""
        mock_bg_referrals_handler.handle.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = BaseFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN
        )

        result = await TestServiceImpl.get_data(filter_params)

        assert result["transformed"] is True
        assert result["items"] == referrals_json_data
        assert result["page"] == filter_params.page
        assert result["limit"] == filter_params.limit

        called_params = mock_bg_referrals_handler.handle.call_args[0][0]
        assert "patientIINOrFIO" in called_params
        assert called_params["patientIINOrFIO"] == TEST_PATIENT_IIN
        assert "dateFrom" in called_params
        assert called_params["dateFrom"] == TEST_DATE_FROM
        assert "dateTo" in called_params
        assert called_params["dateTo"] == TEST_DATE_TO

    @pytest.mark.asyncio
    async def test_get_data_failure(self, mock_bg_referrals_handler):
        """Проверка получения пустого ответа при ошибке."""
        mock_bg_referrals_handler.handle.return_value = HandlerResultDTO(
            success=False,
            error=ERROR_NO_DATA_FOUND,
            status_code=HTTP_INTERNAL_SERVER_ERROR
        )

        filter_params = BaseFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = await TestServiceImpl.get_data(filter_params)

        assert result["transformed"] is True
        assert result["items"] == []
        assert result["page"] == filter_params.page
        assert result["limit"] == filter_params.limit

    def test_filter_to_bg_params(self):
        """Проверка преобразования параметров фильтрации в параметры запроса к БГ."""
        filter_params = BaseFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            sort_by="date_desc",
            page=TEST_PAGE_NUMBER,
            limit=TEST_PAGE_SIZE
        )

        bg_params = TestServiceImpl._filter_to_bg_params(filter_params)

        assert "patientIINOrFIO" in bg_params
        assert bg_params["patientIINOrFIO"] == TEST_PATIENT_IIN
        assert "dateFrom" in bg_params
        assert bg_params["dateFrom"] == TEST_DATE_FROM
        assert "dateTo" in bg_params
        assert bg_params["dateTo"] == TEST_DATE_TO

        assert "department" not in bg_params
        assert "sort_by" not in bg_params
        assert "page" not in bg_params
        assert "limit" not in bg_params

    def test_filter_to_bg_params_empty(self):
        """Проверка преобразования пустых параметров фильтрации."""
        filter_params = BaseFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        bg_params = TestServiceImpl._filter_to_bg_params(filter_params)

        assert "patientIINOrFIO" not in bg_params
        assert "dateFrom" in bg_params
        assert bg_params["dateFrom"] == TEST_DATE_FROM
        assert "dateTo" in bg_params
        assert bg_params["dateTo"] == TEST_DATE_TO

    def test_is_date_in_range(self):
        """Проверка входа даты в диапазон."""
        from datetime import datetime

        date_from = datetime.strptime(TEST_DATE_FROM, "%Y-%m-%d")
        date_to = datetime.strptime(TEST_DATE_TO, "%Y-%m-%d")

        assert TestServiceImpl._is_date_in_range(TEST_REG_DATE, date_from, date_to)
        assert not TestServiceImpl._is_date_in_range("2025-01-01T00:00:00", date_from, date_to)
        assert not TestServiceImpl._is_date_in_range("", date_from, date_to)
        assert not TestServiceImpl._is_date_in_range("invalid-date", date_from, date_to)

    def test_is_patient_match(self):
        """Проверка соответствия пациента фильтру."""
        item = {
            "patient": {
                "personin": TEST_PATIENT_IIN,
                "personFullName": TEST_PATIENT_NAME
            }
        }

        assert TestServiceImpl._is_patient_match(item, TEST_PATIENT_IIN)
        assert TestServiceImpl._is_patient_match(item, "СЛОБОДЕНЮК")
        assert TestServiceImpl._is_patient_match(item, "")
        assert not TestServiceImpl._is_patient_match(item, "НЕСУЩЕСТВУЮЩИЙ")

    def test_is_department_match(self):
        """Проверка соответствия отделения фильтру."""
        item = {
            "bedProfile": {
                "code": TEST_DEPARTMENT_CODE
            }
        }

        assert TestServiceImpl._is_department_match(item, TEST_DEPARTMENT_CODE)
        assert TestServiceImpl._is_department_match(item, "all")
        assert TestServiceImpl._is_department_match(item, "")
        assert not TestServiceImpl._is_department_match(item, "999")

    def test_extract_phone_number(self):
        """Проверка извлечения номера телефона."""
        additional_info_with_phone = "Контакт: +77076098760"
        additional_info_without_phone = "Без телефона"

        phone = TestServiceImpl._extract_phone_number(additional_info_with_phone)
        assert phone == "+77076098760"

        phone = TestServiceImpl._extract_phone_number(additional_info_without_phone)
        assert phone == ContactInfo.DEFAULT_PHONE.value

        phone = TestServiceImpl._extract_phone_number("")
        assert phone == ContactInfo.DEFAULT_PHONE.value

    def test_format_department(self):
        """Проверка форматирования номера отделения."""
        formatted = TestServiceImpl._format_department(TEST_DEPARTMENT_CODE)
        assert formatted == f"№{TEST_DEPARTMENT_CODE}"

        formatted = TestServiceImpl._format_department("")
        assert formatted == f"№{DefaultValues.DEPARTMENT_NUMBER.value}"

    def test_format_diagnosis(self):
        """Проверка форматирования диагноза."""
        sick_data = {
            "code": "G80.1",
            "name": "Спастическая диплегия"
        }

        diagnosis = TestServiceImpl._format_diagnosis(sick_data)
        assert diagnosis == "G80.1 Спастическая диплегия"

        diagnosis = TestServiceImpl._format_diagnosis({})
        assert diagnosis == ""

    def test_format_period(self):
        """Проверка форматирования периода госпитализации."""
        period = TestServiceImpl._format_period(
            "2025-01-01T00:00:00",
            "2025-01-10T00:00:00"
        )
        assert period == "С 01.01.2025 – По 10.01.2025"

        period = TestServiceImpl._format_period(
            "2025-01-01T00:00:00",
            None
        )
        assert period == "С 01.01.2025"

        period = TestServiceImpl._format_period(None, None)
        assert period == ""

    def test_calculate_age(self):
        """Проверка расчета возраста."""
        with patch('services.journal_base_service.datetime') as mock_datetime:
            from datetime import datetime
            mock_datetime.now.return_value = datetime(2025, 1, 1)
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            age = TestServiceImpl._calculate_age("2000-01-01T00:00:00")
            assert age == 25

            age = TestServiceImpl._calculate_age(None)
            assert age == 0

            age = TestServiceImpl._calculate_age("invalid-date")
            assert age == 0

    def test_apply_sort(self):
        """Проверка применения сортировки."""
        from unittest.mock import MagicMock

        mock_item1 = MagicMock()
        mock_item1.receipt_date = "2025-01-01"
        mock_item1.patient.full_name = "Иванов Иван"

        mock_item2 = MagicMock()
        mock_item2.receipt_date = "2025-01-02"
        mock_item2.patient.full_name = "Петров Петр"

        items = [mock_item2, mock_item1]

        sorted_items = TestServiceImpl._apply_sort(items, "date_asc")
        assert sorted_items[0] == mock_item1

        sorted_items = TestServiceImpl._apply_sort(items, "date_desc")
        assert sorted_items[0] == mock_item2

    def test_apply_pagination(self):
        """Проверка применения пагинации."""
        items = list(range(LARGE_DATASET_SIZE))

        paginated_items, total_pages = TestServiceImpl._apply_pagination(
            items, DEFAULT_PAGE_NUMBER, DEFAULT_PAGE_SIZE
        )

        assert len(paginated_items) == DEFAULT_PAGE_SIZE
        assert total_pages == 3
        assert paginated_items == list(range(DEFAULT_PAGE_SIZE))

        paginated_items, total_pages = TestServiceImpl._apply_pagination(
            items, 3, DEFAULT_PAGE_SIZE
        )

        assert len(paginated_items) == 5
        assert paginated_items == list(range(20, 25))