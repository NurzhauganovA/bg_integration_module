import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.journal.deceased_patients_service import DeceasedPatientsService
from data_subjects.requests.deceased_patients_request import DeceasedFilter
from data_subjects.responses.deceased_patients_response import DeceasedStatusColor
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO


class TestDeceasedPatientsService:
    """Тесты для сервиса умерших пациентов."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        for item in referrals_json_data:
            item["addiditonalInformation"] = "смерть пациента"
            item["outDate"] = "2025-01-10T15:30:00"

        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        # Создаем фильтр
        filter_params = DeceasedFilter(
            date_from="2023-01-01",
            date_to="2023-01-31",
            patient_identifier="070210653849",
            department="072"
        )

        # Вызываем метод получения данных
        result = await DeceasedPatientsService.get_data(filter_params)

        # Проверяем результат
        assert result.hospital_name == "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау"
        assert isinstance(result.items, list)
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit

        # Проверяем, что все элементы имеют правильный статус цвета
        for item in result.items:
            assert item.status_color == DeceasedStatusColor.RED

    @pytest.mark.asyncio
    async def test_get_data_empty(self, mock_journal_base_service):
        """Проверка получения пустого ответа при отсутствии данных."""
        # Настраиваем мок для _get_bg_data
        mock_journal_base_service.return_value = HandlerResultDTO(
            success=False,
            error="No data found",
            status_code=404
        )

        # Создаем фильтр
        filter_params = DeceasedFilter(
            date_from="2023-01-01",
            date_to="2023-01-31"
        )

        # Вызываем метод получения данных
        result = await DeceasedPatientsService.get_data(filter_params)

        # Проверяем результат
        assert result.hospital_name == "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау"
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат умерших пациентов."""
        # Добавляем признаки смерти для тестовых данных
        for item in referrals_json_data:
            item["addiditonalInformation"] = "смерть пациента"
            item["outDate"] = "2020-01-10T15:30:00"

        # Создаем фильтр
        filter_params = DeceasedFilter(
            date_from="2020-01-01",
            date_to="2020-01-31"
        )

        # Вызываем метод преобразования данных
        result = DeceasedPatientsService._transform_data(
            {"referralItems": referrals_json_data},
            filter_params
        )

        # Проверяем результат
        assert result.hospital_name.startswith("Коммунальное государственное предприятие")
        assert isinstance(result.items, list)

        # Если есть элементы, проверяем первый
        if result.items:
            item = result.items[0]
            assert hasattr(item, "id")
            assert hasattr(item, "patient")
            assert hasattr(item, "status_color")
            assert hasattr(item, "additional_info")
            assert item.status_color == DeceasedStatusColor.RED  # Для умерших пациентов

            # Проверяем, что в дополнительной информации есть данные о лечении и исходе
            assert "treatment_outcome" in item.additional_info
            assert "discharge_outcome" in item.additional_info
            assert item.additional_info["treatment_outcome"] == "Смерть"
            assert item.additional_info["discharge_outcome"] == "Умер"

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        # Добавляем признаки смерти для тестовых данных
        for item in referrals_json_data:
            item["addiditonalInformation"] = "смерть пациента"
            item["outDate"] = "2025-01-10T00:00:00"

        # Создаем фильтр
        filter_params = DeceasedFilter(
            date_from="2025-01-01",
            date_to="2025-12-31",
            patient_identifier="070210653849",
            department="072"
        )

        filtered_items = DeceasedPatientsService._apply_filter(
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
                assert (filter_params.patient_identifier.lower() in patient_name or
                        filter_params.patient_identifier == patient_iin)

            if filter_params.department != "all":
                department = item.get("bedProfile", {}).get("code", "")
                assert department == filter_params.department

            assert "смерть" in item.get("addiditonalInformation", "").lower() or item.get("outDate")

    def test_format_period(self):
        """Проверка форматирования периода госпитализации."""
        period = DeceasedPatientsService._format_period(
            "2025-01-01T00:00:00",
            "2025-01-10T00:00:00"
        )
        assert period == "С 01.01.2025 – По 10.01.2025"

        period = DeceasedPatientsService._format_period(
            "2025-01-01T00:00:00",
            None
        )
        assert period == "С 01.01.2025"

        period = DeceasedPatientsService._format_period(None, None)
        assert period == ""

    def test_calculate_age(self):
        """Проверка расчета возраста на основе даты рождения."""
        with patch('services.journal.deceased_patients_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 1)
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            age = DeceasedPatientsService._calculate_age("2000-01-01T00:00:00")
            assert age == 25

            age = DeceasedPatientsService._calculate_age(None)
            assert age == 0

            age = DeceasedPatientsService._calculate_age("invalid-date")
            assert age == 0