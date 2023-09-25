def build_create_claim_response(shop_title: str, shop_contact_phone: str, order_total_price: str,
                                shop_longitude: float, shop_latitude: float, shop_address: str,
                                shop_contact_name: str,
                                customer_longitude: str, customer_latitude: str, customer_address: str,
                                customer_contact_phone: str, customer_contact_name: str):

    request = {
      "auto_accept": False,
      "client_requirements": {
        "cargo_options": [
          "auto_courier"
        ],
        "taxi_class": "express"
      },
      "comment": f"Еда из ресторана {shop_title}",
      "emergency_contact": {
        "name": "test",
        "phone": shop_contact_phone,
      },
      "items": [
        {
          "cost_currency": "RUB",
          "cost_value": order_total_price,
          "droppof_point": 2,
          "pickup_point": 1,
          "quantity": 1,
          "size": {
            "height": 0.45,
            "length": 0.45,
            "width": 0.45
          },
          "title": "Еда из ресторана",
        }
      ],
      "referral_source": "Nastart Integration",
      "route_points": [
        {
          "address": {
            "coordinates": [
              float(shop_longitude), float(shop_latitude)
            ],
            "fullname": shop_address,
          },
          "contact": {
            "name": shop_contact_name,
            "phone": shop_contact_phone,
          },
          "point_id": 1,
          "skip_confirmation": True,
          "type": "source",
          "visit_order": 1
        },
        {
          "address": {
            "coordinates": [
              float(customer_longitude), float(customer_latitude)
            ],
            "fullname": customer_address,
          },
          "contact": {
            "name": customer_contact_name,
            "phone": customer_contact_phone,
          },
          "point_id": 2,
          "skip_confirmation": True,
          "type": "destination",
          "visit_order": 2
        }
      ],
    }

    return request
