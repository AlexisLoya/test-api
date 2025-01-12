from services.nyt_service import NYTService
from services.logs import log_message
from tenacity import retry, stop_after_attempt, wait_fixed

nyt_service = NYTService()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_books_with_retry(genre: str):
    """
    find books with retries.
    """
    try:
        books = nyt_service.fetch_books(genre)
        log_message(f'{len(books)} books for genre "{genre}" processed correctly.')
    except Exception as e:
        log_message(f"Error to fetch books for genre '{genre}': {str(e)}")
        raise
