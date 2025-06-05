# script_engagement_retention.py

from src.database import execute_query

# ────────────────────────────────────────────────────────────────────────────
# Helper A: Discover columns in public."User"
# ────────────────────────────────────────────────────────────────────────────

def list_user_columns():
    """
    Returns a list of columns in public."User".
    """
    query = """
    SELECT column_name
      FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'User'
     ORDER BY ordinal_position;
    """
    return execute_query(query)

# ────────────────────────────────────────────────────────────────────────────
# Helper B: Discover columns in public."UserActivity"
# ────────────────────────────────────────────────────────────────────────────

def list_useractivity_columns():
    """
    Returns a list of columns in public."UserActivity".
    """
    query = """
    SELECT column_name
      FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'UserActivity'
     ORDER BY ordinal_position;
    """
    return execute_query(query)

# ────────────────────────────────────────────────────────────────────────────
# 0) Sanity Check: Count recent login events
# ────────────────────────────────────────────────────────────────────────────

def count_recent_logins(days_back=30):
    """
    Returns the number of 'login' events in the last `days_back` days.
    """
    query = """
    SELECT COUNT(*) AS recent_login_count
      FROM public."UserActivity"
     WHERE "activityType" = 'login'
       AND "createdAt" >= NOW() - INTERVAL '%s days';
    """
    return execute_query(query, (days_back,))

# ────────────────────────────────────────────────────────────────────────────
# 5) DAU / WAU / MAU (grouped by role if available)
# ────────────────────────────────────────────────────────────────────────────

def get_dau_wau_mau(days_back=30, role_col=None):
    """
    Calculate DAU, WAU, MAU over the past `days_back` days.
    If `role_col` is provided (e.g., "userRole"), group by that column;
    otherwise, compute for all users.
    """
    if role_col:
        # Grouping by role_col
        query = f"""
        WITH ua AS (
          SELECT
            ua."userId",
            DATE_TRUNC('day', ua."createdAt")   AS day,
            DATE_TRUNC('week', ua."createdAt")  AS week,
            DATE_TRUNC('month', ua."createdAt") AS month,
            u."{role_col}"                       AS user_role
          FROM public."UserActivity" ua
          JOIN public."User" u
            ON u."id" = ua."userId"
         WHERE ua."activityType" = 'login'
           AND ua."createdAt" >= (NOW() - INTERVAL '%s days')
        ),
        daily AS (
          SELECT
            day::date               AS period,
            user_role,
            COUNT(DISTINCT "userId") AS dau
          FROM ua
         GROUP BY day, user_role
        ),
        weekly AS (
          SELECT
            week::date              AS period,
            user_role,
            COUNT(DISTINCT "userId") AS wau
          FROM ua
         GROUP BY week, user_role
        ),
        monthly AS (
          SELECT
            month::date             AS period,
            user_role,
            COUNT(DISTINCT "userId") AS mau
          FROM ua
         GROUP BY month, user_role
        )
        SELECT
          d.period,
          d.user_role,
          d.dau,
          COALESCE(w.wau, 0) AS wau,
          COALESCE(m.mau, 0) AS mau
        FROM daily d
        LEFT JOIN weekly w
          ON w.period = DATE_TRUNC('week', d.period)::date
         AND w.user_role = d.user_role
        LEFT JOIN monthly m
          ON m.period = DATE_TRUNC('month', d.period)::date
         AND m.user_role = d.user_role
        ORDER BY d.period DESC, d.user_role;
        """
        return execute_query(query, (days_back,))
    else:
        # No role grouping
        query = """
        WITH ua AS (
          SELECT
            ua."userId",
            DATE_TRUNC('day', ua."createdAt")   AS day,
            DATE_TRUNC('week', ua."createdAt")  AS week,
            DATE_TRUNC('month', ua."createdAt") AS month
          FROM public."UserActivity" ua
         WHERE ua."activityType" = 'login'
           AND ua."createdAt" >= (NOW() - INTERVAL '%s days')
        ),
        daily AS (
          SELECT
            day::date               AS period,
            COUNT(DISTINCT "userId") AS dau
          FROM ua
         GROUP BY day
        ),
        weekly AS (
          SELECT
            week::date              AS period,
            COUNT(DISTINCT "userId") AS wau
          FROM ua
         GROUP BY week
        ),
        monthly AS (
          SELECT
            month::date             AS period,
            COUNT(DISTINCT "userId") AS mau
          FROM ua
         GROUP BY month
        )
        SELECT
          d.period,
          d.dau,
          COALESCE(w.wau, 0) AS wau,
          COALESCE(m.mau, 0) AS mau
        FROM daily d
        LEFT JOIN weekly w
          ON w.period = DATE_TRUNC('week', d.period)::date
        LEFT JOIN monthly m
          ON m.period = DATE_TRUNC('month', d.period)::date
        ORDER BY d.period DESC;
        """
        return execute_query(query, (days_back,))

