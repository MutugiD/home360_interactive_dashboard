import psycopg2
from psycopg2 import sql
import sys

def connect_db():
    try:
        conn = psycopg2.connect(
            host="52.141.50.106",
            database="home360-dev",
            user="home360_reader",
            password="home360123",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_schemas(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
        ORDER BY schema_name;
    """)
    return [row[0] for row in cur.fetchall()]

def get_tables(conn, schema):
    cur = conn.cursor()
    cur.execute(sql.SQL("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY table_name;
    """), [schema])
    return [row[0] for row in cur.fetchall()]

def get_table_info(conn, schema, table):
    cur = conn.cursor()
    cur.execute(sql.SQL("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
    """), [schema, table])
    return cur.fetchall()

def main():
    conn = connect_db()
    print("Successfully connected to database!")

    print("\nDatabase version:")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(cur.fetchone()[0])

    print("\nAvailable schemas:")
    schemas = get_schemas(conn)
    for schema in schemas:
        print(f"\nSchema: {schema}")
        tables = get_tables(conn, schema)
        for table in tables:
            print(f"\n  Table: {table}")
            columns = get_table_info(conn, schema, table)
            for col in columns:
                col_name, data_type, max_length = col
                if max_length:
                    print(f"    {col_name}: {data_type}({max_length})")
                else:
                    print(f"    {col_name}: {data_type}")

    conn.close()

if __name__ == "__main__":
    main()