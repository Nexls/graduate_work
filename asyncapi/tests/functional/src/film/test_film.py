async def test_film_list(
    test_client
) -> None:
    """Тестирование получения списка фильмов"""
    # Выполнение запроса
    response = await test_client.get('/film', params={'page_size': 2, 'page_number': 2})

    # Проверка результата
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_film_filter(
    test_client
) -> None:
    """Тестирование получения списка фильмов"""

    # Выполнение запроса
    response = await test_client.get(
        '/film',
        params={
            'page_size': 50,
            'page_number': 1,
            'filter[genre]': '47392fcb-82e5-4ca3-b01f-aaa9cb96d2a2'
        }
    )

    # Проверка результата
    assert response.status_code == 200
    assert len(response.json()) == 12


async def test_film_sort(test_client):
    """Тестирование получения списка фильмов"""

    # Выполнение запроса
    response = await test_client.get(
        '/film',
        params={
            'page_size': 5,
            'page_number': 1,
            'sort': '-imdb_rating'
        }
    )

    # Проверка результата
    assert response.status_code == 200
    assert response.json()[0] == {
        "uuid": "5f67aeb2-f87c-4c39-ba2e-fba38fa21f3c",
        "title": "Star Wars: Knights of the Old Republic II - The Sith Lords",
        "imdb_rating": 8.9
    }


async def test_film_search(test_client):
    """Тестирование поиска"""

    # Выполнение запроса
    response = await test_client.get('/film/search', params={'page_size': 50, 'page_number': 1, 'query': 'camp'})

    # Проверка результата
    assert response.status_code == 200
    assert len(response.json()) == 1

    assert response.json() == [
        {
            "uuid": "5215a2eb-d3d8-4602-beed-58193a08ce5c",
            "title": "My Love from Another Star",
            "imdb_rating": 8.3
        }
    ]


async def test_film_by_uuid(test_client):
    '''Тестирование получения по конкретному UUID'''

    # Выполнение запроса
    response = await test_client.get('/film/273de788-81be-4460-9ca2-37f8635dcfd7/', params={})

    # Проверка результата
    assert response.status_code == 200

    assert response.json() == {
        "uuid": "273de788-81be-4460-9ca2-37f8635dcfd7",
        "title": "Star Wars: Episode IV - A New Hope",
        "imdb_rating": 8.6,
        "description": "The Imperial Forces, under orders from cruel Darth Vader, "
                       "hold Princess Leia hostage in their efforts to quell the "
                       "rebellion against the Galactic Empire. Luke Skywalker and Han Solo, "
                       "captain of the Millennium Falcon, work together with the companionable "
                       "droid duo R2-D2 and C-3PO to rescue the beautiful princess, help the "
                       "Rebel Alliance and restore freedom and justice to the Galaxy.",
        "genre": [
            {
                "uuid": "47392fcb-82e5-4ca3-b01f-aaa9cb96d2a2",
                "name": "Action"
            },
            {
                "uuid": "61807c42-0f8f-417b-bb28-32e1fb7e370c",
                "name": "Adventure"
            },
            {
                "uuid": "8197e9ab-3869-4f18-b178-a1d297a4db8a",
                "name": "Fantasy"
            },
            {
                "uuid": "8301bd05-5052-4ee3-9e53-b907b160c2d7",
                "name": "Sci-Fi"
            }
        ],
        "actors": [
            {
                "uuid": "ba2fbd08-691e-47b2-b0de-dc34f8c718a9",
                "full_name": "Mark Hamill"
            },
            {
                "uuid": "b3916c46-28ca-4dc9-a56a-f313a44e2acd",
                "full_name": "Harrison Ford"
            },
            {
                "uuid": "5a8edb9d-ca8f-4cef-89d4-bdd231667012",
                "full_name": "Peter Cushing"
            },
            {
                "uuid": "61fb7c17-7161-411b-af40-c5ae2f352822",
                "full_name": "Carrie Fisher"
            }
        ],
        "writers": [
            {
                "uuid": "148e753d-bba8-4ab0-a738-0411abc825ec",
                "full_name": "George Lucas"
            }
        ],
        "directors": [
            {
                "uuid": "148e753d-bba8-4ab0-a738-0411abc825ec",
                "full_name": "George Lucas"
            }
        ]
    }


async def test_fake_uuid(test_client):
    """Тестирование получения ошибки по фейковому UUID"""

    # Выполнение запроса
    response = await test_client.get('/film/11111111-1111-1111-1111-012345678912/', params={})

    # Проверка результата
    assert response.status_code == 404

    assert response.json() == {'detail': 'film not found'}


async def test_cached(test_client):
    """Тестирование на кэшируемость данных"""

    # Выполнение запроса
    first_response = await test_client.get('/film/2907029a-68d5-48af-8855-7de80101ee42/', params={})

    # Проверка результата
    assert first_response.status_code == 200
    assert first_response.headers['x-cached'] == "0"

    second_response = await test_client.get('/film/2907029a-68d5-48af-8855-7de80101ee42/', params={})

    assert second_response.status_code == 200
    assert second_response.headers['x-cached'] == "1"
