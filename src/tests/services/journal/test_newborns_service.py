import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import re

from services.journal.newborns_service import NewbornsService
from data_subjects.requests.newborns_request import NewbornFilter, NewbornStatus
from data_subjects.responses.newborns_response import NewbornStatusColor
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO


class TestNewbornsService:
    """Тесты для сервиса новорожденных."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["birthDate"] = "2025-01-01T00:00:00"
            item["addiditonalInformation"] = "С МАМОЙ"

        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = NewbornFilter(
            date_from="2025-01-01",
            date_to="2025-12-31",
            patient_identifier="070210653849",
            department="072",
            status=NewbornStatus.ACTIVE
        )

        result = await NewbornsService.get_data(filter_params)

        assert result.hospital_name == "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау"
        assert isinstance(result.items, list)
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit

    @pytest.mark.asyncio
    async def test_get_data_empty(self, mock_journal_base_service):
        """Проверка получения пустого ответа при отсутствии данных."""
        mock_journal_base_service.return_value = HandlerResultDTO(
            success=False,
            error="No data found",
            status_code=404
        )

        filter_params = NewbornFilter(
            date_from="2025-01-01",
            date_to="2025-12-31"
        )

        result = await NewbornsService.get_data(filter_params)

        assert result.hospital_name == "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау"
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат данных новорожденных."""
        for item in referrals_json_data:
            # Указываем дату рождения - недавнюю дату для новорожденного
            patient_data = item.get("patient", {})
            patient_data["birthDate"] = "2025-01-01T00:00:00"
            item["addiditonalInformation"] = "С МАМОЙ"

        # Создаем фильтр
        filter_params = NewbornFilter(
            date_from="2025-01-01",
            date_to="2025-12-31"
        )

        result = NewbornsService._transform_data(
            {"referralItems": referrals_json_data},
            filter_params
        )

        assert result.hospital_name.startswith("Коммунальное государственное предприятие")
        assert isinstance(result.items, list)

        if result.items:
            item = result.items[0]
            assert hasattr(item, "id")
            assert hasattr(item, "patient")
            assert hasattr(item, "status_color")
            assert hasattr(item, "additional_info")
            assert item.status_color == NewbornStatusColor.GREEN

            assert "mother" in item.additional_info
            assert item.additional_info["mother"] is not None
            assert hasattr(item.additional_info["mother"], "full_name")

            assert "Иванова Мария Петровна" == item.additional_info["mother"].full_name

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["birthDate"] = "2025-01-01T00:00:00"
            item["addiditonalInformation"] = "С МАМОЙ"

        filter_params = NewbornFilter(
            date_from="2025-01-01",
            date_to="2025-12-31",
            patient_identifier="070210653849",
            department="072",
            status=NewbornStatus.ACTIVE
        )

        filtered_items = NewbornsService._apply_filter(
            referrals_json_data,
            filter_params
        )

        for item in filtered_items:
            reg_date = datetime.strptime(item["regDate"].split("T")[0], "%Y-%m-%d")
            assert datetime(2025, 1, 1) <= reg_date <= datetime(2025, 12, 31)

            if filter_params.patient_identifier:
                patient_data = item.get("patient", {})
                patient_iin = patient_data.get("personin", "")
                patient_name = patient_data.get("personFullName", "").lower()
                additional_info = item.get("addiditonalInformation", "").lower()

                assert (filter_params.patient_identifier.lower() in patient_name or
                        filter_params.patient_identifier == patient_iin or
                        filter_params.patient_identifier.lower() in additional_info)

            if filter_params.department != "all":
                department = item.get("bedProfile", {}).get("code", "")
                assert department == filter_params.department

            if filter_params.status == NewbornStatus.ACTIVE:
                assert "outDate" not in item or not item["outDate"]