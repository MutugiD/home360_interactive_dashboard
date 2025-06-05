# Invite_Flow_Effectiveness.py

from src.database import DatabaseConnection, execute_query

# ────────────────────────────────────────────────────────────────────────────
# Helper: Discover columns of a given table in public schema
# ────────────────────────────────────────────────────────────────────────────

def list_table_columns(table_name):
    """
    Return a list of column names for public."<table_name>".
    """
    query = """
    SELECT column_name
      FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name   = %s
     ORDER BY ordinal_position;
    """
    return execute_query(query, (table_name,))


# ────────────────────────────────────────────────────────────────────────────
# 13) Time Taken from Invite Sent to User Signup
# ────────────────────────────────────────────────────────────────────────────

def get_invite_to_signup_times():
    """
    For every invited user (HomeMember.userId), compute:
      invite_time   = HomeMember.createdAt
      signup_time   = User.createdAt
      hours_to_signup = difference in hours between signup_time and invite_time

    Only keep rows where signup_time >= invite_time, and order by
    invite_time descending (most recent first). Returns all rows.
    """
    query = """
    WITH invites AS (
      SELECT
        hm."userId"    AS invited_user_id,
        hm."createdAt" AS invite_time,
        u."createdAt"  AS signup_time
      FROM public."HomeMember" hm
      JOIN public."User" u
        ON u."id" = hm."userId"
      WHERE hm."userId" IS NOT NULL
    )
    SELECT
      invited_user_id,
      invite_time,
      signup_time,
      ROUND(
        EXTRACT(
          EPOCH FROM (signup_time - invite_time)
        ) / 3600.0
      , 2) AS hours_to_signup
    FROM invites
    WHERE signup_time >= invite_time   -- only keep non‐negative intervals
    ORDER BY invite_time DESC;
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# Main: Inspect Schema and Run Invite Flow Query
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n▶ Initializing connection pool...")
    DatabaseConnection.initialize_pool()

    # Inspect columns to confirm assumptions
    print("\n▶ Discovering public.\"HomeMember\" columns:")
    hm_cols = [c["column_name"] for c in list_table_columns("HomeMember")]
    print(hm_cols)

    print("\n▶ Discovering public.\"User\" columns:")
    user_cols = [c["column_name"] for c in list_table_columns("User")]
    print(user_cols)

    # 13) Time Taken from Invite Sent to User Signup
    print("\n[13] Time from invite sent (HomeMember.createdAt) to user signup (User.createdAt) for ALL invites:")
    try:
        rows = get_invite_to_signup_times()
        if rows:
            for r in rows:
                print(r)
        else:
            print("   • No invited users who have signed up found.")
    except Exception as e:
        print(f"   ✖ Error: {e}")

    DatabaseConnection.close_all_connections()
