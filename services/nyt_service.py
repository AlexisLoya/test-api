import os
import requests
from dotenv import load_dotenv
from services.logs import log_message
from models.nyt import BookResponse

load_dotenv()

class NYTService:
    BASE_URL = "https://api.nytimes.com/svc/books/v3"
    API_KEY = os.getenv("NYT_API_KEY")
    books_cache = set()
    genres_cache = []

    def fetch_books(self, genre: str):
        """
        Fetch books by genre from NYT.
        """
        url = f"{self.BASE_URL}/lists/current/{genre}.json"
        params = {"api-key": self.API_KEY}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            log_message(f"Error fetching books: {response.status_code}")
            response.raise_for_status()

        books = response.json().get("results", {}).get("books", [])
        log_message(f"Books found for genre '{genre}': {len(books)}")

        for book in books:
            self.books_cache.add(BookResponse(
                book_uri=book.get("book_uri"),
                rank=book.get("rank"),
                title=book.get("title"),
                author=book.get("author"),
                description=book.get("description"),
                amazon_url=book.get("amazon_product_url"),
            ))

        return list(self.books_cache)

    def fetch_genres(self):
        """
        Fetch genres from NYT.
        """
        url = f"{self.BASE_URL}/lists/names.json"
        params = {"api-key": self.API_KEY}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            log_message(f"Error fetching genres: {response.status_code}")
            response.raise_for_status()

        genres = response.json().get("results", [])
        log_message(f"Genres fetched: {len(genres)}")

        self.genres_cache = genres
        return genres

    def reset_books(self):
        """
        Clear cached books.
        """
        self.books_cache.clear()
        log_message("Books cache reset.")

    def get_cached_books(self):
        """
        Return cached books as a list.
        """
        return list(self.books_cache)
