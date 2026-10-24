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

Telegram Notifications

The project uses Celery and Redis to send Telegram notifications asynchronously.

Features:

Notifications about new rentals.

Daily overdue rental checks at 09:00 (Europe/Kyiv).

Automatic retries of failed notifications every hour.

To enable notifications, create a Telegram bot and add these variables to your .env file:

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

Celery worker, Celery Beat, and Redis start automatically with docker compose up --build.

Failed notifications are stored in the database and retried automatically.