# ────────────────────────────────────────────────────────────────────────────
# 6) Average Session Length (if available)
# ────────────────────────────────────────────────────────────────────────────

def get_average_session_length():
    """
    Compute the average session duration, if a duration column exists in UserActivity.
    We check for 'sessionDuration' or 'duration' in the schema. Otherwise, skip.
    """
    # Introspect UserActivity columns
    cols = [row["column_name"] for row in list_useractivity_columns()]

    # Look for plausible session-duration columns
    duration_col = None
    for candidate in ("sessionDuration", "duration", "session_length", "length"):
        if candidate in cols:
            duration_col = candidate
            break

    if not duration_col:
        # No duration column found
        return None

    # Calculate average session length (in seconds)
    query = f"""
    SELECT
      ROUND(AVG(ua."{duration_col}")::numeric, 2) AS avg_session_seconds
    FROM public."UserActivity" ua
   WHERE ua."activityType" = 'session_end';
    """
    return execute_query(query)

# ────────────────────────────────────────────────────────────────────────────
# 7) Retention Rates (Day 1, Day 3, Day 7, Day 30)
# ────────────────────────────────────────────────────────────────────────────

def get_retention_rates():
    """
    For each signup cohort (grouped by signup day), calculate the percentage of users
    who return within Day 1, Day 3, Day 7, and Day 30 windows.
    ("Return within N days" means: activity_day >= signup_day + (N-1) days
     AND activity_day < signup_day + N days.)
    """
    query = """
    WITH cohorts AS (
      SELECT
        "id" AS user_id,
        DATE_TRUNC('day', "createdAt") AS signup_day
      FROM public."User"
    ), activity AS (
      SELECT DISTINCT
        ua."userId" AS user_id,
        DATE_TRUNC('day', ua."createdAt") AS activity_day
      FROM public."UserActivity" ua
     WHERE ua."activityType" = 'login'
    ), flagged AS (
      SELECT
        c.signup_day AS cohort_date,
        COUNT(DISTINCT CASE
            WHEN a.activity_day >= (c.signup_day + INTERVAL '1 day')
             AND a.activity_day <  (c.signup_day + INTERVAL '2 day')
          THEN c.user_id END) AS day1_retained,
        COUNT(DISTINCT CASE
            WHEN a.activity_day >= (c.signup_day + INTERVAL '3 day')
             AND a.activity_day <  (c.signup_day + INTERVAL '4 day')
          THEN c.user_id END) AS day3_retained,
        COUNT(DISTINCT CASE
            WHEN a.activity_day >= (c.signup_day + INTERVAL '7 day')
             AND a.activity_day <  (c.signup_day + INTERVAL '8 day')
          THEN c.user_id END) AS day7_retained,
        COUNT(DISTINCT CASE
            WHEN a.activity_day >= (c.signup_day + INTERVAL '30 day')
             AND a.activity_day <  (c.signup_day + INTERVAL '31 day')
          THEN c.user_id END) AS day30_retained,
        COUNT(DISTINCT c.user_id) AS cohort_size
      FROM cohorts c
      LEFT JOIN activity a
        ON a.user_id = c.user_id
       AND a.activity_day > c.signup_day
      GROUP BY c.signup_day
    )
    SELECT
      cohort_date::date                                             AS cohort_date,
      ROUND((day1_retained::numeric / GREATEST(cohort_size,1)) * 100, 2)  AS pct_day1,
      ROUND((day3_retained::numeric / GREATEST(cohort_size,1)) * 100, 2)  AS pct_day3,
      ROUND((day7_retained::numeric / GREATEST(cohort_size,1)) * 100, 2)  AS pct_day7,
      ROUND((day30_retained::numeric / GREATEST(cohort_size,1)) * 100, 2) AS pct_day30
    FROM flagged
    ORDER BY cohort_date DESC;
    """
    return execute_query(query)

