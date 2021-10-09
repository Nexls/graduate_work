import pytest
from ... import settings


@pytest.mark.asyncio
async def test_person_list(make_get_request):
    '''Тестирование получения списка персонажей'''

    # Выполнение запроса
    response = await make_get_request('/person/search', {'page[size]': 2, 'page[number]': 2})

    # Проверка результата
    assert response.status == 200
    assert len(response.body) == 2


@pytest.mark.asyncio
async def test_person_search(make_get_request):
    '''Тестирование поиска'''

    # Выполнение запроса
    response = await make_get_request('/person/search', {'page[size]': 50, 'page[number]': 1, 'query': 'Nick'})

    # Проверка результата
    assert response.status == 200
    assert len(response.body) == 1

    expected = {
        "uuid": "13096714-19d3-4b07-adad-e14d2dd30657",
        "full_name": "Nick Cornish",
        "role": "actor",
        "film_ids": [
            "59844b89-64b1-45eb-b27a-940441c2fb7c"
        ]
    }

    assert expected in response.body


@pytest.mark.asyncio
async def test_person_by_uuid(make_get_request):
    '''Тестирование получения по конкретному UUID'''

    # Выполнение запроса
    response = await make_get_request('/person/04dc23a3-38c2-4135-8394-d731d6a9d655/', {})

    # Проверка результата
    assert response.status == 200

    assert response.body == {
        "uuid": "04dc23a3-38c2-4135-8394-d731d6a9d655",
        "full_name": "Richard Arnold",
        "role": "actor",
        "film_ids": [
            "c62c41c9-3d2f-4e0a-947c-b898cf839f72"
        ]
    }


@pytest.mark.asyncio
async def test_person_films(make_get_request):
    '''
    Тестирование получения списка фильмов.
    Для этого теста нужен индекс фильмов!
    '''

    # Выполнение запроса
    response = await make_get_request('/person/d750da99-d533-4c17-a344-4bcb3a04163b/film/', {})

    # Проверка результата
    assert response.status == 200

    assert response.body == [{
        "uuid": "649a437c-440f-40e6-bf32-2fdc519baa95",
        "title": "The Sun Is Also a Star",
        "imdb_rating": 5.8
    }]


@pytest.mark.asyncio
async def test_fake_uuid(make_get_request):
    '''Тестирование получения ошибки по фейковому UUID'''

    # Выполнение запроса
    response = await make_get_request('/person/11111111-1111-1111-1111-012345678912/', {})

    # Проверка результата
    assert response.status == 404

    assert response.body == {'detail': 'person not found'}


@pytest.mark.asyncio
async def test_cached(make_get_request):
    '''Тестирование на кэшируемость данных'''

    # Выполнение запроса
    first_response = await make_get_request('/person/1f3d25c0-c303-4f7e-944c-900957271ee6/', {})

    # Проверка результата
    assert first_response.status == 200
    assert first_response.headers['x-cached'] == "0"

    second_response = await make_get_request('/person/1f3d25c0-c303-4f7e-944c-900957271ee6/', {})

    assert second_response.status == 200
    assert second_response.headers['x-cached'] == "1"
