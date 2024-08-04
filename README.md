# My-kanban

## Description

A simple multi-user kanban application written on the Django 4.2 web framework.

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

```bash
git clone https://github.com/Mas5ive/My_kanban2
```

```bash
cd My_kanban2/
```

### Using Poetry

```bash
poetry install
```

```bash
poetry shell
```

### Using pip

- сreate a virtual environment
- activate it
- and run the command:

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 manage.py migrate
```

```bash
python3 manage.py runserver
```

## Turn on the demo (optional)

```bash
python3 manage.py loaddata data.json
```

This command will fill the database with content that will allow you to evaluate **most** of the application's features.

This example creates 3 users with the same passwords (321qwe,./):

| User      | Email                 |
|-----------|-----------------------|
| TestUser1 | <testuser1@mall.com>  |
| TestUser2 | <testuser2@mall.com>  |
| TestUser3 | <testuser3@mall.com>  |

Use them to get a peek behind the scenes!
