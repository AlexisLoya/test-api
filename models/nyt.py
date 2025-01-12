from pydantic import BaseModel

class NYTBookFilter(BaseModel):
    genre: str

class BookResponse(BaseModel):
    book_uri: str
    rank: int
    title: str
    author: str
    description: str
    amazon_url: str


    def __hash__(self):
        return hash((self.book_uri))

    def __eq__(self, other):
        if isinstance(other, BookResponse):
            return (self.book_uri) == (other.book_uri)
        return False
