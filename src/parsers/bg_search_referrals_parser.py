from integration_sdk_orkendeu_mis.parsers.abstract import AbstractParser
from integration_sdk_orkendeu_mis.parsers.mixins.xml_utils import XMLUtilsMixin
from integration_sdk_orkendeu_mis.parsers.mixins.error_check import SubjectNotFoundError
from typing import Union


class BGReferralsParser(AbstractParser):
    """
    Парсер для ответа БГ по направлению пациента.
    """

    def parse(self, data_to_parse: bytes) -> Union[dict, list]:
        if not data_to_parse:
            raise SubjectNotFoundError("Пустой ответ от БГ")

        root = XMLUtilsMixin().parse_xml(data_to_parse)
        items = root.findall(".//referralList/referralItem")

        return {
            "referralItems": [
                {
                    "iin": item.findtext("patient/personin"),
                    "full_name": item.findtext("patient/personFullName"),
                    "hospital": item.findtext("orgHealthCareRef/name"),
                    "doctor": item.findtext("directDoctor"),
                    "diagnosis": item.findtext("sick/name"),
                    "referral_type": item.findtext("referralType/name")
                }
                for item in items
            ]
        }