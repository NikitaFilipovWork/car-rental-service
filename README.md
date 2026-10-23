# Car Rental Service

## Quick start

Install Docker Desktop, open terminal in project directory and execute this command:

```bash
docker compose up --build
```

Open:

- API: <http://localhost:8000>
- Swagger: <http://localhost:8000/api/docs/>
- Admin panel: <http://localhost:8000/admin/>

## Download test data to db

When app is running, execute this command to load data to db:

```bash
docker compose exec web python manage.py loaddata initial_data.json
```

Accounts for tests:

- admin: `admin@admin.com` / `admin`
- user: `user1@user.com` / `user1`

## To stop the app

Use `Ctrl+C` in terminal, where you execute docker compose, and then use:

```bash
docker compose down
```

Data from db will be saved using volumes. If you want to clear it, use it with -v flag:

```bash
docker compose down -v
```
