import os
from psycopg2 import pool
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────────────────────────
# CORE: DatabaseConnection & execute_query
# ────────────────────────────────────────────────────────────────────────────

load_dotenv()  # if you store DB_HOST, DB_NAME, etc. in a .env file

class DatabaseConnection:
    _connection_pool = None

    @classmethod
    def initialize_pool(cls):
        """Initialize a SimpleConnectionPool if not already done."""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pool.SimpleConnectionPool(
                    minconn=int(os.getenv('DB_MIN_CONN', '1')),
                    maxconn=int(os.getenv('DB_MAX_CONN', '10')),
                    host=os.getenv('DB_HOST'),
                    database=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    port=os.getenv('DB_PORT')
                )
                print("🟢 Connection pool created")
            except Exception as e:
                print(f"🔴 Error creating connection pool: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Get one connection from the pool (initializes if needed)."""
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        """Return a connection back to the pool."""
        if cls._connection_pool is not None and conn is not None:
            cls._connection_pool.putconn(conn)

    @classmethod
    def close_all_connections(cls):
        """Close all connections in the pool."""
        if cls._connection_pool is not None:
            try:
                cls._connection_pool.closeall()
                print("🔴 All connections closed")
            except Exception as e:
                print(f"🔴 Error closing connection pool: {e}")
            finally:
                cls._connection_pool = None


def execute_query(query: str, params: tuple = None):
    """
    Execute a read-only SELECT query and return a list of dicts.
    Make sure no CREATE/INSERT/UPDATE/DELETE statements appear here.
    """
    conn = None
    try:
        conn = DatabaseConnection.get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"🔴 Error executing query: {e}")
        raise
    finally:
        if conn:
            DatabaseConnection.return_connection(conn)

if __name__ == '__main__':
    print("Testing database connection...")
    try:
        DatabaseConnection.initialize_pool()
        # Test a simple query
        test_query = "SELECT 1 as test_column;"
        result = execute_query(test_query)
        print(f"Test query result: {result}")
        if result and result[0]['test_column'] == 1:
            print("Database connection successful!")
        else:
            print("Database connection test failed.")
    except Exception as e:
        print(f"An error occurred during database test: {e}")
    finally:
        DatabaseConnection.close_all_connections()
