# My-kanban2

[![Django Tests](https://github.com/Mas5ive/My_kanban2/actions/workflows/check.yml/badge.svg)](https://github.com/Mas5ive/My_kanban2/actions/workflows/check.yml)

## Description

A simple multi-user kanban application written on the Django 4.2 web framework. This is a demonstration project. Tests cover a small portion of the code intentionally.

The project uses:

- nginx
- postgres
- redis

### Available features

- signup is available via github
- login via email
- reset password
- create Kanban boards
- different functionality depending on the user's relationship to the board
- invite/exclude other users to your projects
- create/edit/move/delete task cards
- comment on cards and attach files

## Installation

You will need to have a **docker** to run it.

```bash
git clone https://github.com/Mas5ive/My_kanban2.git
```

```bash
cd My_kanban2/
```

## Preparation (optional)

 To try out github login, you need to create a github app in your developer settings.

- Specify values in the following fields:
  - Homepage URL: <https://127.0.0.1>
  - Authorization callback URL: <https://127.0.0.1/complete/github/>
- Generate keys and use them in the **docker-compose-demo.yml** file in the service with django, find the environment variables for github and replace them with your keys.

## Turn on the demo

### Run

```bash
docker compose -f docker-compose-demo.yml up --build
```

On your localhost on port 80 the application will become available after some time...

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
docker compose -f docker-compose-demo.yml down -v
```
