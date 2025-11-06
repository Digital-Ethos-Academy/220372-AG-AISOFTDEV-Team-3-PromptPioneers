"""
Database configuration and session management for the PRD Analyzer application.

This module provides:
- SQLAlchemy engine and session configuration
- Database session dependency for FastAPI
- Database initialization and utility functions
- Connection management and foreign key enforcement

Usage:
    from database import get_db, init_db
    
    # Initialize database at startup
    init_db()
    
    # Use in FastAPI endpoints
    @app.get("/items/")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
"""

from typing import Generator, Optional
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from models import Base

# ============================================================================
# CONFIGURATION
# ============================================================================

# Database configuration
# SQLite database file location - stored in the artifacts directory
DATABASE_URL: str = "sqlite:///./artifacts/prd-database.db"
DATABASE_FILE: Path = Path("artifacts/prd-database.db")

# ============================================================================
# ENGINE SETUP
# ============================================================================

def create_database_engine(
    database_url: str = DATABASE_URL,
    echo: bool = False
) -> Engine:
    """
    Create and configure SQLAlchemy engine for database connections.
    
    Args:
        database_url: Database connection URL (default: SQLite local file).
        echo: If True, log all SQL statements (useful for debugging).
    
    Returns:
        Engine: Configured SQLAlchemy engine instance.
    
    Note:
        - check_same_thread=False allows SQLite to work with FastAPI's threading
        - This is safe when using proper session management with Depends()
        - Future mode enables SQLAlchemy 2.0 behaviors for forward compatibility
    """
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=None,  # Uses default QueuePool
        echo=echo,
        future=True
    )


# Create global engine instance
engine: Engine = create_database_engine()


# ============================================================================
# EVENT LISTENERS
# ============================================================================

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn: Connection, connection_record: object) -> None:
    """
    Enable foreign key constraint enforcement for SQLite connections.
    
    SQLite doesn't enforce foreign keys by default. This event listener
    ensures that foreign key constraints are enabled for every new connection.
    
    Args:
        dbapi_conn: Database connection object.
        connection_record: Connection record for tracking.
    
    Note:
        This is called automatically for every new database connection.
    """
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


# ============================================================================
# SESSION FACTORY
# ============================================================================

def create_session_factory(engine_instance: Engine) -> sessionmaker:
    """
    Create a session factory for database operations.
    
    Args:
        engine_instance: SQLAlchemy engine to bind sessions to.
    
    Returns:
        sessionmaker: Factory for creating database sessions.
    
    Configuration:
        - autocommit=False: Explicit commit required (safer for transactions)
        - autoflush=False: Manual control over when changes are flushed
        - bind=engine: Associates sessions with the database engine
    """
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine_instance
    )


# Create global session factory
SessionLocal: sessionmaker = create_session_factory(engine)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session management.
    
    Creates a new database session for each request and ensures proper
    cleanup after the request completes. This prevents connection leaks
    and maintains transaction integrity.
    
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session for the request.
    
    Note:
        The session is automatically closed in the finally block,
        even if an exception occurs during request processing.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db(engine_instance: Optional[Engine] = None, verbose: bool = True) -> bool:
    """
    Initialize the database by creating all tables defined in models.
    
    This function should be called once at application startup. It creates
    all tables if they don't exist, but will not modify existing tables
    or drop any data.
    
    Args:
        engine_instance: Optional engine to use (defaults to global engine).
        verbose: If True, print status messages.
    
    Returns:
        bool: True if initialization successful, False otherwise.
    
    Usage:
        # At application startup
        from database import init_db
        
        if init_db():
            print("Ready to serve requests")
        else:
            print("Failed to initialize database")
    
    Note:
        - Safe to call multiple times (idempotent)
        - Does not modify existing table structures
        - Requires all models to be imported before calling
    """
    target_engine: Engine = engine_instance or engine
    
    try:
        # Import models to register them with Base.metadata
        import models  # noqa: F401
        
        # Create all tables (checkfirst=True is default, safe for existing tables)
        Base.metadata.create_all(bind=target_engine)
        
        if verbose:
            print("✓ Database tables created successfully!")
        return True
        
    except SQLAlchemyError as e:
        if verbose:
            print(f"✗ Database initialization failed: {e}")
        return False
    except Exception as e:
        if verbose:
            print(f"✗ Unexpected error during database initialization: {e}")
        return False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def drop_all_tables(
    engine_instance: Optional[Engine] = None,
    verbose: bool = True,
    confirm: bool = False
) -> bool:
    """
    Drop all tables from the database.
    
    ⚠️  WARNING: This will permanently delete all data in the database!
    Use with extreme caution, typically only in development or testing.
    
    Args:
        engine_instance: Optional engine to use (defaults to global engine).
        verbose: If True, print status messages.
        confirm: Safety flag - must be True to actually drop tables.
    
    Returns:
        bool: True if tables dropped successfully, False otherwise.
    
    Usage:
        from database import drop_all_tables
        
        # Safe - requires explicit confirmation
        drop_all_tables(confirm=True)
    
    Note:
        Requires confirm=True as a safety mechanism to prevent
        accidental data loss.
    """
    if not confirm:
        if verbose:
            print("⚠️  Drop operation cancelled: confirm=True required")
        return False
    
    target_engine: Engine = engine_instance or engine
    
    try:
        Base.metadata.drop_all(bind=target_engine)
        
        if verbose:
            print("✓ All database tables dropped!")
        return True
        
    except SQLAlchemyError as e:
        if verbose:
            print(f"✗ Failed to drop tables: {e}")
        return False
    except Exception as e:
        if verbose:
            print(f"✗ Unexpected error while dropping tables: {e}")
        return False


