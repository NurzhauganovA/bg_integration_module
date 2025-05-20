from fastapi import APIRouter, Query
from typing import Optional

from services.journal.maternity_assets_service import MaternityAssetsService
from data_subjects.responses.maternity_assets_response import MaternityResponse
from data_subjects.requests.maternity_assets_request import MaternityFilter, MaternityStatus

router = APIRouter()


@router.get("/maternity-assets", response_model=MaternityResponse, tags=["maternity_assets"])
async def get_maternity_assets(
        patient_identifier: Optional[str] = Query(None, description="ИИН или ФИО пациентки"),
        date_from: str = Query(..., description="Дата начала периода (ГГГГ-ММ-ДД)"),
        date_to: str = Query(..., description="Дата окончания периода (ГГГГ-ММ-ДД)"),
        department: Optional[str] = Query("all", description="Участок/отделение"),
        status: Optional[MaternityStatus] = Query(MaternityStatus.ALL, description="Статус актива"),
        delivery_status: Optional[str] = Query(None, description="Статус доставки"),
        sort_by: Optional[str] = Query("date_desc", description="Поле для сортировки"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(10, description="Количество записей на странице"),
):
    """
    Получение активов роддома для пациентки в указанном диапазоне дат.

    Этот эндпоинт получает записи о пациентках роддома из Бюро госпитализации
    и форматирует их в соответствии с требованиями к активам роддома.
    """
    filter_params = MaternityFilter(
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

    return await MaternityAssetsService.get_data(filter_params)