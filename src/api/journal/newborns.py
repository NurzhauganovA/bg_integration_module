from fastapi import APIRouter, Query
from typing import Optional

from services.journal.newborns_service import NewbornsService
from data_subjects.responses.newborns_response import NewbornResponse
from data_subjects.requests.newborns_request import NewbornFilter, NewbornStatus

router = APIRouter()


@router.get("/newborns", response_model=NewbornResponse, tags=["newborns"])
async def get_newborns(
        patient_identifier: Optional[str] = Query(None, description="ИИН или ФИО пациента (новорожденного или матери)"),
        date_from: str = Query(..., description="Дата начала периода (ГГГГ-ММ-ДД)"),
        date_to: str = Query(..., description="Дата окончания периода (ГГГГ-ММ-ДД)"),
        department: Optional[str] = Query("all", description="Участок/отделение"),
        status: Optional[NewbornStatus] = Query(NewbornStatus.ALL, description="Статус новорожденного"),
        delivery_status: Optional[str] = Query(None, description="Статус доставки"),
        sort_by: Optional[str] = Query("date_desc", description="Поле для сортировки"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(10, description="Количество записей на странице"),
):
    """
    Получение данных о новорожденных в указанном диапазоне дат.

    Этот эндпоинт получает записи о новорожденных из Бюро госпитализации
    и форматирует их в соответствии с требованиями к данным новорожденных.
    """
    filter_params = NewbornFilter(
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

    return await NewbornsService.get_data(filter_params)