import pytest
from unittest.mock import AsyncMock

from data_subjects.responses.hospital_assets_response import HospitalAssetsResponse
from data_subjects.requests.hospital_assets_request import HospitalAssetsFilter, HospitalAssetStatus


class TestHospitalAssetsAPI:
    """Тесты для API активов стационара."""

    @pytest.mark.asyncio
    async def test_get_hospital_assets_success(self, client, mock_hospital_assets_service, hospital_response_template):
        """Проверка успешного получения активов стационара."""
        mock_hospital_assets_service.get_data.return_value = HospitalAssetsResponse(**hospital_response_template)

        response = client.get(
            "/api/journal/hospital-assets",
            params={
                "date_from": "2025-01-01",
                "date_to": "2025-12-31"
            }
        )

        assert response.status_code == 200
        assert response.json() == hospital_response_template

        called_filter = mock_hospital_assets_service.get_data.call_args[0][0]
        assert isinstance(called_filter, HospitalAssetsFilter)
        assert called_filter.date_from == "2025-01-01"
        assert called_filter.date_to == "2025-12-31"
        assert called_filter.status == HospitalAssetStatus.ALL
        assert called_filter.department == "all"

    @pytest.mark.asyncio
    async def test_get_hospital_assets_with_filters(self, client, mock_hospital_assets_service,
                                                    hospital_response_template):
        """Проверка получения активов стационара с фильтрами."""
        mock_hospital_assets_service.get_data.return_value = HospitalAssetsResponse(**hospital_response_template)

        # Выполняем запрос с фильтрами
        response = client.get(
            "/api/journal/hospital-assets",
            params={
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
                "patient_identifier": "070210653849",
                "department": "072",
                "status": "hospitalized",
                "sort_by": "patient_name_asc",
                "page": 2,
                "limit": 20
            }
        )

        assert response.status_code == 200

        called_filter = mock_hospital_assets_service.get_data.call_args[0][0]
        assert isinstance(called_filter, HospitalAssetsFilter)
        assert called_filter.date_from == "2025-01-01"
        assert called_filter.date_to == "2025-12-31"
        assert called_filter.patient_identifier == "070210653849"
        assert called_filter.department == "072"
        assert called_filter.status == HospitalAssetStatus.HOSPITALIZED
        assert called_filter.sort_by == "patient_name_asc"
        assert called_filter.page == 2
        assert called_filter.limit == 20

    @pytest.mark.asyncio
    async def test_get_hospital_assets_missing_required_params(self, client):
        """Проверка получения ошибки при отсутствии обязательных параметров."""
        response = client.get("/api/journal/hospital-assets")

        assert response.status_code == 422
        assert "detail" in response.json()

        errors = response.json()["detail"]
        error_fields = [error["loc"][1] for error in errors]
        assert "date_from" in error_fields
        assert "date_to" in error_fields