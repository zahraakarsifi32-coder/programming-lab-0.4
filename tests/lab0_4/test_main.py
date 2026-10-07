import pytest
from fastapi.testclient import TestClient

from src.lab0_4.main import app, authors, books


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_data():
    authors[:] = [
        {"id": 1, "name": "George Orwell"},
        {"id": 2, "name": "Frank Herbert"},
    ]

    books[:] = [
        {"id": 1, "title": "1984", "year": 1949, "author_id": 1},
        {"id": 2, "title": "Dune", "year": 1965, "author_id": 2},
    ]


def test_get_books():
    response = client.get("/books")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_one_book():
    response = client.get("/books/1")

    assert response.status_code == 200
    assert response.json()["title"] == "1984"


def test_book_not_found():
    response = client.get("/books/999")

    assert response.status_code == 404


def test_create_book():
    response = client.post(
        "/books",
        json={
            "title": "Animal Farm",
            "year": 1945,
            "author_id": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Animal Farm"


def test_invalid_book_data():
    response = client.post(
        "/books",
        json={
            "title": "Future Book",
            "year": 5000,
            "author_id": 1,
        },
    )

    assert response.status_code == 400


def test_update_book():
    response = client.patch(
        "/books/2",
        json={"year": 1966},
    )

    assert response.status_code == 200
    assert response.json()["year"] == 1966


def test_delete_book():
    response = client.delete("/books/2")

    assert response.status_code == 202
    assert len(books) == 1


def test_get_authors():
    response = client.get("/authors")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_create_author():
    response = client.post(
        "/authors",
        json={"name": "J. K. Rowling"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "J. K. Rowling"


def test_update_author():
    response = client.patch(
        "/authors/1",
        json={"name": "Orwell"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Orwell"


def test_delete_unused_author():
    client.post(
        "/authors",
        json={"name": "Unused Author"},
    )

    response = client.delete("/authors/3")

    assert response.status_code == 202


def test_cannot_delete_author_with_books():
    response = client.delete("/authors/1")

    assert response.status_code == 400
