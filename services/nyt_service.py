import os
import requests
from services.logs import log_message
from models.nyt import BookResponse
from dotenv import load_dotenv

load_dotenv()

class NYTService:
    BASE_URL = "https://api.nytimes.com/svc/books/v3"
    API_KEY = os.getenv("NYT_API_KEY")
    
    books_cache = set()

    def fetch_books(self, genre: str):
        """
        Busca libros del NYT según el género.
        """
        url = f"{self.BASE_URL}/lists/current/{genre}.json"
        params = {"api-key": self.API_KEY}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            log_message(f'Error to find books: {response.status_code}')
            response.raise_for_status()

        data = response.json()
        books = data.get("results", {}).get("books", [])
        log_message(f'Books found for genre "{genre}": {len(data.get("results", {}).get("books", []))}')
        for book in books:
            self.books_cache.add(BookResponse(
                book_uri=book.get("book_uri"),
                rank=book.get("rank"),
                title=book.get("title"),
                author=book.get("author"),
                description=book.get("description"),
                amazon_url=book.get("amazon_product_url")
            ))
        return books

    def reset_books(self):
        """
        Clean the state in memory.
        """
        log_message("Reset books found")
        self.books_cache = []

    def get_cached_books(self):
        """
        Returns the books saved.
        """
        return self.books_cache