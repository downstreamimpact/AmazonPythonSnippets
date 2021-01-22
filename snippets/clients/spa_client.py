# pods is Downstream's client for interacting with various Amazon APIs
from pods.clients.selling_partner.selling_partner_api_client import (
    SellingPartnerApiClient,
)


class SpaClient(SellingPartnerApiClient):
    def get_report_document(self, report_document_id: str) -> dict:
        return self.get(f"/reports/2020-09-04/documents/{report_document_id}")
