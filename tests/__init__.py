import pytest
from services.nyt_service import NYTService

nyt_service = NYTService()

def test_fetch_books(mocker):
    mock_response = {
        "results": {
            "books": [
                {"book_uri": "nyt://book/1", "rank": 1, "title": "Book 1", "author": "Author 1", "description": "Desc 1", "amazon_product_url": "url1"},
                {"book_uri": "nyt://book/2", "rank": 2, "title": "Book 2", "author": "Author 2", "description": "Desc 2", "amazon_product_url": "url2"},
            ]
        }
    }

    mocker.patch("requests.get", return_value=MockResponse(mock_response, 200))
    books = nyt_service.fetch_books("fiction")
    assert len(books) == 2

def test_reset_books():
    nyt_service.books_cache = {"nyt://book/1"}
    nyt_service.reset_books()
    assert len(nyt_service.books_cache) == 0
