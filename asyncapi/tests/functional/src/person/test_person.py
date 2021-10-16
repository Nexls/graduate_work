async def test_person_list(test_client):
    """Тестирование получения списка персонажей"""

    # Выполнение запроса
    response = await test_client.get('/person/search', params={'page_size': 2, 'page_number': 2})

    # Проверка результата
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_person_search(test_client):
    """Тестирование поиска"""

    # Выполнение запроса
    response = await test_client.get('/person/search', params={'page_size': 50, 'page_number': 1, 'query': 'Nick'})

    # Проверка результата
    assert response.status_code == 200
    assert len(response.json()) == 1

    expected = {
        'uuid': '13096714-19d3-4b07-adad-e14d2dd30657',
        'full_name': 'Nick Cornish',
        'role': 'actor',
        'film_ids': [
            '59844b89-64b1-45eb-b27a-940441c2fb7c'
        ]
    }

    assert expected in response.json()


async def test_person_by_uuid(test_client):
    """Тестирование получения по конкретному UUID"""

    # Выполнение запроса
    response = await test_client.get('/person/04dc23a3-38c2-4135-8394-d731d6a9d655/', params={})

    # Проверка результата
    assert response.status_code == 200

    assert response.json() == {
        'uuid': '04dc23a3-38c2-4135-8394-d731d6a9d655',
        'full_name': 'Richard Arnold',
        'role': 'actor',
        'film_ids': [
            'c62c41c9-3d2f-4e0a-947c-b898cf839f72'
        ]
    }


async def test_person_films(test_client):
    '''
    Тестирование получения списка фильмов.
    Для этого теста нужен индекс фильмов!
    '''

    # Выполнение запроса
    response = await test_client.get('/person/d750da99-d533-4c17-a344-4bcb3a04163b/film/', params={})

    # Проверка результата
    assert response.status_code == 200

    assert response.json() == [{
        'uuid': '649a437c-440f-40e6-bf32-2fdc519baa95',
        'title': 'The Sun Is Also a Star',
        'imdb_rating': 5.8
    }]


async def test_fake_uuid(test_client):
    """Тестирование получения ошибки по фейковому UUID"""

    # Выполнение запроса
    response = await test_client.get('/person/11111111-1111-1111-1111-012345678912/', params={})

    # Проверка результата
    assert response.status_code == 404

    assert response.json() == {'detail': 'person not found'}


async def test_cached(test_client):
    """Тестирование на кэшируемость данных"""

    # Выполнение запроса
    first_response = await test_client.get('/person/1f3d25c0-c303-4f7e-944c-900957271ee6/', params={})

    # Проверка результата
    assert first_response.status_code == 200
    assert first_response.headers['x-cached'] == '0'

    second_response = await test_client.get('/person/1f3d25c0-c303-4f7e-944c-900957271ee6/', params={})

    assert second_response.status_code == 200
    assert second_response.headers['x-cached'] == '1'
