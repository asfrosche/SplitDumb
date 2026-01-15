# SplitDumb

A production-quality expense sharing application built with FastAPI (backend) and Flutter (mobile frontend).

## Features (Phase 0 - P0)

- User authentication and profiles
- Group creation and management
- Expense creation with multiple split types:
  - Equal splits
  - Unequal/custom splits
  - Percentage splits
  - Share-based splits
- Expense editing and deletion
- Balance calculation per group and per user
- Manual settlements (settle-up)
- Activity feed / expense history
- Basic multi-currency support

## Architecture

- **Backend**: FastAPI + PostgreSQL with clean architecture
  - Domain layer: Pure business logic
  - Application layer: Use cases and orchestration
  - Infrastructure layer: Database, repositories
  - API layer: FastAPI routers and DTOs

- **Frontend**: Flutter mobile app
  - State management: Riverpod
  - Routing: GoRouter
  - Networking: Dio with JWT authentication

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Flutter SDK 3.0+
- Docker and Docker Compose (optional, for local development)

### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up database**:
   - Option A: Using Docker Compose (recommended):
   ```bash
   docker-compose up -d db
   ```

   - Option B: Manual PostgreSQL setup:
     - Create database: `createdb splitdumb`
     - Update `DATABASE_URL` in `.env` file

4. **Run migrations**:
```bash
cd backend
alembic upgrade head
```

5. **Seed currencies** (optional):
```bash
python scripts/seed_currencies.py
```

6. **Start backend server**:
```bash
# Using Docker Compose
docker-compose up backend

# Or directly
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Flutter dependencies**:
```bash
cd mobile
flutter pub get
```

2. **Generate JSON serialization code** (if needed):
```bash
flutter pub run build_runner build
```

3. **Update API base URL** (if backend is not on localhost:8000):
   - Edit `mobile/lib/core/network/api_client.dart`
   - Update `baseUrl` constant

4. **Run Flutter app**:
```bash
flutter run
```

## Docker Setup (Full Stack)

To run everything with Docker Compose:

```bash
docker-compose up
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
splitdumb/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── application/  # Application services
│   │   ├── core/         # Config, security, database
│   │   ├── domain/       # Domain models and services
│   │   └── infrastructure/ # Database models, repositories
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── mobile/
│   └── lib/
│       ├── core/         # Networking, routing, theme
│       └── features/     # Feature modules (auth, groups, expenses, etc.)
└── docker-compose.yml
```

## Development Notes

### Backend

- All monetary values are stored as integers (cents) to avoid floating-point errors
- Balances are calculated on-the-fly from expenses and settlements
- Soft deletes are used for expenses (deleted_at field)
- JWT tokens expire after 7 days (configurable)

### Frontend

- State management uses Riverpod providers
- JWT tokens are stored securely using flutter_secure_storage
- API client automatically adds Authorization header to requests
- Error handling shows user-friendly messages

## Future Phases

- **P1**: Debt simplification algorithms, receipt/audio recording
- **P2**: Server deployment, bank integration
- **P3**: Budgeting features, spending insights, categorization

## License

MIT
