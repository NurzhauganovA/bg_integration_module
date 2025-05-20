from integration_sdk_orkendeu_mis.fetchers.sync_soap import SyncSOAPFetcher
from typing import Dict


class BGReferralsFetcher(SyncSOAPFetcher):
    method = "POST"
    content_type = "text/xml"

    def __init__(self):
        self.url = "http://127.0.0.1:8010/"
        super().__init__(url=self.url)

    def build_payload(self, validated_data: Dict) -> str:
        return f"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <SendMessage xmlns="http://bip.bee.kz/SyncChannel/v10/Types">
                            <request>
                                <requestInfo>
                                    <messageId>auto-generated-id</messageId>
                                    <serviceId>bg.service.searchReferrals</serviceId>
                                    <messageDate>2024-01-01T00:00:00Z</messageDate>
                                    <sessionId>test-session</sessionId>
                                </requestInfo>
                                <requestData>
                                    <ns4:data xmlns:ns4="http://bip.bee.kz/SyncChannel/v10/Interfaces"
                                              xmlns:cs="http://bg.kz/searchReferrals"
                                              xsi:type="cs:SearchReferrals"
                                              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                        <dateFrom>{validated_data["dateFrom"]}</dateFrom>
                                        <dateTo>{validated_data["dateTo"]}</dateTo>
                                        <patientIINOrFIO>{validated_data["patientIINOrFIO"]}</patientIINOrFIO>
                                        <searchDirections>true</searchDirections>
                                        <referralCode>true</referralCode>
                                        <searchHospitalized>true</searchHospitalized>
                                        <searchRefusal>true</searchRefusal>
                                    </ns4:data>
                                </requestData>
                            </request>
                        </SendMessage>
                    </soap:Body>
                </soap:Envelope>"""
