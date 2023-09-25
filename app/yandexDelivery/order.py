import requests
import uuid
import json

from app.db.db import DB
from app.yandexDelivery.api.create_claim import build_create_claim_response


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
                       "order_created_time"]

        self.shop_id = None
        self.shop_secret_key = None
        self.shop_tg_group_id = None
        self.shop_title = None
        self.shop_latitude = None
        self.shop_longitude = None
        self.shop_contact_phone = None
        self.shop_address = None
        self.customer_name = None
        self.customer_contact_phone = None
        self.order_wc_id = None
        self.order_products = None
        self.order_customer_note = None
        self.order_price = None
        self.order_payment_method_title = None
        self.order_created_time = None
        self.delivery_type = None
        self.delivery_price = None
        self.delivery_address = None
        self.delivery_latitude = None
        self.delivery_longitude = None
        self.delivery_api_key = None
        self.delivery_geo_key = None

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
            if getattr(self, self.params[i]) is None:
                setattr(self, self.params[i], data[i])

    async def update_status(self, status: str):
        await self.db.update(table_name=self.table,
                             where_cond='id',
                             where_value=self.id,
                             status=status)

    async def create_claim(self):
        request = build_create_claim_response(shop_title=self.shop_title, shop_contact_phone=self.shop_contact_phone,
                                              order_total_price=str(self.order_price),
                                              shop_longitude=self.shop_longitude, shop_latitude=self.shop_latitude,
                                              shop_address=self.shop_address, shop_contact_name="test",
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
