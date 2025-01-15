import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from services.nyt_service import NYTService

client = TestClient(app)
nyt_service = NYTService()


class TestNYTAPI(unittest.TestCase):
    def setUp(self):
        """
        Reset the cache before each test to ensure isolation.
        """
        nyt_service.reset_books()

    @patch("services.nyt_service.requests.get")
    def test_fetch_genres(self, mock_get):
        """
        Test the /genres endpoint for fetching available genres.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"list_name": "Fiction", "display_name": "Fiction"},
                {"list_name": "Nonfiction", "display_name": "Nonfiction"},
            ]
        }
        mock_get.return_value = mock_response

        response = client.get("/nyt/genres")
        self.assertEqual(response.status_code, 200)
        self.assertIn("genres", response.json())
        self.assertEqual(len(response.json()["genres"]), 2)

    @patch("services.nyt_service.requests.get")
    def test_get_logs(self, mock_get):
        """
        Test the /logs endpoint for retrieving execution logs.
        """
        with open("execution.log", "w") as log_file:
            log_file.write("Log Entry 1\nLog Entry 2\n")

        response = client.get("/nyt/logs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("logs", response.json())
        self.assertGreater(len(response.json()["logs"]), 0)

    def tearDown(self):
        """
        Cleanup after each test.
        """
        nyt_service.reset_books()
        with open("execution.log", "w") as log_file:
            log_file.truncate(0)


if __name__ == "__main__":
    unittest.main()
