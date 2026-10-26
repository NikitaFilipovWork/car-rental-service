# Car Rental Service

REST API for a car rental company: car catalog, rentals, Stripe payments
and Telegram notifications for staff.

**Stack:** Python 3.13, Django 6, Django REST Framework, SimpleJWT,
PostgreSQL, Redis, Celery, Stripe, drf-spectacular (Swagger).

## Contents

1. [Run with Docker (recommended)](#1-run-with-docker-recommended)
2. [Run locally without Docker](#2-run-locally-without-docker)
3. [Environment variables](#3-environment-variables)
4. [Authentication](#4-authentication)
5. [API overview](#5-api-overview)
6. [Business rules](#6-business-rules)
7. [Stripe payments](#7-stripe-payments)
8. [Telegram notifications](#8-telegram-notifications)
9. [Tests and code style](#9-tests-and-code-style)

---

## 1. Run with Docker (recommended)

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/)
(Docker Compose 2.24 or newer).

**Step 1.** Clone the repository and go to the project folder:

```bash
git clone https://github.com/NikitaFilipovWork/car-rental-service.git
cd car-rental-service
```

**Step 2.** Create `.env` from the sample and fill in your keys
(see [Environment variables](#3-environment-variables)):

```bash
cp .env.sample .env
```

The app starts without `.env` too, but then Stripe and Telegram will not work.

**Step 3.** Build and start all services:

```bash
docker compose up --build
```

Compose starts 5 containers: `web` (Django), `db` (PostgreSQL), `redis`,
`worker` (Celery worker) and `beat` (Celery Beat). Migrations run
automatically when `web` starts.

**Step 4.** In a second terminal, load demo data (10 cars, 2 users, 6 rentals):

```bash
docker compose exec web python manage.py loaddata initial_data.json
```

Demo accounts:

| Role  | Email             | Password |
|-------|-------------------|----------|
| Staff | `admin@admin.com` | `admin`  |
| User  | `user1@user.com`  | `user1`  |

To create your own admin instead:

```bash
docker compose exec web python manage.py createsuperuser
```

**Step 5.** Open in the browser:

| What        | URL                                |
|-------------|------------------------------------|
| API root    | <http://localhost:8000/>           |
| Swagger UI  | <http://localhost:8000/api/docs/>  |
| Admin panel | <http://localhost:8000/admin/>     |

**Stop the app:** press `Ctrl+C`, then:

```bash
docker compose down
```

Database data is kept in a Docker volume. To delete it as well:

```bash
docker compose down -v
```

---

## 2. Run locally without Docker

You need Python 3.13. PostgreSQL and Redis are optional: without
`POSTGRES_DB` the app uses SQLite, and without Redis the cache is kept in memory
(notifications are then saved as failed and resent later).

```bash
python -m venv .venv
```

Activate the environment. On Windows:

```bash
.venv\Scripts\activate
```

On macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and prepare `.env`:

```bash
pip install -r requirements.txt
```

```bash
cp .env.sample .env
```

To use SQLite, open `.env` and leave `POSTGRES_DB` empty (`POSTGRES_DB=`).

Apply migrations, load demo data and start the server:

```bash
python manage.py migrate
```

```bash
python manage.py loaddata initial_data.json
```

```bash
python manage.py runserver
```

To process notifications, start Redis, then Celery in two separate terminals:

```bash
celery -A core worker --loglevel=info
```

```bash
celery -A core beat --loglevel=info
```

On Windows add `--pool=solo` to the worker command.

---

## 3. Environment variables

All variables are listed in [.env.sample](.env.sample).

| Variable                | Required | Description |
|-------------------------|----------|-------------|
| `SECRET_KEY`            | yes      | Django secret key (Docker uses a dev default if empty) |
| `DEBUG`                 | no       | `True` / `False`, default `False` |
| `ALLOWED_HOSTS`         | no       | Comma-separated hosts, default `127.0.0.1,localhost` |
| `POSTGRES_DB`           | no       | Database name. Empty means SQLite |
| `POSTGRES_USER`         | no       | Default `postgres` |
| `POSTGRES_PASSWORD`     | no       | Default `postgres` |
| `POSTGRES_HOST`         | no       | `localhost` locally (Docker sets `db` itself) |
| `POSTGRES_PORT`         | no       | Default `5432` |
| `REDIS_URL`             | no       | Redis for cache, e.g. `redis://localhost:6379/1` |
| `CELERY_BROKER_URL`     | no       | Celery broker, default `redis://127.0.0.1:6379/0` |
| `STRIPE_API`            | for payments | Stripe secret key `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | for payments | Webhook signing secret `whsec_...` |
| `SITE_URL`              | no       | Public URL of the API, used in Stripe redirect links. Default `http://localhost:8000` |
| `TELEGRAM_BOT_TOKEN`    | for notifications | Token from @BotFather |
| `TELEGRAM_CHAT_ID`      | for notifications | Chat that receives notifications |

---

## 4. Authentication

The API uses JWT. Every endpoint except registration, login and Stripe
callbacks requires a token.

**1. Register:**

```bash
curl -X POST http://localhost:8000/api/users/ -H "Content-Type: application/json" -d "{\"email\": \"me@example.com\", \"password\": \"secret123\"}"
```

**2. Get tokens:**

```bash
curl -X POST http://localhost:8000/api/users/token/ -H "Content-Type: application/json" -d "{\"email\": \"me@example.com\", \"password\": \"secret123\"}"
```

The response contains `access` (valid 60 minutes) and `refresh` (valid 1 day).

**3. Send the access token in every request:**

```
Authorization: Bearer <access>
```

In Swagger click **Authorize** and paste the access token.

**4. Refresh the access token** with `POST /api/users/token/refresh/` and body
`{"refresh": "<refresh>"}`.

Rate limits: anonymous users get 30 requests per minute, authenticated users
100 per minute, login 5 per minute, registration 3 per minute.

---

## 5. API overview

Full interactive documentation is in Swagger: <http://localhost:8000/api/docs/>.

### Users — `/api/users/`

| Method | URL                         | Who    | Description |
|--------|-----------------------------|--------|-------------|
| POST   | `/api/users/`               | anyone | Register |
| POST   | `/api/users/token/`         | anyone | Get JWT tokens |
| POST   | `/api/users/token/refresh/` | anyone | Refresh access token |
| GET, PUT, PATCH | `/api/users/me/`   | user   | View / update own profile |

### Cars — `/api/cars/`

| Method | URL                | Who        | Description |
|--------|--------------------|------------|-------------|
| GET    | `/api/cars/`       | anyone     | List cars |
| GET    | `/api/cars/{id}/`  | anyone     | Car details |
| POST, PUT, PATCH, DELETE | `/api/cars/`, `/api/cars/{id}/` | staff | Manage cars |
| POST   | `/api/cars/{id}/upload-image/` | staff | Upload or replace car image (`multipart/form-data`, field `image`) |

Every car has an `image` field with the full image URL (or `null`).
Images are stored in `media/uploads/cars/` (in Docker: the `media_data` volume).

Filters and sorting for the list:

| Parameter                  | Example                      |
|----------------------------|------------------------------|
| `brand`                    | `?brand=toyota`              |
| `fuel_type`                | `?fuel_type=ELECTRIC` (`GAS`, `DIESEL`, `HYBRID`, `ELECTRIC`) |
| `min_year`, `max_year`     | `?min_year=2018&max_year=2022` |
| `available`                | `?available=true`            |
| `start_date` + `end_date`  | `?start_date=2026-11-01&end_date=2026-11-05` — cars free for these dates (both are required) |
| `search`                   | `?search=corolla` (brand or model) |
| `ordering`                 | `?ordering=-daily_rate` (`daily_rate`, `year`, `brand`, `model`) |

### Rentals — `/api/rentals/`

A regular user sees only their own rentals, staff sees all.

| Method | URL                          | Description |
|--------|------------------------------|-------------|
| GET    | `/api/rentals/`              | List. Filters: `?status=BOOKED`, `?user_id=1` |
| POST   | `/api/rentals/`              | Book a car: `{"car": 1, "start_date": "2026-11-01", "end_date": "2026-11-05"}` |
| GET    | `/api/rentals/{id}/`         | Details with car, user and payments |
| POST   | `/api/rentals/{id}/return/`  | Return the car |
| POST   | `/api/rentals/{id}/cancel/`  | Cancel the booking |

### Payments — `/api/payments/`

| Method | URL                        | Who    | Description |
|--------|----------------------------|--------|-------------|
| GET    | `/api/payments/`           | user   | List own payments (staff: all). Filters: `?status=PENDING`, `?type=RENTAL` |
| GET    | `/api/payments/{id}/`      | user   | Payment details |
| GET    | `/api/payments/success/`   | Stripe | Redirect after successful payment |
| GET    | `/api/payments/cancel/`    | Stripe | Redirect when user leaves checkout |
| POST   | `/api/payments/webhook/`   | Stripe | Stripe webhook |

---

## 6. Business rules

**Rental statuses:** `BOOKED` → `COMPLETED` (returned), `CANCELED`
(canceled before start) or `OVERDUE` (not returned after `end_date`).

**Booking**

- `start_date` cannot be in the past and cannot be later than `end_date`.
- The car must have `inventory > 0`. Booking decreases `inventory` by 1.
- The dates must not overlap another active (`BOOKED` / `OVERDUE`) rental of
  the same car.
- The price per day is fixed at booking time; later price changes do not
  affect the rental.

**Return** — possible from `start_date` onward. `inventory` goes back up by 1
and payments are created:

- `RENTAL` = price per day × number of booked days (`end_date - start_date + 1`);
- `OVERDUE_FEE`, if returned after `end_date` = price per day × overdue days × 1.5.

**Cancel** — only a `BOOKED` rental and only before `start_date`.
`inventory` goes back up by 1. If you cancel the day before the start, a
`CANCELLATION_FEE` of 50% of the rental price is charged.

**Overdue** — every day at 09:00 (Europe/Kyiv) Celery Beat marks unreturned
rentals as `OVERDUE` and notifies staff in Telegram.

---

## 7. Stripe payments

Each payment is a Stripe Checkout Session. The payment link is in the
`session_url` field of the payment (also shown in the rental details).

**Setup:**

1. Create a Stripe account and switch to **Test mode**.
2. Copy the secret key (`sk_test_...`) to `STRIPE_API` in `.env`.
3. Install the [Stripe CLI](https://docs.stripe.com/stripe-cli) and forward
   webhooks to the local server:

   ```bash
   stripe listen --forward-to localhost:8000/api/payments/webhook/
   ```

4. The CLI prints a signing secret `whsec_...`. Put it in
   `STRIPE_WEBHOOK_SECRET` and restart the app.

To pay in test mode, use the card `4242 4242 4242 4242`, any future date and any CVC.

**How a payment gets its status:**

- `PENDING` — created, not paid yet.
- `PAID` — set by the webhook `checkout.session.completed`, or when Stripe
  redirects the user to `/api/payments/success/`. The Telegram notification is
  sent only once.
- `EXPIRED` — set by the webhook `checkout.session.expired` (sessions live 24 hours).

For production, add the endpoint `https://<your-domain>/api/payments/webhook/`
in Stripe Dashboard → Developers → Webhooks with the events
`checkout.session.completed`, `checkout.session.async_payment_succeeded` and
`checkout.session.expired`, and set `SITE_URL` to your domain.

---

## 8. Telegram notifications

Staff get Telegram messages when:

- a rental is created, returned or canceled;
- a payment is completed;
- a rental is overdue (daily check at 09:00 Europe/Kyiv).

**Setup:**

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy its token to
   `TELEGRAM_BOT_TOKEN`.
2. Add the bot to the chat (or write to it), then get the chat id, for example
   from `https://api.telegram.org/bot<token>/getUpdates`. Put it in `TELEGRAM_CHAT_ID`.
3. Restart the app.

Messages are sent by the Celery worker. If Redis or Telegram is unavailable,
the message is saved as a `FailedNotification` (visible in the admin panel),
and Celery Beat tries to resend it every hour.

---

## 9. Tests and code style

Run tests (no Redis, Stripe or Telegram needed; they are mocked):

```bash
python manage.py test
```

In Docker:

```bash
docker compose exec web python manage.py test
```

Check code style (the same checks run in GitHub Actions CI on every push):

```bash
black --check .
```

```bash
flake8
```
