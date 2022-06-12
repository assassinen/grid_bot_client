import time
from datetime import datetime

from ex_bitmex.session import Session


class BitmexExchangeInterface:
    def __init__(self, key, secret, base_url, api_url, instrument):
        self.instrument = instrument
        self.session = Session(key, secret, base_url, api_url)

    def get_positions(self):
        query = (
            "?filter=%7B%22symbol%22%3A%20%22{}%22%7D"
            "&columns=%5B%22avgEntryPrice%22%5D".format(self.instrument)
        )
        result = self.session.get("position", query)
        positions = result[0] if result else {}
        return {
            "price": positions.get("avgEntryPrice", 0),
            "size": positions.get("currentQty", 0),
        }

    def get_last_trade_price(self):
        query = "?symbol={}&count=1&reverse=true".format(self.instrument)
        result = self.session.get("trade", query)
        trade_price = result[0] if result else {}
        return trade_price["price"] if result else None

    def get_last_order_price(self, side):
        last_order_price = [
            order["price"] for order in self.get_open_orders() if order["side"] == side
        ]
        return (
            last_order_price[0]
            if len(last_order_price) > 0
            else self.get_last_trade_price()
        )

    def get_order_params_from_responce(self, responce):
        status_mapp = {"New": "open", "Canceled": "cancelled"}
        data_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        dt = responce.get("timestamp", "1970-01-01T00:00:00.000Z")
        timestamp = int(
            time.mktime(datetime.strptime(dt, data_format).timetuple()) * 1000
        ) + int(dt[-4:-1])
        return {
            "price": responce.get("price"),
            "size": responce.get("orderQty"),
            "side": responce.get("side", "No data").lower(),
            "order_id": responce.get("orderID"),
            "status": status_mapp.get(
                responce.get("ordStatus"), responce.get("ordStatus").lower()
            ),
            "timestamp": timestamp,
        }

    def get_order_state(self, order_id):
        query = f"?filter=%7B%22orderID%22%3A%22{order_id}%22%7D&count=1&reverse=false"
        try:
            order = self.session.get("order", query)[0]
        except Exception as r:
            order = {"orderID": order_id, "ordStatus": "cancelled"}
        return self.get_order_params_from_responce(order)

    def get_orders_state(self, orders_state):
        open_orders = self.get_open_orders()
        open_order_ids = [open_order.get("order_id") for open_order in open_orders]
        order_state_ids = [
            order_id for order_id in orders_state if order_id not in open_order_ids
        ]
        return open_orders + [
            self.get_order_state(order_id) for order_id in order_state_ids
        ]

    def get_open_orders(self):
        query = (
            "?filter=%7B%22ordStatus%22%3A%20%22New%22%7D&reverse=true"
            "&columns=price%2C%20orderQty%2C%20side%2C%20ordStatus%2C%20timestamp"
            "&symbol={}".format(self.instrument)
        )
        open_orders = self.session.get("order", query)
        return [self.get_order_params_from_responce(order) for order in open_orders]

    def create_order(self, order=""):
        postdict = {
            "symbol": self.instrument,
            "side": order["side"].title(),
            "orderQty": order["size"],
            "price": order["price"],
            "ordType": "Limit",
            "execInst": "ParticipateDoNotInitiate",
        }
        order = self.session.post("order", postdict)
        return self.get_order_params_from_responce(order)

    def cancel_all_orders(self):
        postdict = {"symbol": self.instrument}
        return self.session.delete("order/all", postdict)
