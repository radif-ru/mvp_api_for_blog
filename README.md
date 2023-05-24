# Запуск
> Запуск prod версии `docker-compose -f docker-compose.prod.yml up -d --build --remove-orphans`
> 
> Флаг `-d` можно убрать для запуска не в фоне, так же если нет необходимости, можно убрать `--remove-orphans`.
> 
> После запуска автоматически создадутся пользователи, пароли будут одинаковые, для удобного тестирования: `qwertytwerq`,
> но токены сгенерируются рандомно, пользователи: `admin` (админ), `olya`, `ivan`. 
> Так же к пользователям рандомно прикрепятся статьи, а к статьям рандомные комментарии с рандомными авторами
>
> Задача была реализовать MVP API, по этому не стал усложнять - 
> например не стал, как обычно, создавать и внедрять систему логирования, 
> асинхронность, токены не содержат время жизни и другую информацию (нет в задаче), 
> не делал возможность комментирования комментариев и т.д. 
> В prod версии порты не проброшены наружу, в отличие от dev - здесь использую 
> для локальных тестов. 
> Сразу работал с веткой dev, так как один, затем мержил через пул реквест в main.

> Не понял момент с авторизацией. 
> Достаточно указывать токен в заголовках или же нужно 
> дополнительное `API` для авторизации, где токен помещается например в `Cookies` и дальше 
> можно работать без указания токена в заголовке. 
> Сделал, так, что токен всегда должен быть в заголовке. 
> В задаче не было указано нужно ли делать `API` для регистрации и получения токена, по этому у меня они 
> генерятся автоматом, как и пользователи, в админке можно глянуть какие токены получились для тестирования.

> После первого запуска необходимо сменить пароль супер пользователя! 
> Либо, для максимальной безопасности, отключить автозаполнение пользователей
> 
> Контейнеры на перезапуске, если не нужно - отключить.
> 
> Токен необходимо указывать в заголовке `Authorization`
> 
> `API` для `CRUD` операций тут: http://127.0.0.1/api/articles
> 
> Методы `GET` (все статьи или при передаче параметра `id` - статья и все комментарии к ней), `POST`, `PATCH`, `DELETE`,
> при создании статьи обязательно нужно указать название и текст, удалять и изменять данные можно так, как указано в задаче
>
> Работа с токенами http://127.0.0.1/api/token
> 
> Метод `POST` генерирует новые токен, необходимо передать `username` и `password`, возвращает `token` и его `id`. 
> Метод `DELETE` удаляет (архивирует токен),
> необходимо передать `id` токена, быть авторизованным или владельцем токена или админом

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
