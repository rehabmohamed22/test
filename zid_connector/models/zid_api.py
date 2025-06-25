import requests


class ZidAPIService:
    BASE_URL = "https://api.zid.sa/v1/managers/store"

    def __init__(self, access_token, manager_token):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Manager-Token": manager_token,
            "Accept-Language": "ar",
        }

    def update_order_status(self, order_id, status, inventory_address_id=None, tracking_number=None, tracking_url=None,
                            waybill_url=None):
        url = f"{self.BASE_URL}/orders/{order_id}/change-order-status"
        data = {
            "order_status": status,
        }

        if inventory_address_id:
            data["inventory_address_id"] = inventory_address_id
        if tracking_number:
            data["tracking_number"] = tracking_number
        if tracking_url:
            data["tracking_url"] = tracking_url
        if waybill_url:
            data["waybill_url"] = waybill_url

        response = requests.post(url, headers=self.headers, data=data)
        return response.json()
