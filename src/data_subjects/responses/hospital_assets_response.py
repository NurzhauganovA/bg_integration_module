from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class HospitalStatus(str, Enum):
    """ Статус пребывания в стационаре """
    HOSPITALIZED = "hospitalized"  # Госпитализирован
    WAITING = "waiting"  # В приемном покое
    DISCHARGED = "discharged"  # Выписан


class HospitalStatusColor(str, Enum):
    """ Цвет для статуса пребывания в стационаре """
    GREEN = "green"  # Зеленый - для приемного покоя или активных
    BLUE = "blue"  # Синий - для госпитализированных
    GRAY = "gray"  # Серый - для выписанных


class HospitalPatient(BaseModel):
    """Модель пациента стационара"""
    id: str = Field(..., description="ID пациента")
    iin: Optional[str] = Field(None, description="ИИН пациента")
    full_name: str = Field(..., description="ФИО пациента")
    birth_date: Optional[str] = Field(None, description="Дата рождения пациента")


class HospitalAsset(BaseModel):
    """Модель актива стационара"""
    id: str = Field(..., description="ID актива")
    number: str = Field(..., description="Номер")
    receipt_date: str = Field(..., description="Дата получения")
    patient: HospitalPatient = Field(..., description="Информация о пациенте")
    status: HospitalStatus = Field(..., description="Статус пребывания в стационаре")
    status_color: HospitalStatusColor = Field(..., description="Цвет статуса")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Дополнительная информация")


class HospitalAdditionalInfo(BaseModel):
    """Дополнительная информация об активе стационара"""
    treatment_outcome: Optional[str] = Field(None, description="Исход лечения")
    discharge_outcome: Optional[str] = Field(None, description="Исход пребывания")
    hospitalization_period: Optional[str] = Field(None, description="Период пребывания в стационаре")
    diagnosis: Optional[str] = Field(None, description="Заболевание")
    doctor: Optional[str] = Field(None, description="Врач")
    executor: Optional[str] = Field(None, description="Исполнитель")
    department: Optional[str] = Field(None, description="Участок")


class HospitalAssetsResponse(BaseModel):
    """Ответ с активами стационара"""
    hospital_name: str = Field(..., description="Название медицинского учреждения")
    items: List[HospitalAsset] = Field(default_factory=list, description="Список активов стационара")
    total: int = Field(0, description="Общее количество записей")
    page: int = Field(1, description="Текущая страница")
    limit: int = Field(10, description="Количество записей на странице")
    total_pages: int = Field(1, description="Общее количество страниц")