import requests
import uuid
import json
import asyncio

from app.db.db import DB
from app.yandexDelivery.api.create_claim import build_create_claim_response

from datetime import datetime, timedelta


class Order:
    def __init__(self, orders_table_name: str) -> None:
        self.db = DB()
        self.table = orders_table_name
        self.id = None
        self.params = ["id", "shop_id", "shop_secret_key", "shop_tg_group_id",
                       "shop_title", "shop_latitude", "shop_longitude", "shop_contact_phone",
                       "shop_address", "customer_name", "customer_contact_phone", "order_wc_id",
                       "order_products", "order_customer_note", "order_price", "order_payment_method_title",
                       "delivery_type", "delivery_price", "delivery_address", "delivery_latitude",
                       "delivery_longitude", "delivery_api_key", "delivery_geo_key", "status",
                       "order_created_time", "order_created_timezone", "shop_contact_name"]
        self.delivery_params = ["delivery_id", "delivery_order_id", "delivery_claim_id", "delivery_LUT",
                                "delivery_claim_version", "delivery_status", "delivery_offer_valid_until"]

        self.shop_id = None
        self.shop_secret_key = None
        self.shop_tg_group_id = None
        self.shop_title = None
        self.shop_latitude = None
        self.shop_longitude = None
        self.shop_contact_phone = None
        self.shop_contact_name = None
        self.shop_address = None
        self.customer_name = None
        self.customer_contact_phone = None
        self.order_wc_id = None
        self.order_products = None
        self.order_customer_note = None
        self.order_price = None
        self.order_payment_method_title = None
        self.order_created_time = None
        self.order_created_timezone = None
        self.delivery_type = None
        self.delivery_price = None
        self.delivery_address = None
        self.delivery_latitude = None
        self.delivery_longitude = None
        self.delivery_api_key = None
        self.delivery_geo_key = None
        self.status = None

        self.delivery_id = None
        self.delivery_order_id = None
        self.delivery_claim_id = None
        self.delivery_id = None
        self.delivery_LUT = None
        self.delivery_status = None
        self.delivery_claim_version = None
        self.delivery_price = None
        self.delivery_offer_valid_until = None

        for i in range(len(self.params)):
            setattr(self, self.params[i], None)

    async def new_order(self, data: dict):
        self.id = await self.db.get_last_row_id(self.table) + 1

        for key, value in data.items():
            setattr(self, key, value)

        await self.db.insert(table_name=self.table,
                             id=self.id,
                             **data)

        return self.id

    async def from_db(self, ID: int):
        data = await self.db.select_where(self.table, 'id', ID)

        for i in range(len(self.params)):
            setattr(self, self.params[i], data[i])

        delivery_data = await self.db.select_where('delivery', 'order_id', self.id)
        if delivery_data:
            for i in range(len(self.delivery_params)):
                setattr(self, self.delivery_params[i], delivery_data[i])

    async def update_status(self, status: str):
        self.status = status
        await self.db.update(table_name=self.table,
                             where_cond='id',
                             where_value=self.id,
                             status=status)

    async def __check_status(self):
        request = f"https://b2b.taxi.yandex.net/b2b/cargo/integration/v2/claims/info?claim_id={self.delivery_claim_id}"

        headers = {'content-type': 'application/json', 'Accept-Language': 'ru',
                   'Authorization': f'Bearer {self.delivery_api_key}'}

        r = requests.post(request, headers=headers)

        return r.json()

    async def get_new_order_price(self):
        response = await self.__check_status()

        if 'status' in response:
            if response['status'] == 'ready_for_approval':
                self.delivery_status = 'ready_for_approval'
                await self.update_status('delivery_ready_for_approval')
                await self.db.update(table_name='delivery',
                                     where_cond='id',
                                     where_value=self.delivery_id,
                                     status=self.delivery_status,
                                     offer_valid_until=response['pricing']['offer']['valid_until'])
                return response['pricing']['offer']['price']

        await asyncio.sleep(0.5)
        return await self.get_new_order_price()

    async def get_courier_info(self):
        response = await self.__check_status()

        if 'status' in response:
            if response['status'] == 'performer_found':
                await self.update_status('courier_found')
                return response['performer_info'], response['route_points']

        await asyncio.sleep(1)
        return await self.get_courier_info()

    async def confirm_delivery(self):
        request = {
            "version": 1
        }

        headers = {'content-type': 'application/json', 'Accept-Language': 'ru',
                   'Authorization': f'Bearer {self.delivery_api_key}'}

        r = requests.post(f"https://b2b.taxi.yandex.net/b2b/cargo/integration/v2/claims/accept?claim_id={self.delivery_claim_id}",
                          data=json.dumps(request), headers=headers)

        res_data = r.json()

        if res_data:
            return True

    async def check_order_confirmed(self):
        await self.from_db(self.id)

        if self.status in ["delivery_confirmed", "cancelled", "delivery_cancelled"]:
            return

        if self.delivery_offer_valid_until:
            valid_until_str = str(self.delivery_offer_valid_until)
            date_time_str = valid_until_str.split('T')[0] + ' ' + valid_until_str.split('T')[1].split('+')[0]
            valid_until = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")

            current_time = datetime.utcnow()

            time_difference = valid_until - current_time

            if time_difference <= timedelta(minutes=9.5):
                return 'validate_time_out'

        await asyncio.sleep(5)
        return await self.check_order_confirmed()

    async def create_claim(self):
        request = build_create_claim_response(shop_title=self.shop_title, shop_contact_phone=self.shop_contact_phone,
                                              order_total_price=str(self.order_price),
                                              shop_longitude=self.shop_longitude, shop_latitude=self.shop_latitude,
                                              shop_address=self.shop_address, shop_contact_name=self.shop_contact_name,
                                              customer_longitude=self.delivery_longitude,
                                              customer_latitude=self.delivery_latitude,
                                              customer_address=self.delivery_address,
                                              customer_contact_phone=self.customer_contact_phone,
                                              customer_contact_name=self.customer_name)

        headers = {'content-type': 'application/json', 'Accept-Language': 'ru',
                   'Authorization': f'Bearer {self.delivery_api_key}'}

        order_uuid = str(uuid.uuid4())

        r = requests.post(f"https://b2b.taxi.yandex.net/b2b/cargo/integration/v2/claims/create?request_id={order_uuid}",
                          data=json.dumps(request), headers=headers)
        res_data = r.json()

        self.delivery_claim_id = res_data['id']
        self.delivery_id = int(await self.db.get_last_row_id('delivery')) + 1
        self.delivery_LUT = res_data['updated_ts']
        self.delivery_status = res_data['status']
        self.delivery_claim_version = res_data['version']

        await self.db.insert('delivery', id=self.delivery_id,
                             order_id=self.id, claim_id=self.delivery_claim_id,
                             last_updated_time=self.delivery_LUT, version=self.delivery_claim_version,
                             status=self.delivery_status)

    async def __check_cancel(self):
        headers = {'content-type': 'application/json', 'Accept-Language': 'ru',
                   'Authorization': f'Bearer {self.delivery_api_key}'}

        r = requests.post(f"https://b2b.taxi.yandex.net/b2b/cargo/integration/v2/claims/cancel-info?claim_id={self.delivery_claim_id}",
                          headers=headers)
        res_data = r.json()

        if res_data['cancel_state'] == "free":
            return True

        return False

    async def cancel(self):
        if await self.__check_cancel():
            headers = {'content-type': 'application/json', 'Accept-Language': 'ru',
                       'Authorization': f'Bearer {self.delivery_api_key}'}

            request = {
                "cancel_state": "free",
                "version": self.delivery_claim_version
            }

            r = requests.post(
                f"https://b2b.taxi.yandex.net/b2b/cargo/integration/v2/claims/cancel?claim_id={self.delivery_claim_id}",
                data=json.dumps(request), headers=headers)
            res_data = r.json()
