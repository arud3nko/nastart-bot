import requests

from app.db.db import DB


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

