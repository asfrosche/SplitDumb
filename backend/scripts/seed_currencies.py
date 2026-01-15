"""
Seed script to populate currencies table.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infrastructure.db.models import Base, Currency

# Create engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Common currencies
CURRENCIES = [
    {"code": "USD", "name": "US Dollar", "symbol": "$", "precision": 2},
    {"code": "EUR", "name": "Euro", "symbol": "€", "precision": 2},
    {"code": "GBP", "name": "British Pound", "symbol": "£", "precision": 2},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "precision": 0},
    {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "precision": 2},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "precision": 2},
    {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF", "precision": 2},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "precision": 2},
    {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "precision": 2},
    {"code": "BRL", "name": "Brazilian Real", "symbol": "R$", "precision": 2},
]


def seed_currencies():
    """Seed currencies table."""
    db = SessionLocal()
    try:
        # Check if currencies already exist
        existing = db.query(Currency).count()
        if existing > 0:
            print("Currencies already seeded.")
            return

        # Insert currencies
        for currency_data in CURRENCIES:
            currency = Currency(**currency_data)
            db.add(currency)

        db.commit()
        print(f"Seeded {len(CURRENCIES)} currencies.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding currencies: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_currencies()
