import unittest
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

class TestBeerAPI(unittest.TestCase):
    def test_list_beers(self):
        response = client.get("/stock")
        self.assertEqual(response.status_code, 200)
        self.assertIn("beers", response.json())

    def test_place_order(self):
        response = client.post("/order", params={"name": "Corona", "quantity": 2})
        self.assertEqual(response.status_code, 200)
        self.assertIn("order", response.json())

    def test_pay_equal(self):
        client.post("/order", json={"name": "Corona", "quantity": 2})
        response = client.put("/pay", json={"mode": "equal"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("remaining_balances", response.json())

    def test_pay_individual(self):
        client.post("/order", json={"name": "Corona", "quantity": 2})
        response = client.put("/pay", json={"mode": "individual", "friend_name": "Tony Stark"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("remaining_balances", response.json())

if __name__ == "__main__":
    unittest.main()