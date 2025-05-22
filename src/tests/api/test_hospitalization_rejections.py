import pytest
from unittest.mock import AsyncMock

from data_subjects.responses.hospitalization_rejections_response import RejectionResponse
from data_subjects.requests.hospitalization_rejections_request import RejectionFilter, RejectionStatus


class TestHospitalizationRejectionsAPI:
    """Тесты для API отказов от госпитализации."""

    @pytest.mark.asyncio
    async def test_get_hospitalization_rejections_success(self, client, mock_hospitalization_rejections_service):
        """Проверка успешного получения отказов от госпитализации."""
        response_template = {
            "hospital_name": "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
            "items": [],
            "total": 0,
            "page": 1,
            "limit": 10,
            "total_pages": 0
        }

        mock_hospitalization_rejections_service.get_data.return_value = RejectionResponse(**response_template)

        response = client.get(
            "/api/journal/hospitalization-rejections",
            params={
                "date_from": "2025-01-01",
                "date_to": "2025-12-31"
            }
        )

        assert response.status_code == 200
        assert response.json() == response_template

        called_filter = mock_hospitalization_rejections_service.get_data.call_args[0][0]
        assert isinstance(called_filter, RejectionFilter)
        assert called_filter.date_from == "2025-01-01"
        assert called_filter.date_to == "2025-12-31"
        assert called_filter.status == RejectionStatus.ALL

    @pytest.mark.asyncio
    async def test_get_hospitalization_rejections_with_filters(self, client, mock_hospitalization_rejections_service):
        """Проверка получения отказов от госпитализации с фильтрами."""
        response_template = {
            "hospital_name": "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
            "items": [],
            "total": 0,
            "page": 2,
            "limit": 20,
            "total_pages": 0
        }

        mock_hospitalization_rejections_service.get_data.return_value = RejectionResponse(**response_template)

        response = client.get(
            "/api/journal/hospitalization-rejections",
            params={
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
                "patient_identifier": "070210653849",
                "department": "072",
                "status": "rejected",
                "sort_by": "patient_name_asc",
                "page": 2,
                "limit": 20
            }
        )

        assert response.status_code == 200

        called_filter = mock_hospitalization_rejections_service.get_data.call_args[0][0]
        assert isinstance(called_filter, RejectionFilter)
        assert called_filter.date_from == "2025-01-01"
        assert called_filter.date_to == "2025-12-31"
        assert called_filter.patient_identifier == "070210653849"
        assert called_filter.department == "072"
        assert called_filter.status == RejectionStatus.REJECTED
        assert called_filter.sort_by == "patient_name_asc"
        assert called_filter.page == 2
        assert called_filter.limit == 20

    @pytest.mark.asyncio
    async def test_get_hospitalization_rejections_missing_required_params(self, client):
        """Проверка получения ошибки при отсутствии обязательных параметров."""
        response = client.get("/api/journal/hospitalization-rejections")

        assert response.status_code == 422
        assert "detail" in response.json()

        errors = response.json()["detail"]
        error_fields = [error["loc"][1] for error in errors]
        assert "date_from" in error_fields
        assert "date_to" in error_fields