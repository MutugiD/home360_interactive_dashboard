from src.database import DatabaseConnection, execute_query

def explore_database_schema():
    """Explore the database schema to understand available tables and columns"""

    # Get all tables
    tables_query = """
    SELECT table_name, table_schema
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """

    tables = execute_query(tables_query)
    print("Available tables:")
    for table in tables:
        print(f"  - {table['table_name']}")

    # Get columns for key tables
    key_tables = ['User', 'HomeMember', 'Task', 'UserActivity', 'Home']

    for table_name in key_tables:
        print(f"\n--- Columns for {table_name} ---")
        columns_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position;
        """
        try:
            columns = execute_query(columns_query, (table_name,))
            for col in columns:
                print(f"  {col['column_name']} ({col['data_type']}) - {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        except Exception as e:
            print(f"  Error: {e}")

    # Sample data from key tables - using correct column names
    print("\n--- Sample User data (first 3 rows) ---")
    try:
        users = execute_query('SELECT "id", "firstName", "lastName", "name", "createdAt", "countryCode" FROM public."User" LIMIT 3;')
        for user in users:
            print(f"  {user}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- Sample HomeMember data (first 5 rows) ---")
    try:
        home_members = execute_query('SELECT "userId", "homeId", "role", "createdAt" FROM public."HomeMember" LIMIT 5;')
        for hm in home_members:
            print(f"  {hm}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- Sample Home data (first 3 rows) ---")
    try:
        homes = execute_query('SELECT "id", "name", "createdAt" FROM public."Home" LIMIT 3;')
        for home in homes:
            print(f"  {home}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n--- Available User Roles ---")
    try:
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember";')
        for role in roles:
            print(f"  - {role['role']}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    DatabaseConnection.initialize_pool()
    try:
        explore_database_schema()
    finally:
        DatabaseConnection.close_all_connections()