import pytest
from ... import settings


@pytest.mark.asyncio
async def test_genge_list(make_get_request):
    '''Тестирование получения списка жанров'''

    # Выполнение запроса
    response = await make_get_request('/genre/', {})

    # Проверка результата
    assert response.status == 200
    assert len(response.body) == 26

    assert {'name': 'Fantasy', 'uuid': '47392fcb-82e5-4ca3-b01f-aaa9cb96d2a2'} in response.body


@pytest.mark.asyncio
async def test_genge_by_uuid(make_get_request):
    '''Тестирование получения жанра по конкретному UUID'''

    # Выполнение запроса
    response = await make_get_request('/genre/933d0c17-2209-4b17-a3ec-a7d919768cc9/', {})

    # Проверка результата
    assert response.status == 200

    assert response.body == {"uuid": "933d0c17-2209-4b17-a3ec-a7d919768cc9", "name": "Comedy"}


@pytest.mark.asyncio
async def test_fake_uuid(make_get_request):
    '''Тестирование получения ошибки по фейковому UUID'''

    # Выполнение запроса
    response = await make_get_request('/genre/11111111-1111-1111-1111-012345678912/', {})

    # Проверка результата
    assert response.status == 404

    assert response.body == {'detail': 'Genre not found'}


@pytest.mark.asyncio
async def test_cached(make_get_request):
    '''Тестирование на кэшируемость данных'''

    # Выполнение запроса
    first_response = await make_get_request('/genre/72f42752-d389-4ef2-b62f-1f5e84abdfe0/', {})

    # Проверка результата
    assert first_response.status == 200
    assert first_response.headers['x-cached'] == "0"

    second_response = await make_get_request('/genre/72f42752-d389-4ef2-b62f-1f5e84abdfe0/', {})

    assert second_response.status == 200
    assert second_response.headers['x-cached'] == "1"
