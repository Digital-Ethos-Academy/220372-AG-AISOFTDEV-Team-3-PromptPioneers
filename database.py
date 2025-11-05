from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

# Database configuration
# SQLite database file location - stored in the project root directory
DATABASE_URL = "sqlite:///./prd-database.db"

# Create SQLAlchemy engine
# check_same_thread=False is required for SQLite to work with FastAPI's async nature
# This allows the same connection to be used across different threads
# Note: This is safe for SQLite when using proper session management
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    # Enable connection pooling for better performance
    # For SQLite, we use NullPool to avoid connection issues
    poolclass=None,  # Uses default pool (QueuePool)
    # Echo SQL statements for debugging (set to False in production)
    echo=False,
    # Future mode enables SQLAlchemy 2.0 behaviors
    future=True
)


# Enable foreign key constraint enforcement for SQLite
# SQLite doesn't enforce foreign keys by default, so we need to enable it
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraint enforcement for SQLite connections."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Create a SessionLocal class for database sessions
# Each instance of SessionLocal will be a database session
# autocommit=False: Don't auto-commit transactions (explicit commit required)
# autoflush=False: Don't auto-flush pending changes before queries
# bind=engine: Bind sessions to our database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database sessions.
    
    This function creates a new SQLAlchemy session for each request,
    yields it to the endpoint function, and ensures proper cleanup
    after the request is complete.
    
    Usage in FastAPI endpoints:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        # Yield the session to the caller (FastAPI endpoint)
        yield db
    finally:
        # Ensure session is closed after request is complete
        # This prevents connection leaks and ensures proper cleanup
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function should be called once when the application starts
    to ensure all tables defined in the models exist in the database.
    
    If tables already exist, this function will not recreate them
    or drop existing data.
    
    Usage:
        # In main.py or app startup
        from database import init_db
        init_db()
    """
    # Import all models to ensure they are registered with Base.metadata
    # This is necessary for create_all() to know which tables to create
    import models  # noqa: F401
    
    # Create all tables defined in the models
    # checkfirst=True (default) ensures existing tables are not recreated
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_all_tables() -> None:
    """
    Drop all tables from the database.
    
    WARNING: This will delete all data in the database!
    Use with caution, typically only in development or testing.
    
    Usage:
        from database import drop_all_tables
        drop_all_tables()
    """
    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped!")


def reset_db() -> None:
    """
    Reset the database by dropping and recreating all tables.
    
    WARNING: This will delete all data in the database!
    Use with caution, typically only in development or testing.
    
    Usage:
        from database import reset_db
        reset_db()
    """
    drop_all_tables()
    init_db()
    print("Database reset complete!")


# Utility function to test database connection
def test_connection() -> bool:
    """
    Test the database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Create a test session
        db = SessionLocal()
        # Execute a simple query
        db.execute("SELECT 1")
        db.close()
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # If this file is run directly, test the connection and initialize the database
    print("Testing database connection...")
    if test_connection():
        print("\nInitializing database...")
        init_db()