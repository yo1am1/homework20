import json
import pathlib

import responses

import pytest
import requests

from django.test import RequestFactory

from django.test import Client
from django.urls import reverse

from book_shelf import views

root = pathlib.Path(__file__).parent


@pytest.fixture
def mocked():
    def inner(file_name):
        return json.load(open(root / "fixtures" / file_name))

    return inner


@pytest.fixture
def rf():
    return RequestFactory()


def test_urls_output(mocked):
    mocked_data = mocked("urls_get_test.json")
    body = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/"
    ).json()

    assert body == mocked_data


@responses.activate
def test_index_view(rf):
    url = reverse("books_info_or_add")
    request = rf.post(url)
    response = views.BookView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_connection_to_books_list():
    client = Client()
    response = client.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/"
    )

    assert response.status_code == 200


def test_get_book_exists(mocked):
    mocked_data = mocked("get_book.json")
    body = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/1"
    ).json()

    assert body == mocked_data


def test_get_book_not_exist(mocked):
    mocked_data = mocked("book_not_exist.json")
    body = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/0"
    ).json()

    assert body == mocked_data


@pytest.mark.django_db
def test_book_remove_not_exist(mocked):
    mocked_data = mocked("remove_book_not_exist.json")
    body = requests.delete(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/3"
    ).json()

    assert body == mocked_data


@pytest.mark.django_db
def test_connection_to_authors_list():
    client = Client()
    response = client.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/authors/"
    )

    assert response.status_code == 200


def test_get_author_list(mocked):
    mocked_data = mocked("get_authors.json")
    body = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/authors/"
    ).json()

    assert body == mocked_data


def test_get_author(mocked):
    mocked_data = mocked("get_author.json")
    body = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/authors/2"
    ).json()

    assert body == mocked_data


@pytest.mark.django_db
def test_books_post():
    client = Client()
    body = {
        "title": "Not a Divine comedy",
        "publish_year": 20235,
        "author": "Dante Alighieri",
        "genre": "comedy",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/",
        data=json_body,
        content_type="application/json",
    )
    response_body = response.json()

    expected_response = {
        "author": "Dante Alighieri",
        "genre": "comedy",
        "id": 1,
        "publish_year": 20235,
        "title": "Not a Divine comedy",
    }

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_missing_input():
    client = Client()
    body = {
        "title": "The comedy of mine",
        "publish_year": 2023,
        "author": "Viktor",
    }
    json_body = json.dumps(body, indent=4)
    response = client.post(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/",
        data=json_body,
        content_type="application/json",
    )
    response_body = response.json()

    expected_response = {
        "fields": {"1": "title", "2": "publish_year", "3": "author", "4": "genre"},
        "message": "Missing data field. Please, check your input",
        "status": 400,
    }

    assert response_body == expected_response


def test_authors_get_id(mocked):
    mocked_data = mocked("get_author.json")
    body = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/authors/2"
    ).json()

    assert body == mocked_data


