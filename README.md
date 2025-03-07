# Event Management API

## Overview

The **Event Management API** is a lightweight Django-based REST API designed for event management. It provides essential features like user authentication, event creation, search functionality, and participant registration.

### Key Features

-  Custom User model with email-based registration
-  Full CRUD functionality for events
-  Secure JWT authentication
-  Event registration system
-  Email notifications for event registrations
-  Search functionality for events by title, description, or location
-  Role-based access (only organizers can modify or delete events)
-  Docker support for easy deployment

---

##  Installation with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/event-management-api.git
cd event-management-api
```

### 2. Build Docker Images

From the project root, run:

```bash
docker-compose build
```

### 3. Start the Containers

Once the build completes, start the services:

```bash
docker-compose up -d
```

### 4. Create a Superuser

If you need an admin account, run:

```bash
docker exec -it container_id python manage.py createsuperuser
```

### 5. Access the API

Once everything is up and running, you can interact with the API:

- **Base API URL:** `http://localhost:8000/`
- **Admin Panel:** `http://localhost:8000/admin/`

For testing purposes, you can use Postman or execute:

```bash
docker exec -it container_id python manage.py test
```

---

##  API Endpoints

###  User Management

- `POST /register/` – Register a new user

###  Authentication

- `POST /api/token/` – Generate JWT token
- `POST /api/token/refresh/` – Refresh access token

###  Event Management

- `GET /api/events/` – List all events
- `POST /api/events/` – Create an event (requires authentication)
- `GET /api/events/{id}/` – Retrieve event details (restricted to organizer)
- `PUT /api/events/{id}/` – Update an event (only the organizer can edit)
- `DELETE /api/events/{id}/` – Remove an event (only the organizer can delete)
- `GET /api/events?search=your-search-query/` – Search an event by title, description, or location

###  Event Registration

- `POST /api/events/{id}/register/` – Register a user for an event
- `POST /api/events/{id}/unregister/` – Unegister a user for an event

###  API Documentation

Full API Documentation is available at endpoint `/doc`

---

##  Running the Project Without Docker

If you prefer to run the project manually, follow these steps:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Apply Migrations

```bash
python manage.py migrate
```

### 3. Start the Development Server

```bash
python manage.py runserver
```

---

##  Running Tests

To execute tests inside the Docker container:

```bash
docker exec -it container_id python manage.py test
```

---

##  Additional Docker Commands

###  Stop Containers

```bash
docker-compose down
```

###  Restart Containers

```bash
docker-compose up -d
```

###  Remove Containers and Volumes

```bash
docker-compose down -v
```

