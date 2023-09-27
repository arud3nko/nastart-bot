def build_get_offer_request(shop_longitude: float, shop_latitude: float, shop_address: str,
                            customer_longitude: str, customer_latitude: str, customer_address: str,) -> dict:

    request = {
        "items": [
            {
                "quantity": 1,
                "size": {
                    "height": 0.45,
                    "length": 0.45,
                    "width": 0.45
                },
            }
        ],
        "requirements": {
          "client_requirements": {
            "cargo_options": [
              "auto_courier"
            ],
            "taxi_class": "express"
          },
        },
        "route_points": [
            {
                "coordinates": [
                    float(shop_longitude), float(shop_latitude)
                ],
                "fullname": shop_address
            },
            {
              "coordinates": [
                float(customer_longitude), float(customer_latitude)
              ],
              "fullname": customer_address
            }
        ],
    }

    return request
