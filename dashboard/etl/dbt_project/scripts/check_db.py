import psycopg2

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host="52.141.50.106",
            database="home360-dev",
            user="home360_reader",
            password="home360pass123",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    conn = connect_to_db()
    if conn:
        try:
            cur = conn.cursor()

            # Get database version
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"Database version: {version[0]}")

            # List schemas
            cur.execute("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
                ORDER BY schema_name;
            """)
            schemas = cur.fetchall()
            print("\nAvailable schemas:")
            for schema in schemas:
                print(f"- {schema[0]}")

                # List tables in each schema
                cur.execute(f"""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = '{schema[0]}'
                    ORDER BY table_name;
                """)
                tables = cur.fetchall()
                for table in tables:
                    print(f"  - {table[0]}")

            cur.close()
        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    main()