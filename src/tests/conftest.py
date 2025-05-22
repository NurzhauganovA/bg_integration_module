import pytest
import json
import os
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from pathlib import Path

from main import app


@pytest.fixture
def client():
    """Фикстура для создания тестового клиента."""
    return TestClient(app)


@pytest.fixture
def referrals_json_data():
    """Загрузка тестовых данных о направлениях из JSON файла."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    json_path = os.path.join(base_dir, "assets", "response.json")

    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


@pytest.fixture
def referrals_xml_data():
    """Загрузка тестовых данных о направлениях из XML файла."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    xml_path = os.path.join(base_dir, "assets", "response_bg.xml")

    try:
        with open(xml_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""


@pytest.fixture
def mock_hospital_assets_service():
    """Фикстура для мокирования сервиса активов стационара."""
    with patch('api.journal.hospital_assets.HospitalAssetsService') as mock_service:
        mock_service.get_data = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_hospitalization_rejections_service():
    """Фикстура для мокирования сервиса отказов от госпитализации."""
    with patch('api.journal.hospitalization_rejections.HospitalizationRejectionsService') as mock_service:
        mock_service.get_data = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_ambulance_assets_service():
    """Фикстура для мокирования сервиса активов скорой помощи."""
    with patch('api.journal.ambulance_assets.AmbulanceAssetsService') as mock_service:
        mock_service.get_data = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_newborns_service():
    """Фикстура для мокирования сервиса новорожденных."""
    with patch('api.journal.newborns.NewbornsService') as mock_service:
        mock_service.get_data = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_clinic_assets_service():
    """Фикстура для мокирования сервиса активов поликлиники."""
    with patch('api.journal.clinic_assets.ClinicAssetsService') as mock_service:
        mock_service.get_data = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_deceased_patients_service():
    """Фикстура для мокирования сервиса умерших пациентов."""
    with patch('api.journal.deceased_patients.DeceasedPatientsService') as mock_service:
        mock_service.get_data = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_maternity_assets_service():
    """Фикстура для мокирования сервиса активов роддома."""
    with patch('api.journal.maternity_assets.MaternityAssetsService') as mock_service:
        mock_service.get_data = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_journal_base_service():
    """Фикстура для мокирования базового сервиса журнала."""
    with patch('services.journal_base_service.JournalBaseService._get_bg_data') as mock_get_bg_data:
        from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
        mock_get_bg_data.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": []}
        )
        yield mock_get_bg_data


@pytest.fixture
def mock_bg_referrals_handler():
    """Фикстура для мокирования обработчика запросов к БГ."""
    with patch('services.journal_base_service.BGReferralsHandler') as mock_handler:
        from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
        handler_instance = mock_handler.return_value
        handler_instance.handle = AsyncMock(return_value=HandlerResultDTO(
            success=True,
            data={"referralItems": []}
        ))
        yield handler_instance


@pytest.fixture
def hospital_response_template():
    """Шаблон ответа для активов стационара."""
    return {
        "hospital_name": "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
        "items": [],
        "total": 0,
        "page": 1,
        "limit": 10,
        "total_pages": 0
    }