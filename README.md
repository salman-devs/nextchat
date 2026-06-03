# NextChat

A real-time team collaboration platform built with FastAPI and React. NextChat allows teams to communicate through workspaces and channels with real-time messaging, file sharing, and role-based access control.

## Features

- Authentication with JWT (register, login, logout)
- Workspaces with role-based access control (owner, admin, member)
- Channels within workspaces for organized communication
- Real-time messaging with WebSockets
- Typing indicators
- Online and offline user status
- Message history with persistent storage
- File uploads and sharing
- Message search across workspace channels
- In-app notifications

## Tech Stack

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy ORM
- PostgreSQL (Supabase)
- WebSockets
- JWT Authentication (python-jose)
- Bcrypt password hashing (passlib)
- Alembic for database migrations
- Uvicorn ASGI server

### Frontend
- React 18
- Vite
- React Router DOM
- Axios
- Context API for state management
- date-fns for timestamp formatting
- CSS Variables for theming

### Deployment
- Frontend: Vercel
- Backend: Render
- Database: Supabase (PostgreSQL)

## Project Structure

nextchat/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── workspaces.py
│   │   │   ├── channels.py
│   │   │   └── messages.py
│   │   ├── websocket/
│   │   │   ├── manager.py
│   │   │   └── connection.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── auth/
│   │   ├── database/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
└── frontend/
├── src/
│   ├── pages/
│   ├── components/
│   ├── services/
│   ├── context/
│   └── routes/
└── package.json


## Database Schema

- users (id, username, email, hashed_password, profile_picture, is_online, created_at)
- workspaces (id, name, owner_id, created_at)
- workspace_members (id, workspace_id, user_id, role)
- channels (id, name, workspace_id, created_at)
- messages (id, content, channel_id, sender_id, created_at)
- files (id, file_url, message_id, uploaded_at)

## API Endpoints

### Authentication
- POST /auth/register
- POST /auth/login
- GET /auth/me

### Workspaces
- POST /workspaces/
- GET /workspaces/
- GET /workspaces/{id}
- DELETE /workspaces/{id}
- POST /workspaces/{id}/join
- GET /workspaces/{id}/members
- PATCH /workspaces/{id}/members/{user_id}/role
- DELETE /workspaces/{id}/members/{user_id}

### Channels
- POST /channels/
- GET /channels/workspace/{workspace_id}
- DELETE /channels/{id}

### Messages
- GET /messages/{channel_id}
- GET /messages/search/{workspace_id}?q={query}
- POST /upload/{channel_id}

### WebSocket
- WS /ws/channel/{channel_id}?token={jwt_token}

## Getting Started

### Prerequisites
- Python 3.12
- Node.js 18+
- PostgreSQL database (Supabase recommended)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a .env file in the backend folder:

DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Run the backend:

```bash
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## How It Works

1. Register an account or login
2. Create a workspace or join one using a workspace ID
3. Create channels inside the workspace
4. Start chatting in real-time with your team
5. Share files using the attachment button
6. Search messages using the search bar
7. View online status of team members in the right sidebar

## Environment Variables

| Variable | Description |
|---|---|
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | JWT secret key |
| ALGORITHM | JWT algorithm (HS256) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry time |

## License

MIT License

