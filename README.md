# Voice Assistant

Привет! \
Сейчас отправляем на ревью в довольно сыром виде, т.к. с переносом на fastapi всплыли ошибки с другими сервисами, \
а свободного времени оказалось меньше, чем хотелось бы.

По этой же причине сейчас не разделена бизнес-логика обработки запросов Алисы и техническая часть (получение данных).

## Запуск
В консоли выполнить команду `docker-compose up`

Список запускаемых сервисов
- http://localhost:8000/ - Gate
- http://localhost:8001/api/docs/ - Asyncapi
- http://localhost:8002/api/docs/ - Authapi
- http://localhost:8003/api/docs/ - Voice assistant api
- http://localhost:5432/ - PostgreSQL
- http://localhost:6379/ - Redis
- http://localhost:9200/ - ElasticSearch
- http://localhost:5601/ - Kibana


### Как обрабатываем запросы от Алисы:
Взаимодействие основано на паттерне **state machine**. \
Это значит, что мы обрабатываем запрос пользователя в зависимости от *сцены* (состояния) в котором он находится.

Всего реализовано 5 сцен:
1. Welcome
2. Top Films
3. Film Info
4. Person Info
5. Helper

При старте пользователь попадает на сцену Welcome, тут он получает краткую справку о том, что это за навык.\
Затем пользователь задает вопрос сервису.\

Чтобы понять, что хочет пользователь, мы выделяем из запроса по "намерение" - **интент**.

Если мы распознали интент, то возвращаем ответ, вместе с этим переводя пользователя на одну из трех сцен: \
Top Films / Film Info / Person Info

Находясь на одной из этих сцен, пользователь может задать вопрос, связанный с предыдущим ответом.

Например:
- Кто автор фильма Дюна?
- Ответ: Дени Вильнёв *(пользователь попадает на сцену Person Info)*
- Сколько ему лет?
- Ответ: 54

При этом один, и тот же интент, полученный из разных сцен может быть обработан по-разному. \
Например, находясь на сцене Film Info, запрос "расскажи подробнее" вернет подробную информацию о фильме. \
Но тот же запрос со сцены Person Info вернет информацию о человеке. 

#### Приоритет обработки интента
1. Проверяется, возможна ли локальная обработка интента (в рамках текущей Сцена)
2. Затем проверяется есть ли обработка среди остальных сцен
3. При неудаче срабатывает функция fallback, которая просит пользователя сформулировать вопрос иначе. \
   При этом все нераспознанные запросы сохраняются для дальнейшего анализа.

Также пользователь может в любой момент попросить помощи в использовании навыка. \
Тогда вызывается сцена Help - она предлагает примеры запросов к сервису.

###Список возможных интентов по группам

#### Топ фильмов
- Топ по дате
- Топ по типу
- Топ по жанру

#### Информация о фильме
- Описание фильма
- Актеры фильма 
- Автор фильма
- Длительность фильма
- Жанр фильма
- Рейтинг фильма
- Дата выхода

#### Информация о персоне
- Возраст человека
- Фильмы с участием
- Биография человека


