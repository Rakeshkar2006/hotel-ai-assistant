# AI-Powered Hotel Booking and Guest Service Assistant

An AI-powered hotel management and guest service backend built with FastAPI, PostgreSQL, JWT authentication, RAG, pgvector, WebSocket, Docker, and automated testing.

## Project Overview

This project provides a secure backend system for hotel booking and guest services.

The system can:

- Manage hotel room types and rooms
- Manage guest information
- Create and manage hotel bookings
- Prevent invalid or overlapping bookings
- Manage guest service requests
- Provide secure JWT-based authentication
- Support Admin, Receptionist, and Guest roles
- Upload and approve hotel knowledge documents
- Answer guest questions using Retrieval-Augmented Generation (RAG)
- Retrieve booking information securely for the logged-in guest
- Provide real-time chat using WebSocket
- Store chat sessions and messages
- Use PostgreSQL and pgvector for data and vector search
- Run using Docker
- Provide automated tests using pytest

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- pgvector
- Sentence Transformers
- RAG
- WebSocket
- pytest
- Docker
- Git & GitHub

## User Roles

### Admin

- Manage hotel data
- Manage users and guests
- Manage rooms and room types
- Manage bookings
- Manage service requests
- Upload and approve knowledge documents

### Receptionist

- Manage hotel operations
- Manage guest bookings
- Manage guest service requests

### Guest

- Access personal booking information
- Ask hotel-related questions
- Use the AI guest service chatbot
- View personal chat history

## Main Features

### Authentication

- User registration/login
- JWT access tokens
- Password hashing
- Role-based access control

### Hotel Booking

- Room type management
- Room management
- Guest management
- Booking management
- Booking status workflow
- Automatic booking price calculation
- Date validation
- Room availability validation
- Overlapping booking prevention

### Guest Service Requests

Guests can submit service requests such as:

- Housekeeping
- Other hotel services

Service request status can be managed by authorized users.

### Knowledge Documents

Administrators can:

1. Upload hotel knowledge documents
2. Approve documents
3. Store approved documents
4. Index document content
5. Search indexed content

Supported document formats:

- PDF
- TXT
- DOCX

### AI / RAG Chatbot

The chatbot uses approved hotel documents to answer guest questions.

The system uses:

- Document chunking
- Sentence Transformer embeddings
- pgvector similarity search
- Retrieval-Augmented Generation

The chatbot can provide information such as:

- Breakfast timings
- Check-in time
- Check-out time
- Hotel policies
- Other approved hotel information

If sufficient information is not available in the approved documents, the system does not invent an answer.

### Booking-Aware Chat

Authenticated guests can ask about their booking.

The system restricts booking information so that a guest can access only their own booking information.

### WebSocket Chat

Real-time chat is supported through WebSocket.

WebSocket endpoint:

`/chat/ws`

### API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

`/docs`

OpenAPI documentation:

`/openapi.json`

## Project Structure

```text
hotel-ai-assistant/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   └── deps.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── models/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── rag/
│   │   ├── answer.py
│   │   ├── chunker.py
│   │   └── search.py
│   │
│   ├── schemas/
│   └── main.py
│
├── data/
│   └── storage/
│
├── scripts/
│
├── tests/
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
## Installation and Setup

### 1. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file using `.env.example` as the template.

Do not commit `.env`, passwords, JWT tokens, or API keys to GitHub.

### 4. Run Database Migrations

```powershell
alembic upgrade head
```

### 5. Start the FastAPI Server

```powershell
uvicorn app.main:app --reload
```

API documentation is available at `/docs`.

## Testing

Run the automated tests with:

```powershell
pytest
```

## Docker

Start the application with Docker Compose:

```powershell
docker compose up --build
```

Stop the containers with:

```powershell
docker compose down
```

## Screenshots and Demo Evidence

Project demonstration screenshots are available in `docs/screenshots/`.

The screenshots cover authentication, room and guest management, booking validation, service requests, document indexing, RAG chatbot responses, access control, RAG fallback, and WebSocket chat.

## Individual Project

This project is developed and presented as an individual complete project. All major components are integrated into a single application, including authentication, hotel management, booking, service requests, knowledge document processing, RAG-based guest assistance, WebSocket chat, automated testing, and Docker deployment.