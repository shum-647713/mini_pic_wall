# mini_pic_wall

mini_pic_wall is a small project that demonstrates an example of a picture posting site API using **Django**, **Django Rest Framework**, **Celery** (with **Redis** as broker), **Docker**, **Docker Compose**, **PostgreSQL**, **Nginx**

# Setup

### Installation

requirements: git

```
git clone https://github.com/shum-647713/mini_pic_wall
cd mini_pic_wall/
```

### Development

requirements: docker compose (tested with docker desktop)

to start server for development:
```
sudo docker compose up -d --build
```
if builder fails to download images you may need to do that manually using `docker pull`

to check if server is running, try to access http://127.0.0.1/api/

### Production

requirements: docker compose (tested with docker desktop)

create `prod.env` file with similar content:
```
DEBUG=false
SECRET_KEY=django-insecure-key
ALLOWED_HOSTS=*

CELERY_BROKER=redis://redis:6379/0

DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_NAME=database_name
DJANGO_DB_USER=username
DJANGO_DB_PASSWORD=password
DJANGO_DB_HOST=postgres
DJANGO_DB_PORT=5432

POSTGRES_DB=database_name
POSTGRES_USER=username
POSTGRES_PASSWORD=password
```

to build and run in production:
```
sudo docker compose -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.prod.yml --env-file prod.env exec web python manage.py migrate
sudo docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic
```
if builder fails to download images you may need to do that manually using `docker pull`

to check if server is running, try to access http://127.0.0.1/api/

# API

The actual API uses full links and pagination for lists, but the examples in the table below do not.

Example of a full link: `http://127.0.0.1:8000/api/pictures/1/`

Example of pagination: `{"count": 32, "next": "/link/to/next/page/", "previous": "link/to/previous/page", "results": [object1, object2, ...]}`

| url                                 | method | example                                                                                                                                                                                                                                                                               |
| ----------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| /api/users/                         | GET    | `[{"url": "/api/users/user/", "username": "user"}]`                                                                                                                                                                                                                                   |
| /api/users/                         | POST   | `{"username": "user", "email": "user@example.com", "password": "password"}`                                                                                                                                                                                                           |
| /api/users/\<username\>/            | GET    | `{"username": "user", "deactivate": "/api/users/user/deactivate/", "change": "/api/users/user/change/", "pictures": "/api/users/user/pictures/", "collages": "/api/users/user/collages/"}`                                                                                            |
| /api/users/\<username\>/deactivate/ | POST   | `{"password": "password"}`                                                                                                                                                                                                                                                            |
| /api/users/\<username\>/change/     | POST   | `{"username": "new_name", "email": "new_email@example.com", "password": "new_password", "old_password": "old_password"}`                                                                                                                                                              |
| /api/users/\<username\>/pictures/   | GET    | `[{"url": "/api/pictures/1/", "name": "picture_name", "thumbnail": "/media/thumbnails/hash.png"}]`                                                                                                                                                                                    |
| /api/users/\<username\>/pictures/   | POST   | as form-data only: `name: picture_name --- image: Content-Type: image/png`                                                                                                                                                                                                            |
| /api/users/\<username\>/collages/   | GET    | `[{"url": "/api/collages/1/", "name": "collage_name"}]`                                                                                                                                                                                                                               |
| /api/users/\<username\>/collages/   | POST   | `{"name": "collage_name"}`                                                                                                                                                                                                                                                            |
| /api/pictures/                      | GET    | `[{"url": "/api/pictures/1/", "name": "picture_name", "thumbnail": "/media/thumbnails/hash.png"}]`                                                                                                                                                                                    |
| /api/pictures/\<id\>/               | GET    | `{"name": "picture_name", "image": "/media/images/hash.png", "thumbnail": "/media/thumbnails/hash.png", "collages": "/api/pictures/1/collages/", "attach": "/api/pictures/1/attach/", "detach": "/api/pictures/1/detach/", "owner": {"url": "/api/users/user/", "username": "user"}}` |
| /api/pictures/\<id\>/               | DELETE |                                                                                                                                                                                                                                                                                       |
| /api/pictures/\<id\>/collages/      | GET    | `[{"url": "/api/collages/1/", "name": "collage_name"}]`                                                                                                                                                                                                                               |
| /api/collages/                      | GET    | `[{"url": "/api/collages/1/", "name": "collage_name"}]`                                                                                                                                                                                                                               |
| /api/collages/\<id\>/               | GET    | `{"name": "collage_name", "pictures": "/api/collages/1/pictures/", "attach": "/api/collages/1/attach/", "detach": "/api/collages/1/detach/", "owner": {"url": "/api/users/user/", "username": "user"}}`                                                                               |
| /api/collages/\<id\>/               | DELETE |                                                                                                                                                                                                                                                                                       |
| /api/collages/\<id\>/pictures/      | GET    | `[{"url": "/api/pictures/1/", "name": "picture_name", "thumbnail": "/media/thumbnails/hash.png"}]`                                                                                                                                                                                    |
| /api/collages/\<id\>/attach/        | GET    | `[{"url": "/api/pictures/1/", "name": "picture_name", "thumbnail": "/media/thumbnails/hash.png", "attach": "/api/collages/1/attach/1/"}]`                                                                                                                                             |
| /api/collages/\<id\>/attach/\<id\>/ | POST   |                                                                                                                                                                                                                                                                                       |
| /api/collages/\<id\>/detach/        | GET    | `[{"url": "/api/pictures/1/", "name": "picture_name", "thumbnail": "/media/thumbnails/hash.png", "detach": "/api/collages/1/detach/1/"}]`                                                                                                                                             |
| /api/collages/\<id\>/detach/\<id\>/ | POST   |                                                                                                                                                                                                                                                                                       |
