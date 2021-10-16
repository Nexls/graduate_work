async def test_genge_list(test_client):
    """Тестирование получения списка жанров"""

    # Выполнение запроса
    response = await test_client.get('/genre/', params={})

    # Проверка результата
    assert response.status_code == 200
    assert len(response.json()) == 26

    assert {'name': 'Fantasy', 'uuid': '47392fcb-82e5-4ca3-b01f-aaa9cb96d2a2'} in response.json()


async def test_genge_by_uuid(test_client):
    """Тестирование получения жанра по конкретному UUID"""

    # Выполнение запроса
    response = await test_client.get('/genre/933d0c17-2209-4b17-a3ec-a7d919768cc9/', params={})

    # Проверка результата
    assert response.status_code == 200

    assert response.json() == {'uuid': '933d0c17-2209-4b17-a3ec-a7d919768cc9', 'name': 'Comedy'}


async def test_fake_uuid(test_client):
    """Тестирование получения ошибки по фейковому UUID"""

    # Выполнение запроса
    response = await test_client.get('/genre/11111111-1111-1111-1111-012345678912/', params={})

    # Проверка результата
    assert response.status_code == 404

    assert response.json() == {'detail': 'Genre not found'}


async def test_cached(test_client):
    """Тестирование на кэшируемость данных"""

    # Выполнение запроса
    first_response = await test_client.get('/genre/72f42752-d389-4ef2-b62f-1f5e84abdfe0/', params={})

    # Проверка результата
    assert first_response.status_code == 200
    assert first_response.headers['x-cached'] == '0'

    second_response = await test_client.get('/genre/72f42752-d389-4ef2-b62f-1f5e84abdfe0/', params={})

    assert second_response.status_code == 200
    assert second_response.headers['x-cached'] == '1'
