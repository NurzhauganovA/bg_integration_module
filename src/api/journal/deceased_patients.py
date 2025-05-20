from fastapi import APIRouter, Query
from typing import Optional

from services.journal.deceased_patients_service import DeceasedPatientsService
from data_subjects.responses.deceased_patients_response import DeceasedResponse
from data_subjects.requests.deceased_patients_request import DeceasedFilter

router = APIRouter()


@router.get("/deceased-patients", response_model=DeceasedResponse, tags=["deceased_patients"])
async def get_deceased_patients(
        patient_identifier: Optional[str] = Query(None, description="ИИН или ФИО пациента"),
        date_from: str = Query(..., description="Дата начала периода (ГГГГ-ММ-ДД)"),
        date_to: str = Query(..., description="Дата окончания периода (ГГГГ-ММ-ДД)"),
        department: Optional[str] = Query("all", description="Участок/отделение"),
        delivery_status: Optional[str] = Query(None, description="Статус доставки"),
        sort_by: Optional[str] = Query("date_desc", description="Поле для сортировки"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(10, description="Количество записей на странице"),
):
    """
    Получение данных об умерших пациентах в указанном диапазоне дат.

    Этот эндпоинт получает записи об умерших пациентах из Бюро госпитализации
    и форматирует их в соответствии с требованиями к данным умерших пациентов.
    """
    filter_params = DeceasedFilter(
        patient_identifier=patient_identifier,
        date_from=date_from,
        date_to=date_to,
        department=department,
        delivery_status=delivery_status,
        sort_by=sort_by,
        page=page,
        limit=limit
    )

    return await DeceasedPatientsService.get_data(filter_params)