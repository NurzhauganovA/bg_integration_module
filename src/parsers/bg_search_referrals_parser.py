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

        xml_utils = XMLUtilsMixin()
        root = xml_utils.parse_xml(data_to_parse)

        items = root.findall(".//referralItem")
        if not items:
            raise SubjectNotFoundError("Не найдено направлений в ответе БГ")

        parsed_items = [xml_utils.element_to_dict(item) for item in items]

        return {
            "referralItems": parsed_items
        }