from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


app = FastAPI()


authors = [
    {"id": 1, "name": "George Orwell"},
    {"id": 2, "name": "Frank Herbert"},
]


books = [
    {"id": 1, "title": "1984", "year": 1949, "author_id": 1},
    {"id": 2, "title": "Dune", "year": 1965, "author_id": 2},
]


class AuthorCreate(BaseModel):
    name: str = Field(min_length=1)


class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)


class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    year: int = Field(ge=1, le=2100)
    author_id: int = Field(gt=0)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    year: Optional[int] = Field(default=None, ge=1, le=2100)
    author_id: Optional[int] = Field(default=None, gt=0)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid input data"},
    )


def get_next_id(items):
    max_id = 0

    for item in items:
        if item["id"] > max_id:
            max_id = item["id"]

    return max_id + 1


def author_exists(author_id: int):
    for author in authors:
        if author["id"] == author_id:
            return True

    return False


@app.get("/authors")
def get_authors():
    return authors


@app.get("/authors/{author_id}")
def get_author(author_id: int):
    for author in authors:
        if author["id"] == author_id:
            return author

    raise HTTPException(status_code=404, detail="Author not found")


@app.post("/authors")
def create_author(author: AuthorCreate):
    new_author = {
        "id": get_next_id(authors),
        "name": author.name,
    }

    authors.append(new_author)

    return new_author


@app.patch("/authors/{author_id}")
def update_author(author_id: int, data: AuthorUpdate):
    if data.name is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    for author in authors:
        if author["id"] == author_id:
            author["name"] = data.name
            return author

    raise HTTPException(status_code=404, detail="Author not found")


@app.delete("/authors/{author_id}", status_code=202)
def delete_author(author_id: int):
    for book in books:
        if book["author_id"] == author_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete author because this author has books",
            )

    for author in authors:
        if author["id"] == author_id:
            authors.remove(author)
            return {"message": "Author deleted"}

    raise HTTPException(status_code=404, detail="Author not found")


@app.get("/books")
def get_books():
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books")
def create_book(book: BookCreate):
    if not author_exists(book.author_id):
        raise HTTPException(status_code=400, detail="Author does not exist")

    new_book = {
        "id": get_next_id(books),
        "title": book.title,
        "year": book.year,
        "author_id": book.author_id,
    }

    books.append(new_book)

    return new_book


@app.patch("/books/{book_id}")
def update_book(book_id: int, data: BookUpdate):
    if data.title is None and data.year is None and data.author_id is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    if data.author_id is not None and not author_exists(data.author_id):
        raise HTTPException(status_code=400, detail="Author does not exist")

    for book in books:
        if book["id"] == book_id:

            if data.title is not None:
                book["title"] = data.title

            if data.year is not None:
                book["year"] = data.year

            if data.author_id is not None:
                book["author_id"] = data.author_id

            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}", status_code=202)
def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {"message": "Book deleted"}

    raise HTTPException(status_code=404, detail="Book not found")