def reset_db(
    engine_instance: Optional[Engine] = None,
    verbose: bool = True,
    confirm: bool = False
) -> bool:
    """
    Reset the database by dropping and recreating all tables.
    
    ⚠️  WARNING: This will permanently delete all data in the database!
    Use with extreme caution, typically only in development or testing.
    
    Args:
        engine_instance: Optional engine to use (defaults to global engine).
        verbose: If True, print status messages.
        confirm: Safety flag - must be True to actually reset database.
    
    Returns:
        bool: True if reset successful, False otherwise.
    
    Usage:
        from database import reset_db
        
        # Safe - requires explicit confirmation
        if reset_db(confirm=True):
            print("Database reset complete")
    
    Note:
        This is a destructive operation that:
        1. Drops all existing tables
        2. Recreates all tables from model definitions
        3. Results in an empty database
    """
    if not confirm:
        if verbose:
            print("⚠️  Reset operation cancelled: confirm=True required")
        return False
    
    target_engine: Engine = engine_instance or engine
    
    # Drop all tables first
    if not drop_all_tables(target_engine, verbose=verbose, confirm=True):
        return False
    
    # Recreate all tables
    if not init_db(target_engine, verbose=verbose):
        return False
    
    if verbose:
        print("✓ Database reset complete!")
    return True


def test_connection(
    engine_instance: Optional[Engine] = None,
    verbose: bool = True
) -> bool:
    """
    Test the database connection with a simple query.
    
    Args:
        engine_instance: Optional engine to test (defaults to global engine).
        verbose: If True, print status messages.
    
    Returns:
        bool: True if connection successful, False otherwise.
    
    Usage:
        from database import test_connection
        
        if test_connection():
            print("Database is ready")
        else:
            print("Database connection failed")
    
    Note:
        This function performs a simple SELECT 1 query to verify
        that the database is accessible and responsive.
    """
    target_engine: Engine = engine_instance or engine
    
    try:
        # Create a temporary session for testing
        session_factory: sessionmaker = create_session_factory(target_engine)
        db: Session = session_factory()
        
        try:
            # Execute a simple query to test connectivity
            result = db.execute(text("SELECT 1"))
            # Verify we got a result
            row = result.fetchone()
            
            if row and row[0] == 1:
                if verbose:
                    print("✓ Database connection successful!")
                return True
            else:
                if verbose:
                    print("✗ Database connection test returned unexpected result")
                return False
                
        finally:
            db.close()
            
    except SQLAlchemyError as e:
        if verbose:
            print(f"✗ Database connection failed: {e}")
        return False
    except Exception as e:
        if verbose:
            print(f"✗ Unexpected error during connection test: {e}")
        return False


def database_exists() -> bool:
    """
    Check if the database file exists.
    
    Returns:
        bool: True if database file exists, False otherwise.
    
    Usage:
        from database import database_exists
        
        if not database_exists():
            init_db()
    
    Note:
        This only checks for SQLite database files.
        For other database types, this will return False.
    """
    return DATABASE_FILE.exists()


def get_database_info(verbose: bool = True) -> dict:
    """
    Get information about the current database configuration.
    
    Args:
        verbose: If True, print database information.
    
    Returns:
        dict: Dictionary containing database configuration details.
    
    Usage:
        from database import get_database_info
        
        info = get_database_info()
        print(f"Database URL: {info['url']}")
    """
    info = {
        "url": DATABASE_URL,
        "file_path": str(DATABASE_FILE.absolute()),
        "exists": database_exists(),
        "file_size_mb": round(DATABASE_FILE.stat().st_size / (1024 * 1024), 2) 
                       if database_exists() else 0,
        "engine_echo": engine.echo,
    }
    
    if verbose:
        print("\n" + "=" * 60)
        print("DATABASE CONFIGURATION")
        print("=" * 60)
        print(f"URL:            {info['url']}")
        print(f"File Path:      {info['file_path']}")
        print(f"Exists:         {info['exists']}")
        print(f"Size:           {info['file_size_mb']} MB")
        print(f"Echo SQL:       {info['engine_echo']}")
        print("=" * 60 + "\n")
    
    return info


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main() -> int:
    """
    Main function for database setup and testing.
    
    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    print("\n" + "=" * 60)
    print("DATABASE SETUP AND VERIFICATION")
    print("=" * 60 + "\n")
    
    # Show current database configuration
    get_database_info(verbose=True)
    
    # Test database connection
    print("Step 1: Testing database connection...")
    if not test_connection():
        print("\n✗ Database setup failed: Connection test failed")
        return 1
    
    # Initialize database
    print("\nStep 2: Initializing database tables...")
    if not init_db():
        print("\n✗ Database setup failed: Initialization failed")
        return 1
    
    # Final verification
    print("\nStep 3: Running final verification...")
    if test_connection():
        print("\n" + "=" * 60)
        print("✓ DATABASE SETUP COMPLETE - READY FOR USE")
        print("=" * 60 + "\n")
        return 0
    else:
        print("\n✗ Final verification failed")
        return 1


if __name__ == "__main__":
    exit(main())