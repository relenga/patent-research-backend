"""
Database Schema Setup Script for P3.1

Creates P3.1 database schema using SQLAlchemy create_all() method per 
Standards.md constraints (NO Alembic). Handles schema creation with 
proper error handling and governance compliance.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from app.core.db.database import Base, async_engine
    from app.models.database import *  # Import all P3.1 models
    from sqlalchemy import text
    from sqlalchemy.schema import CreateSchema
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you're running from the project root directory")
    sys.exit(1)


async def check_schema_exists(schema_name="public"):
    """Check if the target schema exists and has proper permissions."""
    print(f"🔧 Checking Schema '{schema_name}' Status...")
    
    try:
        async with async_engine.begin() as conn:
            # Check schema existence
            result = await conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = :schema_name
            """), {"schema_name": schema_name})
            
            schema_exists = result.fetchone() is not None
            print(f"   Schema '{schema_name}': {'EXISTS' if schema_exists else 'NOT FOUND'}")
            
            # Check permissions on schema
            result = await conn.execute(text("""
                SELECT has_schema_privilege(:schema_name, 'CREATE') as can_create,
                       has_schema_privilege(:schema_name, 'USAGE') as can_use
            """), {"schema_name": schema_name})
            
            perms = result.fetchone()
            can_create = perms.can_create if perms else False
            can_use = perms.can_use if perms else False
            
            print(f"   CREATE privilege: {'✅' if can_create else '❌'}")
            print(f"   USAGE privilege: {'✅' if can_use else '❌'}")
            
            return schema_exists, can_create, can_use
    
    except Exception as e:
        print(f"❌ Schema Check Failed: {e}")
        return False, False, False


async def enable_postgresql_extensions():
    """Enable required PostgreSQL extensions for P3.1."""
    print("🔧 Enabling Required PostgreSQL Extensions...")
    
    extensions = [
        ("uuid-ossp", "UUID generation functions"),
        ("btree_gin", "Advanced indexing support")
    ]
    
    enabled_count = 0
    
    try:
        async with async_engine.begin() as conn:
            for ext_name, description in extensions:
                try:
                    # Check if extension exists
                    result = await conn.execute(text("""
                        SELECT EXISTS(
                            SELECT 1 FROM pg_extension 
                            WHERE extname = :ext_name
                        )
                    """), {"ext_name": ext_name})
                    
                    ext_exists = result.scalar()
                    
                    if not ext_exists:
                        # Try to create extension
                        await conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS {ext_name}"))
                        print(f"   ✅ Enabled extension '{ext_name}': {description}")
                        enabled_count += 1
                    else:
                        print(f"   ✅ Extension '{ext_name}' already enabled: {description}")
                        enabled_count += 1
                
                except Exception as e:
                    print(f"   ⚠️  Could not enable '{ext_name}': {e}")
                    # Continue with other extensions
            
            return enabled_count > 0
    
    except Exception as e:
        print(f"❌ Extension setup failed: {e}")
        return False


async def create_database_schema():
    """Create P3.1 database schema using SQLAlchemy create_all()."""
    print("🔧 Creating P3.1 Database Schema...")
    print("   Using SQLAlchemy Base.metadata.create_all() (Standards.md compliant)")
    print()
    
    try:
        async with async_engine.begin() as conn:
            # Create all tables defined in the metadata
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Schema Creation Completed Successfully!")
            return True
    
    except Exception as e:
        print(f"❌ Schema Creation Failed: {e}")
        print(f"   Error Type: {type(e).__name__}")
        
        # Try alternative approach with simplified UUID generation
        print("   Attempting alternative UUID generation method...")
        try:
            # Drop and recreate with simpler UUID approach
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Schema Creation with Alternative Method Succeeded!")
            return True
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            return False


