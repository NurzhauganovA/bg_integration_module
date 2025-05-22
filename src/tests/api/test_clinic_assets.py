import pytest
from unittest.mock import AsyncMock

from data_subjects.responses.clinic_assets_response import ClinicResponse
from data_subjects.requests.clinic_assets_request import ClinicFilter, ClinicStatus


class TestClinicAssetsAPI:
    """Тесты для API активов поликлиники."""

    @pytest.mark.asyncio
    async def test_get_clinic_assets_success(self, client, mock_clinic_assets_service):
        """Проверка успешного получения активов поликлиники."""
        response_template = {
            "hospital_name": "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
            "items": [],
            "total": 0,
            "page": 1,
            "limit": 10,
            "total_pages": 0
        }

        mock_clinic_assets_service.get_data.return_value = ClinicResponse(**response_template)

        response = client.get(
            "/api/journal/clinic-assets",
            params={
                "date_from": "2025-01-01",
                "date_to": "2025-12-31"
            }
        )

        assert response.status_code == 200
        assert response.json() == response_template

        called_filter = mock_clinic_assets_service.get_data.call_args[0][0]
        assert isinstance(called_filter, ClinicFilter)
        assert called_filter.date_from == "2025-01-01"
        assert called_filter.date_to == "2025-12-31"
        assert called_filter.status == ClinicStatus.ALL

    @pytest.mark.asyncio
    async def test_get_clinic_assets_with_filters(self, client, mock_clinic_assets_service):
        """Проверка получения активов поликлиники с фильтрами."""
        response_template = {
            "hospital_name": "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
            "items": [],
            "total": 0,
            "page": 2,
            "limit": 20,
            "total_pages": 0
        }

        mock_clinic_assets_service.get_data.return_value = ClinicResponse(**response_template)

        response = client.get(
            "/api/journal/clinic-assets",
            params={
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
                "patient_identifier": "070210653849",
                "department": "072",
                "status": "in_progress",
                "sort_by": "patient_name_asc",
                "page": 2,
                "limit": 20
            }
        )

        assert response.status_code == 200

        called_filter = mock_clinic_assets_service.get_data.call_args[0][0]
        assert isinstance(called_filter, ClinicFilter)
        assert called_filter.date_from == "2025-01-01"
        assert called_filter.date_to == "2025-12-31"
        assert called_filter.patient_identifier == "070210653849"
        assert called_filter.department == "072"
        assert called_filter.status == ClinicStatus.IN_PROGRESS
        assert called_filter.sort_by == "patient_name_asc"
        assert called_filter.page == 2
        assert called_filter.limit == 20

    @pytest.mark.asyncio
    async def test_get_clinic_assets_missing_required_params(self, client):
        """Проверка получения ошибки при отсутствии обязательных параметров."""
        response = client.get("/api/journal/clinic-assets")

        assert response.status_code == 422
        assert "detail" in response.json()

        errors = response.json()["detail"]
        error_fields = [error["loc"][1] for error in errors]
        assert "date_from" in error_fields
        assert "date_to" in error_fields