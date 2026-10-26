# Car Rental Service

REST API and web app for a car rental company: car catalog with photos,
rentals, Stripe payments and Telegram notifications for staff.

**Backend:** Python 3.13, Django 6, Django REST Framework, SimpleJWT,
PostgreSQL, Redis, Celery, Stripe, drf-spectacular (Swagger).

**Frontend:** Vue 2.7, Vite, axios, v-calendar (in the [frontend](frontend) folder).

## Contents

1. [Quick start with Docker](#1-quick-start-with-docker)
2. [What to put in .env](#2-what-to-put-in-env)
3. [Connect Stripe payments](#3-connect-stripe-payments)
4. [Connect Telegram notifications](#4-connect-telegram-notifications)
5. [Run locally without Docker](#5-run-locally-without-docker)
6. [All environment variables](#6-all-environment-variables)
7. [Authentication](#7-authentication)
8. [API overview](#8-api-overview)
9. [Business rules](#9-business-rules)
10. [Frontend](#10-frontend)
11. [Tests and code style](#11-tests-and-code-style)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Quick start with Docker

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/)
with Docker Compose 2.24 or newer. Ports `8000`, `5173` and `6379` must be free.

**Step 1.** Clone the repository and go to the project folder:

```bash
git clone https://github.com/NikitaFilipovWork/car-rental-service.git
```

```bash
cd car-rental-service
```

**Step 2.** Create `.env` from the sample:

```bash
cp .env.sample .env
```

On Windows (cmd) use `copy .env.sample .env`.

Open `.env` and replace `SECRET_KEY` with any long random string. That is enough
to start the app. Payments and Telegram need their own keys, see
[section 2](#2-what-to-put-in-env); you can add them later.

**Step 3.** Build and start all services:

```bash
docker compose up --build
```

Compose starts 6 containers:

| Container  | What it does                                   | Port  |
|------------|------------------------------------------------|-------|
| `web`      | Django API, runs migrations on start           | 8000  |
| `frontend` | Vue web app (Vite dev server)                  | 5173  |
| `db`       | PostgreSQL                                     | —     |
| `redis`    | Cache and Celery broker                        | 6379  |
| `worker`   | Celery worker, sends Telegram notifications    | —     |
| `beat`     | Celery Beat, daily overdue check, hourly retry | —     |

Wait until the log shows `Starting development server at http://0.0.0.0:8000/`.

**Step 4.** In a second terminal, load demo data (10 cars with photos, 2 users, 6 rentals):

```bash
docker compose exec web python manage.py load_demo_data
```

The command loads `initial_data.json` and copies the car photos from
`car/fixtures/images/` to the media folder. You can run it again at any time:
it resets the demo records and copies only missing photos. Photo authors and
licences are listed in [car/fixtures/images/CREDITS.md](car/fixtures/images/CREDITS.md).

Demo accounts:

| Role  | Email             | Password |
|-------|-------------------|----------|
| Staff | `admin@admin.com` | `admin`  |
| User  | `user1@user.com`  | `user1`  |

To create your own admin:

```bash
docker compose exec web python manage.py createsuperuser
```

**Step 5.** Open in the browser:

| What        | URL                                |
|-------------|------------------------------------|
| **Web app** | <http://localhost:5173/>           |
| API root    | <http://localhost:8000/>           |
| Swagger UI  | <http://localhost:8000/api/docs/>  |
| Admin panel | <http://localhost:8000/admin/>     |

**Step 6 (optional).** Connect [Stripe](#3-connect-stripe-payments) and
[Telegram](#4-connect-telegram-notifications).

**After you change the code or `.env`**, rebuild and restart:

```bash
docker compose up --build
```

**Stop the app:** press `Ctrl+C`, then:

```bash
docker compose down
```

Database and car photos are kept in Docker volumes. To delete them as well:

```bash
docker compose down -v
```

---

## 2. What to put in .env

`.env.sample` already contains working values for Docker and for a local run.
Replace only the lines marked `CHANGE`:

| Variable                | Needed for             | Where to get the value |
|-------------------------|------------------------|------------------------|
| `SECRET_KEY`            | everything             | Any long random string, for example from `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `STRIPE_API`            | payments               | Stripe Dashboard → Developers → API keys → *Secret key* (`sk_test_...`), see [section 3](#3-connect-stripe-payments) |
| `STRIPE_WEBHOOK_SECRET` | payment status updates | Printed by `stripe listen` (`whsec_...`), see [section 3](#3-connect-stripe-payments) |
| `TELEGRAM_BOT_TOKEN`    | notifications          | @BotFather, see [section 4](#4-connect-telegram-notifications) |
| `TELEGRAM_CHAT_ID`      | notifications          | `getUpdates` of your bot, see [section 4](#4-connect-telegram-notifications) |

What happens if a value is missing:

| Missing                 | Result |
|-------------------------|--------|
| `STRIPE_API`            | Catalog and booking work, but returning a car (or canceling the day before the start) fails with *Payment service is unavailable*, because no payment can be created. |
| `STRIPE_WEBHOOK_SECRET` | Payments still become `PAID` when the user comes back from Stripe, but not when they close the tab, and expired sessions stay `PENDING`. |
| Telegram values         | Everything works; notifications are stored as failed (admin → *Failed notifications*) and resent every hour. |

The other variables do not need changes:

- In **Docker**, `docker-compose.yml` sets the database, Redis and Celery addresses
  itself. An empty `POSTGRES_DB` means the database `car_rental`.
- In a **local run**, an empty `POSTGRES_DB` means SQLite and an empty `REDIS_URL`
  means an in-memory cache, so neither PostgreSQL nor Redis is required.
- `DEBUG=True` must stay on: the dev server serves car photos only in debug mode.

After editing `.env`, restart the containers with `docker compose up --build`.
The full list is in [section 6](#6-all-environment-variables).

---

## 3. Connect Stripe payments

Payments are created as Stripe Checkout Sessions when a rental is returned
(rental price and overdue fee) or canceled the day before the start
(cancellation fee). Use **test mode**: no real money is charged.

1. Sign up at <https://dashboard.stripe.com/register> and turn on **Test mode**.
2. Open **Developers → API keys**, copy the *Secret key* (`sk_test_...`) and put it
   in `.env`:

   ```env
   STRIPE_API=sk_test_...
   ```

3. Install the [Stripe CLI](https://docs.stripe.com/stripe-cli) and log in:

   ```bash
   stripe login
   ```

4. Forward Stripe events to the API. Keep this terminal open while you test:

   ```bash
   stripe listen --forward-to localhost:8000/api/payments/webhook/
   ```

5. The command prints `Your webhook signing secret is whsec_...`. Put it in `.env`:

   ```env
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

6. Restart the app (`docker compose up --build`).

To pay, use the test card `4242 4242 4242 4242`, any future date and any CVC.

**How a payment gets its status:**

- `PENDING` — created, not paid yet. The web app shows a *Pay* button.
- `PAID` — set when the user comes back from Stripe (the web app opens its
  *Payment successful* page, which confirms the payment through
  `/api/payments/success/`) or by the webhook `checkout.session.completed`.
  The Telegram notification is sent only once.
- `EXPIRED` — set by the webhook `checkout.session.expired` (sessions live 24 hours).

If the user leaves Stripe without paying, they return to *Payments* with a hint
that they can pay later.

Where Stripe sends the user back is set by `FRONTEND_URL` (default
`http://localhost:5173`). If it is empty, Stripe returns to the API
(`SITE_URL/api/payments/success/`). The address is saved in the payment when it
is created, so changing it does not affect existing payments.

**For production:** add the endpoint `https://<your-domain>/api/payments/webhook/`
in Stripe Dashboard → Developers → Webhooks with the events
`checkout.session.completed`, `checkout.session.async_payment_succeeded` and
`checkout.session.expired`, put its signing secret in `STRIPE_WEBHOOK_SECRET`
and set `FRONTEND_URL` and `SITE_URL` to your domains.

---

## 4. Connect Telegram notifications

Staff get Telegram messages when a rental is created, returned or canceled,
when a payment is completed and when a rental is overdue (daily check at
09:00 Europe/Kyiv). Messages are sent by the `worker` container.

1. In Telegram open [@BotFather](https://t.me/BotFather), send `/newbot` and follow
   the steps. Copy the token it gives you to `.env`:

   ```env
   TELEGRAM_BOT_TOKEN=123456789:AA...
   ```

2. Open a chat with your bot and press **Start** (or add the bot to a group and
   send any message there).
3. Open `https://api.telegram.org/bot<token>/getUpdates` in the browser (with your
   token instead of `<token>`). Find `"chat":{"id":...}` and copy the number to
   `.env` (group ids start with `-`):

   ```env
   TELEGRAM_CHAT_ID=123456789
   ```

4. Restart the app (`docker compose up --build`).

If Redis or Telegram is unavailable, the message is saved as a
`FailedNotification` (admin panel → *Failed notifications*) and Celery Beat
resends it every hour.

---

## 5. Run locally without Docker

You need Python 3.13 and Node.js 18+. PostgreSQL and Redis are optional.

**Backend.** In the project folder:

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

Install dependencies and create `.env`:

```bash
pip install -r requirements.txt
```

```bash
cp .env.sample .env
```

Replace `SECRET_KEY` in `.env` (and the Stripe and Telegram values if you need
them). With the sample values the app uses SQLite and an in-memory cache.

Apply migrations, load demo data and start the API on <http://localhost:8000/>:

```bash
python manage.py migrate
```

```bash
python manage.py load_demo_data
```

```bash
python manage.py runserver
```

**Frontend.** In a second terminal:

```bash
cd frontend
```

```bash
npm install
```

```bash
npm run dev
```

Open <http://localhost:5173/>.

**Optional: PostgreSQL.** Create a database and set `POSTGRES_DB` (and user,
password, host, port if they differ) in `.env`.

**Optional: notifications.** Start Redis on `localhost:6379`, set
`REDIS_URL=redis://localhost:6379/1` in `.env`, then run Celery in two more
terminals:

```bash
celery -A core worker --loglevel=info --pool=solo
```

```bash
celery -A core beat --loglevel=info
```

`--pool=solo` is needed on Windows; on macOS / Linux you can omit it. Without
Redis the app still works: notifications are saved as failed and resent later.

---

## 6. All environment variables

Backend variables live in `.env` in the project root
(see [.env.sample](.env.sample)).

| Variable                | Default | Description |
|-------------------------|---------|-------------|
| `SECRET_KEY`            | — (required) | Django secret key. Docker uses a dev key if it is empty |
| `DEBUG`                 | `False` (`True` in Docker) | Must be `True` to serve car photos with the dev server |
| `ALLOWED_HOSTS`         | `127.0.0.1,localhost` | Comma-separated host names |
| `POSTGRES_DB`           | empty | Database name. Local run: empty means SQLite. Docker: empty means `car_rental` |
| `POSTGRES_USER`         | `postgres` | |
| `POSTGRES_PASSWORD`     | `postgres` | |
| `POSTGRES_HOST`         | `localhost` | Docker always uses `db` |
| `POSTGRES_PORT`         | `5432` | |
| `REDIS_URL`             | empty | Cache. Empty means in-memory cache. Docker always uses `redis://redis:6379/1` |
| `CELERY_BROKER_URL`     | `redis://127.0.0.1:6379/0` | Celery broker. Docker always uses `redis://redis:6379/0` |
| `STRIPE_API`            | empty | Stripe secret key `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | empty | Webhook signing secret `whsec_...` |
| `FRONTEND_URL`          | `http://localhost:5173` | Web app address for Stripe redirects; empty means redirect to the API |
| `SITE_URL`              | `http://localhost:8000` | API address, used for Stripe redirects when `FRONTEND_URL` is empty |
| `TELEGRAM_BOT_TOKEN`    | empty | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID`      | empty | Chat that receives notifications |
| `APP_PORT`              | `8000` | Docker only: host port of the API |
| `FRONTEND_PORT`         | `5173` | Docker only: host port of the web app |

Frontend variable in `frontend/.env` (see [frontend/.env.sample](frontend/.env.sample)):

| Variable            | Default | Description |
|---------------------|---------|-------------|
| `VITE_PROXY_TARGET` | `http://localhost:8000` | Backend address for the Vite proxy. Docker sets `http://web:8000` |

---

## 7. Authentication

The API uses JWT. Every endpoint except registration, login, the car catalog
and Stripe callbacks requires a token.

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

## 8. API overview

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
| POST, PUT, PATCH, DELETE | `/api/cars/`, `/api/cars/{id}/` | staff | Manage cars (a car with rentals cannot be deleted) |
| POST   | `/api/cars/{id}/upload-image/` | staff | Upload or replace car image (`multipart/form-data`, field `image`) |

Every car has an `image` field with the full image URL (or `null`).
Images are stored in `media/uploads/cars/` (in Docker: the `media_data` volume).

Filters and sorting for the list:

| Parameter                  | Example                      |
|----------------------------|------------------------------|
| `brand`                    | `?brand=toyota`              |
| `fuel_type`                | `?fuel_type=ELECTRIC` (`GAS`, `DIESEL`, `HYBRID`, `ELECTRIC`) |
| `min_year`, `max_year`     | `?min_year=2018&max_year=2022` |
| `available`                | `?available=true` — at least one car of the model is free today |
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
| GET    | `/api/payments/success/`   | anyone | Confirms a payment by `?session_id=` (used by the web app after Stripe) |
| GET    | `/api/payments/cancel/`    | anyone | Redirect target when `FRONTEND_URL` is empty |
| POST   | `/api/payments/webhook/`   | Stripe | Stripe webhook |

If Stripe is not configured or not reachable, endpoints that create or check
payments answer `503 Payment service is unavailable` and change nothing.

---

## 9. Business rules

**Rental statuses:** `BOOKED` → `COMPLETED` (returned), `CANCELED`
(canceled before start) or `OVERDUE` (not returned after `end_date`).

**Booking**

- `start_date` cannot be in the past and cannot be later than `end_date`.
- `inventory` is the number of cars of this model in the fleet. A car with
  `inventory = 0` cannot be booked.
- On every day of the chosen period at least one car of the model must be free:
  the number of active (`BOOKED` / `OVERDUE`) rentals of the model on that day
  must be lower than `inventory`. A car that is overdue and not returned yet
  stays busy. Booking, returning and canceling do not change `inventory`.
- The price per day is fixed at booking time; later price changes do not
  affect the rental.

**Return** — possible from `start_date` onward. The car becomes free for
new bookings and payments are created:

- `RENTAL` = price per day × number of booked days (`end_date - start_date + 1`);
- `OVERDUE_FEE`, if returned after `end_date` = price per day × overdue days × 1.5.

**Cancel** — only a `BOOKED` rental and only before `start_date`.
The car becomes free for new bookings. If you cancel the day before the start, a
`CANCELLATION_FEE` of 50% of the rental price is charged.

**Overdue** — every day at 09:00 (Europe/Kyiv) Celery Beat marks unreturned
rentals as `OVERDUE` and notifies staff in Telegram.

---

## 10. Frontend

A single-page Vue app in the [frontend](frontend) folder. In Docker it runs at
<http://localhost:5173/>; for a local run see [section 5](#5-run-locally-without-docker).

**Screens:**

- **Sign in / Sign up.**
- **Cars** — catalog with photos, search, filters (fuel, years, availability,
  free on dates) and sorting.
- **Car page** — details and booking form with a date range picker and price
  calculation. Staff also sees *Edit* and *Delete*.
- **Add / edit car** (staff) — car form with photo upload.
- **My rentals** (staff: *All rentals*) — rentals with status filter,
  *Return car* and *Cancel booking* buttons and the rental's payments.
- **Payments** — payments with status and type filters; unpaid ones have a
  *Pay* button that opens Stripe Checkout.
- **Payment successful** — Stripe returns here after checkout.
- **Profile** — change email and password.

**How it talks to the API:** the Vite dev server proxies `/api` and `/media`
to Django, so the browser sees one origin and no CORS setup is needed.
The backend address comes from `VITE_PROXY_TARGET`.

Other commands in `frontend/`: `npm run build` (production build to
`frontend/dist`) and `npm run lint` (ESLint).

---

## 11. Tests and code style

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

Frontend lint (in `frontend/`):

```bash
npm run lint
```

---

## 12. Troubleshooting

| Problem | Solution |
|---------|----------|
| `port is already allocated` on start | Another program uses 8000, 5173 or 6379. Stop it, or set `APP_PORT` / `FRONTEND_PORT` in `.env`. For 6379 stop your local Redis. |
| Web app shows *Server is not available* | The API is still starting. Wait for `Starting development server` in the `web` log and press *Try again*. |
| `database "..." does not exist` after changing `POSTGRES_DB` | The database volume was created with the old name. Run `docker compose down -v` (deletes the data) and start again. |
| Cars have no photos | Run `docker compose exec web python manage.py load_demo_data` and check that `DEBUG=True`. |
| Code or `.env` changes are not visible | Containers are built from the code: run `docker compose up --build`. |
| *Payment service is unavailable* when returning a car | `STRIPE_API` is empty or wrong. See [section 3](#3-connect-stripe-payments). |
| Payment stays `PENDING` after paying | The user closed the tab before coming back: run `stripe listen` with `STRIPE_WEBHOOK_SECRET` set, see [section 3](#3-connect-stripe-payments). |
| Old payment returns to a page without styles | It was created before `FRONTEND_URL` was set; new payments return to the web app. |
| No Telegram messages | Check `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`, press *Start* in the bot chat and look at `docker compose logs worker`. Unsent messages are in admin → *Failed notifications*. |
| Booking is rejected with *All cars of this model are booked* | Every car of the model is taken on some day of the period. Choose other dates or another car. |
