from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.nyt import NYTBookFilter
from services.nyt_service import NYTService
from tasks.background_tasks import fetch_books_with_retry

router = APIRouter()

nyt_service = NYTService()

@router.post("/books")
def get_books(filter: NYTBookFilter, background_tasks: BackgroundTasks):
    """
    Endpoint to search for books by genre in the NYT.
    """
    
    try:
        background_tasks.add_task(fetch_books_with_retry, filter.genre)
        return {"message": "Fetching books in the background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching books: {str(e)}")

@router.get("/books")
def view_cached_books():
    """
    Returns the books stored.
    """
    books = nyt_service.get_cached_books()
    if not books:
        return {"message": "No books found"}
    return {"books": books}

@router.delete("/books/reset")
def reset_cached_books():
    """
    Reset the books stored.
    """
    nyt_service.reset_books()
    return {"message": "Books cache reset successfully."}


@router.get("/logs")
def get_logs():
    """
    Returns the logs of the application.
    """
    try:
        with open("execution.log", "r") as log_file:
            logs = log_file.readlines()
        return {"logs": logs}
    except FileNotFoundError:
        return {"logs": "No logs found"}
