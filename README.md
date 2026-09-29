# Travel Booking Application

A Django-based travel booking web application for searching, booking, and managing flights, trains, and buses. It uses Django, PostgreSQL, and Bootstrap 5.

## Features

- User registration, login, and profile management
- Browse and filter travel options by type, source, destination, date
- Secure booking with seat management and passenger details
- View and cancel bookings with real-time status updates
- AJAX-powered city autocomplete
- Responsive UI with Bootstrap 5
- TLS/SSL support for database connections

## Technology Stack

- Python 3.x, Django 5.2
- Database: PostgreSQL (connected with `DATABASE_URL`)
- Frontend: Bootstrap 5, JavaScript, AJAX
- PostgreSQL driver: psycopg 3

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/tejvir21/travel_booking_project.git
   cd travel_booking_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env` (`copy .env.example .env` on Windows, or `cp .env.example .env` on macOS/Linux).
   - Edit `.env` and set `SECRET_KEY`, `DATABASE_URL`, `DEBUG`, and `ALLOWED_HOSTS`.
   - Create a PostgreSQL database and user matching `DATABASE_URL`. Keep `.env` private; do not commit it.

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

9. Visit http://127.0.0.1:8000/ in your browser.

## Deployment

For production, configure `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` in the hosting provider's environment settings. Set `DEBUG=False`, run `python manage.py migrate` and `python manage.py collectstatic --noinput`, then configure the host to serve the `staticfiles` directory. Choose a platform that supports PostgreSQL connections.

## Database Configuration

The project loads `.env` and parses `DATABASE_URL` with `django-environ`. Use a PostgreSQL connection URL, for example:

```text
DATABASE_URL=postgresql://travel_user:password@localhost:5432/travel_booking
```

URL-encode reserved characters in the username or password. `ALLOWED_HOSTS` is a comma-separated list of hostnames; `localhost` and `127.0.0.1` are included by default.

## Running Tests

```bash
python manage.py test
```

## License

This project is licensed under the MIT License.
