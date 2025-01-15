import unittest
from fastapi.testclient import TestClient
from models.orders import Beer
from main import app
from services.orders_service import stock, current_order, friends

client = TestClient(app)


class TestOrderAPI(unittest.TestCase):
    def setUp(self):
        """
        Reset data before each test to ensure isolation.
        """
        stock.beers = [
            Beer(name="Corona", price=115, quantity=5),
            Beer(name="Quilmes", price=120, quantity=10),
            Beer(name="Club Colombia", price=110, quantity=8),
        ]

        stock.last_updated = None
        current_order.items = []
        current_order.rounds = []
        current_order.subtotal = 0
        current_order.total = 0
        current_order.paid = False
        friends.clear()

    def test_list_beers(self):
        """
        Test the stock listing endpoint.
        """
        response = client.get("/beers/stock")
        self.assertEqual(response.status_code, 200)
        self.assertIn("beers", response.json())

    def test_place_order(self):
        """
        Test the order placement endpoint.
        """
        order_payload = [
            {"name": "Corona", "quantity": 2, "user": "Tony Stark"},
            {"name": "Quilmes", "quantity": 3, "user": "Peter Parker"},
        ]
        response = client.post("/beers/order", json=order_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(len(current_order.rounds), 1)
        self.assertEqual(len(current_order.items), 2)

    def test_get_bill(self):
        """
        Test the bill retrieval endpoint.
        """
        response = client.get("/beers/bill")
        self.assertEqual(response.status_code, 200)
        self.assertIn("paid", response.json())

    def test_pay_equal(self):
        """
        Test the equal payment endpoint.
        """
        order_payload = [
            {"name": "Corona", "quantity": 2, "user": "Tony Stark"},
            {"name": "Quilmes", "quantity": 3, "user": "Peter Parker"},
        ]
        client.post("/beers/order", json=order_payload)

        # Simular amigos registrados en el sistema
        friends["Tony Stark"] = {"name": "Tony Stark", "balance": 0}
        friends["Peter Parker"] = {"name": "Peter Parker", "balance": 0}

        response = client.put("/beers/pay", json={"mode": "equal"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("remaining_balances", response.json())
        self.assertTrue(current_order.paid)


    def test_pay_individual(self):
        """
        Test the individual payment endpoint.
        """
        order_payload = [
            {"name": "Corona", "quantity": 2, "user": "Tony Stark"},
            {"name": "Quilmes", "quantity": 3, "user": "Peter Parker"},
        ]
        client.post("/beers/order", json=order_payload)

        # Simular amigos registrados en el sistema
        friends["Tony Stark"] = {"name": "Tony Stark", "balance": 0}
        friends["Peter Parker"] = {"name": "Peter Parker", "balance": 0}

        response = client.put(
            "/beers/pay", json={"mode": "individual", "friend": "Tony Stark"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("remaining_balances", response.json())
        self.assertFalse(current_order.paid)


if __name__ == "__main__":
    unittest.main()
