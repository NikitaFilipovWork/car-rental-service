# Car Rental Service

## Quick start

Install Docker Desktop, copy `.env.sample` to `.env` and fill in the values
(the app also starts without `.env`, using local defaults).
Then open terminal in project directory and execute this command:

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

## Telegram Notifications

The project uses **Celery and Redis** to send Telegram notifications asynchronously.

### Features

- Notifications when a rental is created.
- Notifications when a rental is returned.
- Notifications when a rental is canceled.
- Daily checks for overdue rentals at 09:00 (Europe/Kyiv).
- Automatic retries of failed notifications every hour.

### Configuration

Create a Telegram bot using [@BotFather](https://t.me/BotFather) and obtain its API token.

Add the following variables to your `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

The bot must have permission to send messages to the specified chat.

### Background tasks

The following services start automatically with Docker Compose:

- **Redis** — message broker for Celery.
- **Celery Worker** — processes notification tasks.
- **Celery Beat** — schedules periodic tasks.

Start the services:

```bash
docker compose up --build
```

### Failed notifications

If a notification cannot be queued because the Celery broker is unavailable, it is saved in the database as a `FailedNotification`.

Celery Beat schedules an hourly task to retry saved notifications.

Successfully resent notifications are removed from the database.

## Stripe payments

Payments are created as Stripe Checkout Sessions when a rental is returned
(rental price and overdue fee) or canceled less than a day before start
(cancellation fee).

Add the following variables to your `.env` file:

```env
STRIPE_API=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
SITE_URL=http://localhost:8000
```

Stripe marks payments as `PAID` / `EXPIRED` through the webhook
`POST /api/payments/webhook/` (events `checkout.session.completed`,
`checkout.session.async_payment_succeeded`, `checkout.session.expired`).
For local development forward events with the Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/api/payments/webhook/
```