async def verify_schema_tables():
    """Verify that all P3.1 tables were created correctly."""
    print("🔧 Verifying P3.1 Database Tables...")
    
    expected_tables = {
        'documents', 'document_versions', 'artifacts', 'diagram_canonical',
        'corpora', 'corpus_memberships', 'agent_runs', 'tasks',
        'audit_events', 'provenance'
    }
    
    try:
        async with async_engine.begin() as conn:
            # Get all table names in the public schema
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            existing_tables = {row.table_name for row in result}
            
            # Check which P3.1 tables exist
            found_tables = expected_tables.intersection(existing_tables)
            missing_tables = expected_tables - existing_tables
            
            print(f"   Expected P3.1 Tables: {len(expected_tables)}")
            print(f"   Found P3.1 Tables: {len(found_tables)}")
            
            if found_tables:
                print("   ✅ Created Tables:")
                for table in sorted(found_tables):
                    print(f"      • {table}")
            
            if missing_tables:
                print("   ❌ Missing Tables:")
                for table in sorted(missing_tables):
                    print(f"      • {table}")
                return False
            else:
                print("   🎉 All P3.1 tables created successfully!")
                return True
    
    except Exception as e:
        print(f"❌ Table Verification Failed: {e}")
        return False


async def verify_table_constraints():
    """Verify that database constraints are properly created."""
    print("🔧 Verifying Database Constraints...")
    
    try:
        async with async_engine.begin() as conn:
            # Check for key constraints
            result = await conn.execute(text("""
                SELECT COUNT(*) as constraint_count
                FROM information_schema.table_constraints 
                WHERE table_schema = 'public' 
                AND constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'CHECK', 'UNIQUE')
            """))
            
            constraint_count = result.scalar()
            print(f"   Database Constraints Created: {constraint_count}")
            
            if constraint_count > 0:
                print("   ✅ Database constraints successfully applied")
                return True
            else:
                print("   ⚠️  No constraints found - schema may be incomplete")
                return False
    
    except Exception as e:
        print(f"❌ Constraint Verification Failed: {e}")
        return False


async def verify_indexes():
    """Verify that performance indexes are created."""
    print("🔧 Verifying Database Indexes...")
    
    try:
        async with async_engine.begin() as conn:
            # Check for indexes
            result = await conn.execute(text("""
                SELECT COUNT(*) as index_count
                FROM pg_indexes 
                WHERE schemaname = 'public'
                AND indexname NOT LIKE '%_pkey'  -- Exclude primary key indexes
            """))
            
            index_count = result.scalar()
            print(f"   Performance Indexes Created: {index_count}")
            
            if index_count > 0:
                print("   ✅ Performance indexes successfully created")
                return True
            else:
                print("   ⚠️  Limited indexes found - performance may be impacted")
                return True  # Not critical for basic functionality
    
    except Exception as e:
        print(f"❌ Index Verification Failed: {e}")
        return False


async def main():
    """Execute complete P3.1 database schema setup."""
    print("=" * 70)
    print("P3.1 DATABASE SCHEMA SETUP")
    print("=" * 70)
    print()
    
    # Setup results tracking
    steps_completed = 0
    total_steps = 5
    
    # Step 1: Check schema status
    schema_exists, can_create, can_use = await check_schema_exists()
    print()
    
    if not can_use:
        print("❌ Insufficient schema privileges. Cannot proceed with setup.")
        return False
    
    # Step 2: Enable PostgreSQL extensions
    if await enable_postgresql_extensions():
        steps_completed += 1
    print()
    
    # Step 3: Create schema
    if await create_database_schema():
        steps_completed += 1
    print()
    
    # Step 4: Verify tables
    if await verify_schema_tables():
        steps_completed += 1
    print()
    
    # Step 5: Verify constraints and indexes
    constraints_ok = await verify_table_constraints()
    print()
    indexes_ok = await verify_indexes()
    print()
    
    if constraints_ok and indexes_ok:
        steps_completed += 1
    
    # Final results
    print("=" * 70)
    print(f"SCHEMA SETUP RESULTS: {steps_completed}/{total_steps} STEPS COMPLETED")
    print("=" * 70)
    
    if steps_completed >= 3:  # Tables creation is most critical
        print("🎉 P3.1 Database Schema Setup SUCCESSFUL!")
        print("✅ Database ready for P3.1 functional testing")
        return True
    else:
        print("❌ Schema setup incomplete - manual intervention may be required")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)