# MVP API для блога (тестовое задание, DRF использовать запрещено)

## Запуск

> Запуск prod версии
> `docker-compose -f docker-compose.prod.yml up -d --build --remove-orphans`
>
> Флаг `-d` можно убрать для запуска не в фоне, так же если нет необходимости,
> можно убрать `--remove-orphans`.

### Описание

> В prod версии порты не проброшены наружу, в отличие от dev - здесь использую
> для локальных тестов.
> Сразу работал с веткой dev, так как один, затем мержил через пул реквест в
> main.
>
> После запуска автоматически создадутся пользователи,
> пароли будут одинаковые, для удобного тестирования: `qwertytwerq`,
> но токены сгенерируются рандомно, пользователи: `admin` (
> админ), `olya`, `ivan`.
> Так же к пользователям рандомно прикрепятся статьи,
> а к статьям рандомные комментарии с рандомными авторами.
> Каждый пользователь получит рандомный токен - можно посмотреть в админ панели.
>
> Задача была реализовать MVP API, по этому не усложнял -
> например не стал, как обычно, создавать и внедрять систему логирования,
> асинхронность, токены не содержат время жизни и другую информацию (нет в
> задаче),
> не делал возможность комментирования комментариев,
> не делал дополнительные обработчики `try` `except` и т.д.
>
> После первого запуска необходимо сменить пароль супер пользователя!
> Либо, для максимальной безопасности, отключить автозаполнение пользователей.
>
> Контейнеры на перезапуске, если не нужно - отключить.
>
> Токен необходимо указывать в заголовке (`headers`) `Authorization` -
> используется для аутентификации пользователя.

## API

### `CRUD` операции со статьями

> Endpoint: http://127.0.0.1/api/articles

#### Методы и права пользователей

> `GET` - Получить все статьи или статью с комментариями по переданному идентификатору в параметре `id`.
>
> `POST` - Создать статью.
> Обязательные поля в теле запроса: `title`, `text`.
> Возвращает сообщение с результатом и описание ошибки (если есть).
>
> `PATCH` - Редактировать статью.
> Обычному пользователю можно редактировать только свои статьи.
> Админу можно редактировать любые статьи.
> В теле запроса необходимо указать поле `title` или `text`.
> Возвращает сообщение с результатом и описание ошибки (если есть).
> 
> `DELETE` - Удалить статью (перенести в архив).
> Обычному пользователю можно удалять только свои статьи.
> Админу можно удалять любые статьи.
> В теле запроса необходимо указать поле `id` - идентификатор статьи.
> Возвращает сообщение с результатом и описание ошибки (если есть).

> Дополнительно возвращают соответсвующее статус-коды и описания статусов.

### Работа с токенами

> Endpoint: http://127.0.0.1/api/token

#### Методы и права пользователей

> `POST` - Создать токен. 
> Генерирует новый токен, в теле запроса необходимо передать `username` и `password`. 
> В случае успешной идентификации пользователя 
> возвращает сообщение с результатом, сгенерированный token` и его `id`. 
> В случае ошибки возвращает её описание.
> 
> `DELETE` - Удалить токен (перенести в архив). 
> Токен должен быть указан в заголовке (`headers`) `Authorization`.
> Обычному пользователю можно удалить только текущий токен - по которому он аутентифицируется.
> Админ может удалить любой токен, для этого нужно передать в теле запроса `token` (токен) или `id` (идентификатор).
> Возвращает результат выполнения и описание ошибки (если есть).

> Дополнительно возвращают соответсвующее статус-коды и описания статусов.

# Задание

Разработать MVP API для блога.

## Описание:

    Система содержит статьи (Articles) комментарии (Comments),  пользователей (Users), 
    а также токены для работы по API (авторизация по Token). 
    В системе должна быть возможность создать User, Token, Comment  (через админку или API). 

### API для CRUD операций:

    1. Получить все статьи
    2. Получить статью с комментариями (по ID)
    3. Создать статью
    4. Изменить статью
    5. Удалить статью (перенести в архив)

### Описание модели User (в Джанго можно использовать стандартную):

    username - ник автора (уникальный)
    is_superuser (boolean) - параметр администратор или нет
    date_joined - дата когда пользователь появился в системе
    is_active (boolean) - параметр для деактивации юзеров
    
    Администратор (is_superuser) имеет доступ ко всем статьям, может изменять/архивировать любую статью. 
    Пользователь - может изменять/архивировать только свои статьи.
    
    Читать статьи, может любой авторизованный и неавторизованный пользователь. 

### Аутентификация

    Работает по токенам (Token).  
    Выданный токен работает до момента пока его не отключат. 
    Несколько токенов у одного пользователя одновременно могут существовать.

### Дополнительно

    1. Упаковать приложение в докер
    2. Написать тесты на ручки
    3. Создать фикстуры или команду для наполнения БД тестовыми данными.
    4. Инструкцию для поднятия системы.

### Что использовать:

    - Бекенд - FastAPI или Django (нельзя использовать DRF)
    - База данных: PostgreSQL