# ────────────────────────────────────────────────────────────────────────────
# 8) Drill‐Down Example: Users Who Logged In but Never Created a Home
# ────────────────────────────────────────────────────────────────────────────

def list_logged_in_no_home():
    """
    Returns a list of users (id, firstName, lastName) who have ever logged in
    but never appear in HomeMember (i.e., did not create or join any home).
    """
    query = """
    WITH logged_in_users AS (
      SELECT DISTINCT "userId" AS user_id
        FROM public."UserActivity"
       WHERE "activityType" = 'login'
    )
    SELECT
      u."id"        AS user_id,
      u."firstName" AS first_name,
      u."lastName"  AS last_name
    FROM logged_in_users li
    LEFT JOIN public."HomeMember" hm
      ON hm."userId" = li.user_id
    JOIN public."User" u
      ON u."id" = li.user_id
    WHERE hm."userId" IS NULL;
    """
    return execute_query(query)

# ────────────────────────────────────────────────────────────────────────────
# Main: Execute All Metrics and Recommendations
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n▶ Initializing connection pool...")
    DatabaseConnection.initialize_pool()

    # 0) Sanity Check: Recent login count
    print("\n▶ [0] Recent 'login' events (last 30 days):")
    try:
        recent_logins = count_recent_logins(days_back=30)
        print(recent_logins)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # Determine if a 'role' column exists in public."User"
    print("\n▶ Discovering User table columns:")
    user_cols = [c["column_name"] for c in list_user_columns()]
    print(user_cols)

    # If there's any candidate for a role field, pick it; otherwise, None
    role_candidates = ["role", "userRole"]
    role_col = next((c for c in role_candidates if c in user_cols), None)
    if role_col:
        print(f"\n▶ Using role column: {role_col}")
    else:
        print("\n▶ No role column found; aggregating DAU/WAU/MAU across all users.")

    # 5) DAU / WAU / MAU (last 30 days)
    print("\n[5] DAU / WAU / MAU (last 30 days):")
    try:
        dau_wau_mau_rows = get_dau_wau_mau(days_back=30, role_col=role_col)
        if dau_wau_mau_rows:
            for r in dau_wau_mau_rows:
                print(r)
        else:
            print("   • No login events found in the past 30 days.")
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 6) Average Session Length (if available)
    print("\n[6] Average Session Length (all users):")
    try:
        avg_session = get_average_session_length()
        if avg_session is None:
            print("   • No duration column found in UserActivity; skipping.")
        else:
            print(avg_session)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 7) Retention Rates (Day 1, Day 3, Day 7, Day 30)
    print("\n[7] Retention Rates by Signup Cohort (all users):")
    try:
        retention_rows = get_retention_rates()
        if retention_rows:
            for r in retention_rows:
                print(r)
        else:
            print("   • No retention data found (no logins after signup).")
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 8) Drill-Down: Users who logged in but never created/joined a home
    print("\n[8] Users who logged in but never created or joined a Home:")
    try:
        no_home_users = list_logged_in_no_home()
        if no_home_users:
            for u in no_home_users:
                print(u)
        else:
            print("   • No such users found (everyone who logged in belongs to a home).")
    except Exception as e:
        print(f"   ✖ Error: {e}")

    DatabaseConnection.close_all_connections()
