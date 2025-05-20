from fastapi import APIRouter, Query
from typing import Optional

from services.journal.ambulance_assets_service import AmbulanceAssetsService
from data_subjects.responses.ambulance_assets_response import AmbulanceResponse
from data_subjects.requests.ambulance_assets_request import AmbulanceFilter, AmbulanceStatus

router = APIRouter()


@router.get("/ambulance-assets", response_model=AmbulanceResponse, tags=["ambulance_assets"])
async def get_ambulance_assets(
        patient_identifier: Optional[str] = Query(None, description="ИИН или ФИО пациента"),
        date_from: str = Query(..., description="Дата начала периода (ГГГГ-ММ-ДД)"),
        date_to: str = Query(..., description="Дата окончания периода (ГГГГ-ММ-ДД)"),
        department: Optional[str] = Query("all", description="Участок/отделение"),
        status: Optional[AmbulanceStatus] = Query(AmbulanceStatus.ALL, description="Статус актива"),
        delivery_status: Optional[str] = Query(None, description="Статус доставки"),
        sort_by: Optional[str] = Query("date_desc", description="Поле для сортировки"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(10, description="Количество записей на странице"),
):
    """
    Получение активов скорой помощи для пациента в указанном диапазоне дат.

    Этот эндпоинт получает записи о вызовах скорой помощи из Бюро госпитализации
    и форматирует их в соответствии с требованиями к активам скорой помощи.
    """
    filter_params = AmbulanceFilter(
        patient_identifier=patient_identifier,
        date_from=date_from,
        date_to=date_to,
        department=department,
        status=status,
        delivery_status=delivery_status,
        sort_by=sort_by,
        page=page,
        limit=limit
    )

    return await AmbulanceAssetsService.get_data(filter_params)