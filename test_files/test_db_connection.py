"""
Database Connection Test Script for P3.1

Tests PostgreSQL connectivity using .env configuration and async_get_db() 
dependency per Standards.md compliance. Validates database connection 
without violating governance constraints.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from app.core.db.database import async_engine, async_get_db
    from app.core.config import settings
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you're running from the project root directory")
    sys.exit(1)


async def test_database_connection():
    """Test basic database connectivity using async_get_db dependency."""
    print("🔧 Testing PostgreSQL Database Connection...")
    print(f"   Database: {settings.POSTGRES_DB}")
    print(f"   Host: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
    print(f"   User: {settings.POSTGRES_USER}")
    print()
    
    try:
        # Test connection via async_get_db dependency
        async for db in async_get_db():
            result = await db.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Database Connection Successful!")
            print(f"   PostgreSQL Version: {version}")
            return True
    
    except Exception as e:
        print(f"❌ Database Connection Failed:")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False


async def test_database_engine():
    """Test database engine connectivity directly."""
    print("🔧 Testing Database Engine Connectivity...")
    
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            print(f"✅ Engine Connection Successful!")
            print(f"   Connected Database: {db_name}")
            print(f"   Connected User: {user}")
            return True
    
    except Exception as e:
        print(f"❌ Engine Connection Failed:")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False


async def test_database_permissions():
    """Test database permissions for schema creation."""
    print("🔧 Testing Database Permissions...")
    
    try:
        async with async_engine.begin() as conn:
            # Test CREATE TABLE permission by creating a test table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_permissions (
                    id SERIAL PRIMARY KEY,
                    test_column TEXT
                )
            """))
            
            # Test INSERT permission
            await conn.execute(text("""
                INSERT INTO test_permissions (test_column) 
                VALUES ('permission_test') 
                ON CONFLICT DO NOTHING
            """))
            
            # Test SELECT permission
            result = await conn.execute(text("SELECT COUNT(*) FROM test_permissions"))
            count = result.scalar()
            
            # Clean up test table
            await conn.execute(text("DROP TABLE IF EXISTS test_permissions"))
            
            print(f"✅ Database Permissions Valid!")
            print(f"   CREATE, INSERT, SELECT, DROP permissions confirmed")
            return True
    
    except Exception as e:
        print(f"❌ Database Permissions Test Failed:")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False


async def main():
    """Run all database connection tests."""
    print("=" * 60)
    print("P3.1 DATABASE CONNECTION VERIFICATION")
    print("=" * 60)
    print()
    
    # Test results tracking
    tests_passed = 0
    total_tests = 3
    
    # Test 1: async_get_db dependency connection
    if await test_database_connection():
        tests_passed += 1
    print()
    
    # Test 2: Engine direct connection
    if await test_database_engine():
        tests_passed += 1
    print()
    
    # Test 3: Database permissions
    if await test_database_permissions():
        tests_passed += 1
    print()
    
    # Final results
    print("=" * 60)
    print(f"CONNECTION TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    print("=" * 60)
    
    if tests_passed == total_tests:
        print("🎉 All database connection tests PASSED!")
        print("✅ Database is ready for P3.1 schema setup and testing")
        return True
    else:
        print(f"⚠️  {total_tests - tests_passed} connection test(s) FAILED")
        print("❌ Database connection issues must be resolved before proceeding")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)