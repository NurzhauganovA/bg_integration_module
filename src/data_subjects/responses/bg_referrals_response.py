from typing import Optional, List, Any, Self
from pydantic import BaseModel, Field


class Sick(BaseModel):
    beginDate: Optional[str] = Field(None, description="Дата начала больничного листа")
    code: Optional[str] = Field(None, description="Код заболевания")
    endDate: Optional[str] = Field(None, description="Дата окончания больничного листа")
    id: Optional[str] = Field(None, description="ID больничного листа")
    idCode: Optional[str] = Field(None, description="ID кода заболевания")
    name: Optional[str] = Field(None, description="Название заболевания")

    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("Sick object must have a valid value")
        return value


class OrgHealthCare(BaseModel):
    code: Optional[str] = Field(None, description="Код организации здравоохранения")
    funcStructureOrgID: Optional[str] = Field(None, description="ID функциональной структуры организации")
    name: Optional[str] = Field(None, description="Название организации здравоохранения")
    orgHealthCareID: Optional[str] = Field(None, description="ID организации здравоохранения")

    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("OrgHealthCare object must have a valid value")
        return value


class ReferralType(BaseModel):
    beginDate: Optional[str] = Field(None, description="Дата начала направления")
    code: Optional[str] = Field(None, description="Код направления")
    endDate: Optional[str] = Field(None, description="Дата окончания направления")
    id: Optional[str] = Field(None, description="ID направления")
    idCode: Optional[str] = Field(None, description="ID кода направления")
    name: Optional[str] = Field(None, description="Название направления")

    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("ReferralType object must have a valid value")
        return value


class Patient(BaseModel):
    birthDate: Optional[str] = Field(None, description="Дата рождения пациента")
    citizenIdCode: Optional[str] = Field(None, description="ID кода гражданства")
    firstName: Optional[str] = Field(None, description="Имя пациента")
    hGBD: Optional[str] = Field(None, description="ID пациента")
    id: Optional[str] = Field(None, description="ID пациента")
    lastName: Optional[str] = Field(None, description="Фамилия пациента")
    nationalityIdCode: Optional[str] = Field(None, description="ID кода национальности")
    personFullName: Optional[str] = Field(None, description="Полное имя пациента")
    personin: Optional[str] = Field(None, description="ИИН пациента")
    rpnID: Optional[str] = Field(None, description="ID РПН")
    secondName: Optional[str] = Field(None, description="Отчество пациента")
    sexIdCode: Optional[str] = Field(None, description="ID кода пола")
    unknownPerson: Optional[bool] = Field(None, description="Неизвестный пациент")

    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("Patient object must have a valid value")
        return value


class BGReferralItem(BaseModel):
    additionalInformation: Optional[str] = Field(None, description="Дополнительная информация")
    address: Optional[str] = Field(None, description="Адрес")
    cardNumber: Optional[str] = Field(None, description="Номер карты")
    currentPlanDate: Optional[str] = Field(None, description="Дата текущего плана")
    dayHospitalType: Optional[str] = Field(None, description="Тип дневного стационара")
    directDoctor: Optional[str] = Field(None, description="Врач-специалист")
    finSrcParent: Optional[str] = Field(None, description="ID источника финансирования")
    fsmsStatus: Optional[str] = Field(None, description="Статус ФСМС")
    hasConfirm: Optional[str] = Field(None, description="Наличие подтверждения")
    hasFiles: Optional[str] = Field(None, description="Наличие файлов")
    hasRefusal: Optional[str] = Field(None, description="Наличие отказа")
    hasRehabilitationFiles: Optional[str] = Field(None, description="Наличие файлов реабилитации")
    hospitalCode: Optional[str] = Field(None, description="Код больницы")
    hospitalDate: Optional[str] = Field(None, description="Дата больницы")
    hospitalNoticeStatuses: Optional[str] = Field(None, description="Статусы уведомлений больницы")
    hospitalPlanDate: Optional[str] = Field(None, description="Дата плана больницы")
    id: Optional[str] = Field(None, description="ID направления")
    inPatientHelpType: Optional[str] = Field(None, description="Тип помощи в стационаре")
    outDate: Optional[str] = Field(None, description="Дата выписки")
    polyclinicPlanDate: Optional[str] = Field(None, description="Дата плана поликлиники")
    protocolDate: Optional[str] = Field(None, description="Дата протокола")
    protocolNumber: Optional[str] = Field(None, description="Номер протокола")
    regDate: Optional[str] = Field(None, description="Дата регистрации")
    refusalRegDate: Optional[str] = Field(None, description="Дата регистрации отказа")
    refuseJustification: Optional[str] = Field(None, description="Обоснование отказа")
    workPlace: Optional[str] = Field(None, description="Место работы")

    bedProfile: Optional[ReferralType] = Field(None, description="Профиль койки")
    benefitType: Optional[ReferralType] = Field(None, description="Тип льготы")
    orgHealthCareDirect: Optional[OrgHealthCare] = Field(None, description="Организация здравоохранения по направлению")
    orgHealthCareRef: Optional[OrgHealthCare] = Field(None, description="Организация здравоохранения по реабилитации")
    orgHealthCareRequest: Optional[OrgHealthCare] = Field(None, description="Организация здравоохранения по запросу")
    referralTarget: Optional[ReferralType] = Field(None, description="Цель направления")
    referralType: Optional[ReferralType] = Field(None, description="Тип направления")
    rehabilitationType: Optional[ReferralType] = Field(None, description="Тип реабилитации")
    sick: Optional[Sick] = Field(None, description="Болезнь")
    refuseReason: Optional[ReferralType] = Field(None, description="Причина отказа")
    patient: Optional[Patient] = Field(None, description="Пациент")

    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("BGReferralItem object must have a valid value")
        return value


class BGReferralsResponse(BaseModel):
    referralItems: List[BGReferralItem] = Field(None, description="Список направлений")

    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("BGReferralsResponse object must have a valid value")
        return value
