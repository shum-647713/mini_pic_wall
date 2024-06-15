# mini_pic_wall

mini_pic_wall is a small project that demonstrates an example of the architecture and API of a picture posting site

# Setup

### Installation

requirements: git

```
git clone https://github.com/shum-647713/mini_pic_wall
cd mini_pic_wall/
```

### Development

requirements: python (>= 3.10)

```
python -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

For migrating and starting the server you need to provide some environment variables to it.
If you are using `bash` you can make a script that exports them into your shell:

`set_dev_env`:
```
# this file must be used with "source set_dev_env"
# it does NOT work with "bash set_dev_env"
export DEBUG=True
export SECRET_KEY=django-insecure-key
export ALLOWED_HOSTS=*
```

to export environment variables:
```
source set_dev_env
```

to migrate:
```
python manage.py migrate
```

to run the server:
```
python manage.py runserver
```

to check if server is running, try to access http://127.0.0.1:8000/api/

### Production

requirements: docker compose (tested with docker desktop)

create `.env` file with similar content:
```
DEBUG=False
SECRET_KEY=django-insecure-key
ALLOWED_HOSTS=*

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
sudo docker compose up -d --build
sudo docker compose --env-file .env exec web python manage.py migrate
sudo docker compose exec web python manage.py collectstatic
```
if builder fails to download images you may need to do that manually with `docker pull`

to check if server is running, try to access http://127.0.0.1/api/

# API

The actual API uses full links and pagination for lists, but the examples in the table below do not.

Example of a full link: `http://127.0.0.1:8000/api/pictures/1/`

Example of pagination: `{"count": 32, "next": "/link/to/next/page/", "previous": "link/to/previous/page", "results": [object1, object2, ...]}`

| url                                 | method | example                                                                                                                                                                                                            |
| ----------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| /api/users/                         | GET    | `[{"url": "/api/users/user/", "username": "user"}]`                                                                                                                                                                |
| /api/users/                         | POST   | `{"username": "user", "email": "user@example.com", "password": "password"}`                                                                                                                                        |
| /api/users/\<username\>/            | GET    | `{"username": "user", "deactivate": "/api/users/user/deactivate/", "change": "/api/users/user/change/", "pictures": "/api/users/user/pictures/", "collages": "/api/users/user/collages/"}`                         |
| /api/users/\<username\>/deactivate/ | POST   | `{"password": "password"}`                                                                                                                                                                                         |
| /api/users/\<username\>/change/     | POST   | `{"username": "new_name", "email": "new_email@example.com", "password": "new_password", "old_password": "old_password"}`                                                                                           |
| /api/users/\<username\>/pictures/   | GET    | `[{"url": "/api/pictures/1/", "image": "/media/images/hash.png"}]`                                                                                                                                                 |
| /api/users/\<username\>/pictures/   | POST   | Content-Type: image/png                                                                                                                                                                                            |
| /api/users/\<username\>/collages/   | GET    | `[{"url": "/api/collages/1/", "name": "collage_name"}]`                                                                                                                                                            |
| /api/users/\<username\>/collages/   | POST   | `{"name": "collage_name"}`                                                                                                                                                                                         |
| /api/pictures/                      | GET    | `[{"url": "/api/pictures/1/", "image": "/media/images/hash.png"}]`                                                                                                                                                 |
| /api/pictures/\<id\>/               | GET    | `{"image": "/media/images/hash.png", "collages": "/api/pictures/1/collages/", "attach": "/api/pictures/1/attach/", "detach": "/api/pictures/1/detach/", "owner": {"url": "/api/users/user/", "username": "user"}}` |
| /api/pictures/\<id\>/collages/      | GET    | `[{"url": "/api/collages/1/", "name": "collage_name"}]`                                                                                                                                                            |
| /api/pictures/\<id\>/attach/        | GET    | `[{"url": "/api/collages/1/", "name": "collage_name", "attach": "/api/pictures/1/attach/1/"}]`                                                                                                                     |
| /api/pictures/\<id\>/attach/\<id\>/ | POST   |                                                                                                                                                                                                                    |
| /api/pictures/\<id\>/detach/        | GET    | `[{"url": "/api/collages/1/", "name": "collage_name", "detach": "/api/pictures/1/detach/1/"}]`                                                                                                                     |
| /api/pictures/\<id\>/detach/\<id\>/ | POST   |                                                                                                                                                                                                                    |
| /api/collages/                      | GET    | `[{"url": "/api/collages/1/", "name": "collage_name"}]`                                                                                                                                                            |
| /api/collages/\<id\>/               | GET    | `{"name": "collage_name", "pictures": "/api/collages/1/pictures/", "attach": "/api/collages/1/attach/", "detach": "/api/collages/1/detach/", "owner": {"url": "/api/users/user/", "username": "user"}}`            |
| /api/collages/\<id\>/pictures/      | GET    | `[{"url": "/api/pictures/1/", "image": "/media/images/hash.png"}]`                                                                                                                                                 |
| /api/collages/\<id\>/attach/        | GET    | `[{"url": "/api/pictures/1/", "attach": "/api/collages/1/attach/1/"}]`                                                                                                                                             |
| /api/collages/\<id\>/attach/\<id\>/ | POST   |                                                                                                                                                                                                                    |
| /api/collages/\<id\>/detach/        | GET    | `[{"url": "/api/pictures/1/", "detach": "/api/collages/1/detach/1/"}]`                                                                                                                                             |
| /api/collages/\<id\>/detach/\<id\>/ | POST   |                                                                                                                                                                                                                    |
