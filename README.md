# Delivery Driver Recruitment Platform

A Django-based multi-stage recruitment platform for delivery drivers with questionnaires, automated emails, and admin dashboard.

## Features

- User registration system with GDPR compliance
- Multi-stage questionnaire system (3 stages)
- Admin dashboard for application review
- Email notifications for stage progression
- Tracking sources from advertisements
- Google Sheets integration for data export

## Setup Instructions

### 1. Install Requirements

The project requires Python 3.9+ and the following packages:
- Django 4.2+
- django-allauth
- django-crispy-forms
- crispy-bootstrap5
- dj-database-url
- psycopg2-binary
- google-api-python-client
- google-auth
- google-auth-httplib2
- google-auth-oauthlib

### 2. Database Setup

The application uses PostgreSQL by default. Configure your database settings in `settings.py` or through environment variables:

```bash
# Example environment variables
DATABASE_URL=postgresql://user:password@localhost:5432/driver_recruitment
SECRET_KEY=your-secret-key
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create a Superuser

```bash
python manage.py createsuperuser
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

### 6. Configure Google Sheets Integration

To enable the Google Sheets integration for exporting application data:

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API
3. Create OAuth credentials (Desktop application type)
4. Download the credentials file and save it as `credentials.json` in the project root
5. Set the following environment variables:
   ```
   GOOGLE_SHEETS_ENABLED=True
   GOOGLE_SHEETS_ID=your-google-sheet-id
   ```
6. Log in to the admin interface and go to "Core" > "Google Sheets Configuration"
7. Enable the integration and add your Google Sheet ID

Alternatively, you can initialize the Google Sheet by running:

```bash
python manage.py setup_google_sheet
```

This will create the necessary sheets and headers in your Google Sheet.

### 7. Export Data to Google Sheets

There are several ways to export data to Google Sheets:

#### From the Admin Interface:

- Select one or more answers in the Answers admin list and use the "Export selected answers to Google Sheets" action
- Select one or more users in the Users admin list and use the "Export selected users to Google Sheets" action
- Click the "Export to Sheets" button for an individual user in the Users admin list

#### Using Management Commands:

Export all users:
```bash
python manage.py export_to_sheets
```

Export a specific user:
```bash
python manage.py export_to_sheets --user=user@example.com
```

Export a specific stage:
```bash
python manage.py export_to_sheets --stage=1
```

## Advertisement Tracking

The platform supports tracking which advertisements applicants come from:

1. Create sources in the admin interface under "Application Sources"
2. Use tracking links in your advertisements:
   ```
   https://yourdomain.com/source/your-tracking-code/
   ```
3. When users register after visiting this link, their source will be tracked

## Project Structure

- `accounts/`: User authentication and profile management
- `recruitment/`: Questionnaire stages and application process
- `core/`: Shared functionality, settings, and integrations
- `utils/`: Utility functions (Google Sheets integration, etc.)
- `templates/`: HTML templates for the application
- `static/`: Static assets (CSS, JavaScript, images)

## Administration

The admin interface is available at `/admin/` and provides:

- User management (review, edit, export)
- Question configuration (add, edit, organize by stage)
- Answer review and export
- Application source tracking
- Google Sheets configuration

## License

This project is for demonstration purposes only.