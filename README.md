# Foodgram
Cервис для публикаций и обмена рецептами.
Авторизованные пользователи могут подписываться на понравившихся авторов, добавлять рецепты в избранное, в покупки, скачивать список покупок. Неавторизованным пользователям доступна регистрация, авторизация, просмотр рецептов других пользователей.

### Настройка проекта
1. Запустите docker compose:
```bash
docker-compose up -d
```
2. Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```
3. Создайте администратора:
```bash
docker-compose exec backend python manage.py createsuperuser
```
4. Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic
```
## Сайт
Сайт доступен по ссылке:
http://178.154.193.114


## Автор
- [Yasin Abdurakhmanov](https://github.com/yanoben)