@pytest.mark.django_db
def test_book_filter_author(mocked):
    body = {"author": "Me"}
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = [
        {
            "fields": {
                "author": "(<Author: Me>, False)",
                "genre": "tragedy",
                "publish_year": 20235,
                "title": "Foo 2",
            },
            "model": "shelf.book",
            "pk": 5,
        },
        {
            "fields": {
                "author": "Me",
                "genre": "comedy? tragedy...",
                "publish_year": 2023,
                "title": "Foo",
            },
            "model": "shelf.book",
            "pk": 1,
        },
    ]

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_filter_genre(mocked):
    body = {"genre": "comedy"}
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = [
        {
            "fields": {
                "author": "(<Author: Dante Alighieri>, True)",
                "genre": "comedy",
                "publish_year": 20235,
                "title": "Divine",
            },
            "model": "shelf.book",
            "pk": 2,
        },
        {
            "fields": {
                "author": "Me",
                "genre": "comedy? tragedy...",
                "publish_year": 2023,
                "title": "Foo",
            },
            "model": "shelf.book",
            "pk": 1,
        },
    ]

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_filter_title(mocked):
    body = {"title": "Foo"}
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = [
        {
            "fields": {
                "author": "(<Author: Me>, False)",
                "genre": "tragedy",
                "publish_year": 20235,
                "title": "Foo 2",
            },
            "model": "shelf.book",
            "pk": 5,
        },
        {
            "fields": {
                "author": "Me",
                "genre": "comedy? tragedy...",
                "publish_year": 2023,
                "title": "Foo",
            },
            "model": "shelf.book",
            "pk": 1,
        },
    ]

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_filter_publish_year(mocked):
    body = {"publish_year": 2023}
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = [
        {
            "fields": {
                "author": "(<Author: Me>, False)",
                "genre": "tragedy",
                "publish_year": 20235,
                "title": "Foo 2",
            },
            "model": "shelf.book",
            "pk": 5,
        },
        {
            "fields": {
                "author": "(<Author: Dante Alighieri>, True)",
                "genre": "comedy",
                "publish_year": 20235,
                "title": "Divine",
            },
            "model": "shelf.book",
            "pk": 2,
        },
        {
            "fields": {
                "author": "Me",
                "genre": "comedy? tragedy...",
                "publish_year": 2023,
                "title": "Foo",
            },
            "model": "shelf.book",
            "pk": 1,
        },
    ]

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_filter_all(mocked):
    body = {"author": "Me", "genre": "comedy", "title": "Foo", "publish_year": 2023}
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = [
        {
            "fields": {
                "author": "(<Author: Me>, False)",
                "genre": "tragedy",
                "publish_year": 20235,
                "title": "Foo 2",
            },
            "model": "shelf.book",
            "pk": 5,
        },
        {
            "fields": {
                "author": "Me",
                "genre": "comedy? tragedy...",
                "publish_year": 2023,
                "title": "Foo",
            },
            "model": "shelf.book",
            "pk": 1,
        },
    ]

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_filter_empty(mocked):
    body = {}
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = {
        "fields": {"1": "title", "2": "author", "3": "publish_year", "4": "genre"},
        "message": "Missing data field. Please, check your input",
        "status": 400,
    }

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_filter_invalid(mocked):
    body = {
        "foo": "bar",
    }
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = {
        "fields": {"1": "title", "2": "author", "3": "publish_year", "4": "genre"},
        "message": "Missing data field. Please, check your input",
        "status": 400,
    }

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_filter_not_found(mocked):
    body = {"author": "bar"}
    json_body = json.dumps(body, indent=4)
    response = requests.get(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/filter/",
        data=json_body,
    )
    response_body = response.json()

    expected_response = {"message": "No books found", "status": 404}

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_put_method(mocked):
    body = {"author": "try"}
    json_body = json.dumps(body, indent=4)
    response = requests.put(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/1",
        data=json_body,
    )
    response_body = response.json()

    expected_response = {
        "book": '[{    "model": "shelf.book",    "pk": 1,    "fields": {        '
        '"title": "Foo",        "publish_year": 2023,        "author": '
        '"try",        "genre": "comedy? tragedy..."    }}]',
        "message": "Book 'Foo' has been updated",
        "status": 200,
        "updated_fields": ["author"],
    }

    assert response_body == expected_response


@pytest.mark.django_db
def test_book_put_method_already_used(mocked):
    body = {"author": "Me"}
    json_body = json.dumps(body, indent=4)
    response = requests.put(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/1",
        data=json_body,
    )
    response = requests.put(
        "https://boiling-dusk-49835-df388a71925c.herokuapp.com/api/books/1",
        data=json_body,
    )

    response_body = response.json()
    expected_response = {"message": "No fields were updated", "status": 200}

    assert response_body == expected_response


if __name__ == "__main__":
    pytest.main()
