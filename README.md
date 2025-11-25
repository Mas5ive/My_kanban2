# My-kanban2

[![Django Tests](https://github.com/Mas5ive/My_kanban2/actions/workflows/check.yml/badge.svg)](https://github.com/Mas5ive/My_kanban2/actions/workflows/check.yml)

## Description

A simple multi-user kanban application written on the Django 4.2 web framework + Django Ninja 1.4. This is a demonstration project, not intended to be deployed on a server.

### Available features

- signup is available via github
- login via email
- reset password
- create Kanban boards
- different functionality depending on the user's relationship to the board
- invite/exclude other users to your projects
- create/edit/move/delete task cards
- comment on cards and attach files

### Technical features

- docker
- uv
- nginx
- postgres
- redis
- the frontend is written in vanilla JavaScript
- tests cover a small portion of the code intentionally

## Installation

```bash
git clone https://github.com/Mas5ive/My_kanban2.git
```

```bash
cd My_kanban2/
```

Create your own **.env** file based on **.env.example**. Leave the commented lines as they are for now.

### OAuth2 via Github (optional)

 To try out github login, you need to create a github app in your developer settings.

- Specify values in the following fields:
  - Homepage URL: <https://127.0.0.1>
  - Authorization callback URL: <https://127.0.0.1/complete/github/>
- Generate the keys and paste them into the appropriate lines in the **.env** file

## Demo mode

### Run

```bash
docker compose -f docker-compose.yml up --build
```

On your localhost on port **80** the application will become available after some time...

This example creates 3 users with the same passwords (321qwe,./):

| User      | Email                 |
|-----------|-----------------------|
| TestUser1 | <testuser1@mall.com>  |
| TestUser2 | <testuser2@mall.com>  |
| TestUser3 | <testuser3@mall.com>  |

Use them to get a peek behind the scenes!

To stop the application, press Ctrl-c.

### Delete

Enter this command to completely remove docker related files:

```bash
docker compose -f docker-compose.yml down -v
```

## Development

To start, use:

```bash
docker compose up --watch
```

You will have access to ports for all Docker services (see them in docker-compose.override.yml).

Please note that there is a port (5678) for **debugging** Django in the container.

If you need to use *django_debug_toolbar*, you should set the **IP_DOCKER_CONTAINER** environment variable in the **.env** file. To do this, start all services and run the following command in a separate terminal window:

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}' mkb2_django
```

use the output and restart all services. Done!

There is also a built-in option for running **local tests**.
