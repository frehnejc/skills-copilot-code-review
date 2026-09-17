# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up students for activities as a signed-in teacher
- Display active, database-backed school announcements
- Add, edit, and delete announcements from the signed-in management dialog

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get announcements active today                                      |
| GET    | `/announcements/manage`                                           | Get all announcements (bearer session required)                     |
| POST   | `/announcements`                                                  | Add an announcement (bearer session required)                       |
| PUT    | `/announcements/{announcement_id}`                                | Modify an announcement (bearer session required)                    |
| DELETE | `/announcements/{announcement_id}`                                | Delete an announcement (bearer session required)                    |

Announcement create and update requests use JSON with a required `message` and
`expiration_date` (`YYYY-MM-DD`). The optional `start_date` uses the same format.
Management requests send the `session_token` returned by `/auth/login` as an
`Authorization: Bearer <token>` header.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

3. **Announcements** - Uses a generated identifier:
   - Message
   - Optional start date
   - Required expiration date

Activities, accounts, and announcements are stored in MongoDB. Login sessions are
kept in application memory and end when the server restarts.
