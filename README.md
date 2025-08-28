# Travel Booking Application

A Django-based travel booking web application that allows users to search, book, and manage travel options (flights, trains, buses). Built with Bootstrap for a responsive, user-friendly interface and MySQL/TiDB compatibility.

## Features

- User registration, login, and profile management
- Browse and filter travel options by type, source, destination, date
- Secure booking with seat management and passenger details
- View and cancel bookings with real-time status updates
- AJAX-powered city autocomplete
- Responsive UI with Bootstrap 5
- TLS/SSL support for database connections

## Technology Stack

- Python 3.x, Django 4.x
- Database: MySQL or TiDB (MySQL-compatible)
- Frontend: Bootstrap 5, JavaScript, AJAX
- Hosting: PythonAnywhere, AWS, or similar

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/tejvir21/travel_booking_project.git
   cd your-repo
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
   - Copy `env-example.txt` to `.env` and set your values (SECRET_KEY, DB credentials).

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

## Deployment on PythonAnywhere

1. Push code to GitHub.
2. Create a web app on PythonAnywhere (Manual config, Django, Python 3.x).
3. Clone your repo in PythonAnywhere, set up a virtualenv, install requirements.
4. Configure environment variables in the Web tab.
5. Map `/static/` to your `staticfiles` directory and run `collectstatic`.
6. Update WSGI file to point to `travel_project.settings`.
7. Apply migrations and reload the web app.

## Database Configuration

In `settings.py`:
```python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': config('DB_NAME'),
    'USER': config('DB_USER'),
    'PASSWORD': config('DB_PASSWORD'),
    'HOST': config('DB_HOST'),
    'PORT': config('DB_PORT'),
    'OPTIONS': {
      'ssl': {'ca': os.path.join(BASE_DIR, 'certs', 'ca.pem')},
      'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
      'charset': 'utf8mb4',
    },
  }
}
```

## Running Tests

```bash
python manage.py test
```

## License

This project is licensed under the MIT License.
