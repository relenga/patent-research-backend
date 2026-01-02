-- PostgreSQL Database Setup Commands for P3.1
-- Run these commands as a PostgreSQL superuser (postgres user)

-- Connect to the patent_intelligence database
\c patent_intelligence;

-- Grant CREATE privilege on public schema to patent_user
GRANT CREATE ON SCHEMA public TO patent_user;

-- Optional: Grant additional privileges that may be needed
GRANT USAGE ON SCHEMA public TO patent_user;

-- Create the UUID extension if it doesn't exist (as superuser)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify the privileges were granted
SELECT 
    schemaname,
    has_schema_privilege('patent_user', schemaname, 'CREATE') as can_create,
    has_schema_privilege('patent_user', schemaname, 'USAGE') as can_use
FROM pg_namespace 
JOIN information_schema.schemata ON nspname = schema_name 
WHERE schema_name = 'public';

-- Show current user and confirm connection
SELECT current_user, current_database();