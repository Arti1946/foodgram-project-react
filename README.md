# foodgram

 # Описание проекта
Данный проект представляет собой блог, который позволяет пользователям создавать свои рецепты, просматривать рецепты других пользователей, добавлть их в избранное или в список покупок, который можно удет скачать. API (интерфейс программирования приложений), предназначенный для работы с моделями данных. Аутентификация осуществляется потокену. 

API позволяет пользователям выполнять следующие действия:

 - просматривать список всех рецептов или создавать новый, а так же изменять/удалять собственные рецепты по их id.
 - просматривать свой профиль пользователя и изменять свой пароль.

Технические детали
 - используется фреймворк Django REST Framework для создания API
 - для работы с базой данных используется СУБД PostgreSQL
 - для аутентификации пользователей используется REST_FRAMEWORK TokenAuthentication
 - для создания и изменения данных в моделях используются сериализаторы
 - для контроля доступа к данным используются права доступа (permissions)

 # Эндпоинты для взаимодействия с ресурсами:
Аутентификация. Пользователь может получить токен, отправив POST-запрос на эндпоинт api/auth/token/login с указанием своей почты и пароля в теле запроса. Токен будет возвращен в ответе на запрос. Для доступа к защищенным ресурсам пользователь

 - api/auth/token/login/ - POST - Аутентификация пользователя по логину и паролю. Допустимый вид запроса POST. Возвращает токен для аутентифицированного пользователя.
 - api/auth/token/logout/ - POST - удаление окена, авторизованного пользователя.
 - api/users/ - GET - получить список всех пользователей, POST - создать нового пользователя.
 - api/users/{id}/ - GET - получить информацию о пользователе с указанным id.
 - api/users/{id}/subscribe/ - POST - подписаться на пользователя с указанным id. DELETE - отписаться от пользователя с указанным id.
 - api/users/subscriprions/ - GET - получить список всех пользователей, на которых подписан текущий пользователь. 
 - api/users/me/ - GET - получить информацию о себе.
 - api/users/set_password/ - POST - изменить пароль своей учетной записи.
 - api/recipes/ - GET - получить список всех рецептов, POST - создать новый рецепт.
 - api/recipes/{id}/ - GET - получить информацию о рецепте с указанным id, PATCH - обновить информацию о рецепте с указанным id, DELETE - удалить рецепт с указанным id.
 - api/recipes/{id}/favorite/ - POST - добавить в избранное рецепт с указанным id, DELETE - удалить из избранного рецепт с указанным id.
 - api/recipes/{id}/shopping_cart/ - POST - добавить в список покупок рецепт с указанным id, DELETE - удалить из списка покупок рецепт с указанным id.
 - api/recipes/download_shopping_cart/ - GET - скачать список покупок. 
 - api/ingredients/ - GET - получить список всех ингредиентов
 - api/ingredients/{id}/ - GET - получить информацию о рецепте с указанным id.
 - api/tags/ - GET - получить список всех тегов
 - api/tags/{id}/ - GET - получить информацию о теге с указанным id

 # Как запустить проект:
1. Клонируйте репозиторий на свой компьютер:
    git clone https://github.com/<username>/<project-name>.git
2. Для запуска проекта в контейнерах введите в терминале находясь в дерриктории проекта:
    docker compose -f docker-compose.yml up -d
8. Теперь можно отправлять запросы к API по адресу http://localhost:8000/

# Доступ к сервису
domen : agfoodgram.ddns.net

