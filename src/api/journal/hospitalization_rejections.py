from fastapi import APIRouter, Depends, Query
from typing import Optional

from services.journal.hospitalization_rejections_service import HospitalizationRejectionsService
from data_subjects.responses.hospitalization_rejections_response import RejectionResponse
from data_subjects.requests.hospitalization_rejections_request import RejectionFilter, RejectionStatus

router = APIRouter()


@router.get("/hospitalization-rejections", response_model=RejectionResponse, tags=["hospitalization_rejections"])
async def get_hospitalization_rejections(
        patient_identifier: Optional[str] = Query(None, description="ИИН или ФИО пациента"),
        date_from: str = Query(..., description="Дата начала периода (ГГГГ-ММ-ДД)"),
        date_to: str = Query(..., description="Дата окончания периода (ГГГГ-ММ-ДД)"),
        department: Optional[str] = Query("all", description="Участок/отделение"),
        status: Optional[RejectionStatus] = Query(RejectionStatus.ALL, description="Статус отказа"),
        delivery_status: Optional[str] = Query(None, description="Статус доставки"),
        sort_by: Optional[str] = Query("date_desc", description="Поле для сортировки"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(10, description="Количество записей на странице"),
):
    """
    Получение отказов от госпитализации для пациента в указанном диапазоне дат.

    Этот эндпоинт получает записи об отказах в госпитализации из Бюро госпитализации
    и форматирует их в соответствии с требованиями к отказам от госпитализации.
    """
    filter_params = RejectionFilter(
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

    return await HospitalizationRejectionsService.get_data(filter_params)