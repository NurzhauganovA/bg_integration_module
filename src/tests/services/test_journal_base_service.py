import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.requests.base_request import BaseFilter
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO


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
            date_from="2025-01-01",
            date_to="2025-12-31",
            patient_identifier="070210653849"
        )

        result = await TestServiceImpl.get_data(filter_params)

        assert result["transformed"] is True
        assert result["items"] == referrals_json_data
        assert result["page"] == filter_params.page
        assert result["limit"] == filter_params.limit

        called_params = mock_bg_referrals_handler.handle.call_args[0][0]
        assert "patientIINOrFIO" in called_params
        assert called_params["patientIINOrFIO"] == "070210653849"
        assert "dateFrom" in called_params
        assert called_params["dateFrom"] == "2025-01-01"
        assert "dateTo" in called_params
        assert called_params["dateTo"] == "2025-12-31"

    @pytest.mark.asyncio
    async def test_get_data_failure(self, mock_bg_referrals_handler):
        """Проверка получения пустого ответа при ошибке."""
        mock_bg_referrals_handler.handle.return_value = HandlerResultDTO(
            success=False,
            error="Error occurred",
            status_code=500
        )

        filter_params = BaseFilter(
            date_from="2025-01-01",
            date_to="2025-12-31"
        )

        result = await TestServiceImpl.get_data(filter_params)

        assert result["transformed"] is True
        assert result["items"] == []
        assert result["page"] == filter_params.page
        assert result["limit"] == filter_params.limit

    def test_filter_to_bg_params(self):
        """Проверка преобразования параметров фильтрации в параметры запроса к БГ."""
        filter_params = BaseFilter(
            date_from="2025-01-01",
            date_to="2025-12-31",
            patient_identifier="070210653849",
            department="072",
            sort_by="date_desc",
            page=2,
            limit=20
        )

        bg_params = TestServiceImpl._filter_to_bg_params(filter_params)

        assert "patientIINOrFIO" in bg_params
        assert bg_params["patientIINOrFIO"] == "070210653849"
        assert "dateFrom" in bg_params
        assert bg_params["dateFrom"] == "2025-01-01"
        assert "dateTo" in bg_params
        assert bg_params["dateTo"] == "2025-12-31"

        assert "department" not in bg_params
        assert "sort_by" not in bg_params
        assert "page" not in bg_params
        assert "limit" not in bg_params

    def test_filter_to_bg_params_empty(self):
        """Проверка преобразования пустых параметров фильтрации."""
        filter_params = BaseFilter(
            date_from="2025-01-01",
            date_to="2025-12-31"
        )

        bg_params = TestServiceImpl._filter_to_bg_params(filter_params)

        assert "patientIINOrFIO" not in bg_params
        assert "dateFrom" in bg_params
        assert bg_params["dateFrom"] == "2025-01-01"
        assert "dateTo" in bg_params
        assert bg_params["dateTo"] == "2025-12-31"