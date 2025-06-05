from src.database import DatabaseConnection, execute_query

# ────────────────────────────────────────────────────────────────────────────
# 1) Total Users (App Downloads)
# ────────────────────────────────────────────────────────────────────────────

def get_total_users():
    """
    Return a single row with the total number of users in public."User".
    """
    query = """
    SELECT COUNT(*) AS total_users
      FROM public."User";
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 2) Total Logged-In Users
# ────────────────────────────────────────────────────────────────────────────

def get_logged_in_users():
    """
    Count distinct users who have ever logged in (activityType='login').
    """
    query = """
    SELECT COUNT(DISTINCT "userId") AS logged_in_users
      FROM public."UserActivity"
     WHERE "activityType" = 'login';
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 3) Of Logged-In Users: With vs. Without a Home
# ────────────────────────────────────────────────────────────────────────────

def get_logged_in_users_with_and_without_home():
    """
    Among all distinct users who have ever logged in:
      • users_with_home    = count of those appearing in HomeMember (any role).
      • users_without_home = count of those not appearing in HomeMember.
    """
    query = """
    WITH logged_in_users AS (
      SELECT DISTINCT "userId" AS user_id
        FROM public."UserActivity"
       WHERE "activityType" = 'login'
    )
    SELECT
      COUNT(l.user_id) FILTER (WHERE hm."homeId" IS NOT NULL)   AS users_with_home,
      COUNT(l.user_id) FILTER (WHERE hm."homeId" IS NULL)       AS users_without_home
    FROM logged_in_users l
    LEFT JOIN public."HomeMember" hm
      ON hm."userId" = l.user_id;
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 4) Of Users Without a Home: Created vs. Dropped Off
# ────────────────────────────────────────────────────────────────────────────

def get_creation_vs_dropoff():
    """
    1. logged_in_users: all distinct users with any 'login' event.
    2. logged_no_home: those users who do NOT appear in HomeMember at all.
    3. Among logged_no_home:
         • created_home       = count of users who appear in HomeMember with role='Admin'.
         • left_without_home  = count of users who do NOT appear as role='Admin'.
    """
    query = """
    WITH logged_in_users AS (
      SELECT DISTINCT "userId" AS user_id
        FROM public."UserActivity"
       WHERE "activityType" = 'login'
    ),
    logged_no_home AS (
      SELECT l.user_id
        FROM logged_in_users l
   LEFT JOIN public."HomeMember" hm
          ON hm."userId" = l.user_id
       WHERE hm."homeId" IS NULL
    )
    SELECT
      COUNT(u.user_id) FILTER (
          WHERE EXISTS (
            SELECT 1
              FROM public."HomeMember" hm2
             WHERE hm2."userId" = u.user_id
               AND hm2."role" = 'Admin'
          )
      ) AS created_home,
      COUNT(u.user_id) FILTER (
          WHERE NOT EXISTS (
            SELECT 1
              FROM public."HomeMember" hm3
             WHERE hm3."userId" = u.user_id
               AND hm3."role" = 'Admin'
          )
      ) AS left_without_home
    FROM logged_no_home u;
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 5) Of Those Who Created a Home: Invite Counts by Role
# ────────────────────────────────────────────────────────────────────────────

def get_invites_separated_by_role():
    """
    1. home_owners: distinct homeId from HomeMember where role = 'Admin'.
    2. For each home_id, count:
         • family_invited_count = number of HomeMember rows with role = 'Family'.
         • staff_invited_count  = number of HomeMember rows with role = 'Staff'.
    """
    query = """
    WITH home_owners AS (
      SELECT DISTINCT "homeId" AS home_id
        FROM public."HomeMember"
       WHERE "role" = 'Admin'
    )
    SELECT
      ho.home_id,
      COUNT(hm_fam."userId") FILTER (WHERE hm_fam."role" = 'Family') AS family_invited_count,
      COUNT(hm_staff."userId") FILTER (WHERE hm_staff."role" = 'Staff') AS staff_invited_count
    FROM home_owners ho
    LEFT JOIN public."HomeMember" hm_fam
      ON hm_fam."homeId" = ho.home_id AND hm_fam."role" = 'Family'
    LEFT JOIN public."HomeMember" hm_staff
      ON hm_staff."homeId" = ho.home_id AND hm_staff."role" = 'Staff'
    GROUP BY ho.home_id
    ORDER BY ho.home_id;
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 6) Of Invited Members: Signup Rates by Role
# ────────────────────────────────────────────────────────────────────────────

def get_invited_signup_rate_for(role):
    """
    1. invited_by_role: distinct userId from HomeMember where role = given role.
    2. total_invited = count of those user IDs.
    3. signed_up     = count of those IDs that appear in public."User".
    """
    query = """
    WITH invited_by_role AS (
      SELECT DISTINCT "userId" AS invited_user_id
        FROM public."HomeMember"
       WHERE "role" = %s
         AND "userId" IS NOT NULL
    )
    SELECT
      COUNT(i.invited_user_id)                           AS total_invited,
      COUNT(u."id")                                      AS signed_up
    FROM invited_by_role i
    LEFT JOIN public."User" u
      ON u."id" = i.invited_user_id;
    """
    return execute_query(query, (role,))


# ────────────────────────────────────────────────────────────────────────────
# 7) Main: Execute and Print All Funnel Metrics
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # This part needs to be updated if DatabaseConnection is not directly available
    # For now, assuming src.database.DatabaseConnection is the path if run standalone
    # Or, this main block might need to import initialize_pool from src.database as well.
    # For simplicity in this refactoring step, I'll assume direct imports work or are handled
    # by how this script was originally run.
    # The primary goal is for app.py to import these functions correctly.

    # To run standalone, you'd need:
    # from src.database import DatabaseConnection, initialize_pool, close_all_connections

    print("\n▶ Initializing connection pool...")
    DatabaseConnection.initialize_pool()

    # 1) Total Users (App Downloads)
    print("\n[1] Total Users (App Downloads):")
    try:
        print(get_total_users())
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 2) Total Logged-In Users (all time)
    print("\n[2] Total Logged-In Users:")
    try:
        print(get_logged_in_users())
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 3) Of Logged-In Users → With vs. Without Home
    print("\n[3] Of Logged-In Users: With vs. Without Home:")
    try:
        print(get_logged_in_users_with_and_without_home())
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 4) Of Users Without a Home → Created vs. Dropped Off
    print("\n[4] Of Users Without a Home: Created vs. Left Without Creating Home:")
    try:
        print(get_creation_vs_dropoff())
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 5) Of Those Who Created a Home → Invite Counts (Family vs Staff)
    print("\n[5] Of Those Who Created a Home: Invite Counts (Family vs Staff):")
    try:
        print(get_invites_separated_by_role())
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 6) Of Invited Members → Signup Rates for Family and Staff
    for role in ('Family', 'Staff'):
        print(f"\n[6] Signup Rates for Invited {role} Members:")
        try:
            result = get_invited_signup_rate_for(role)
            if result:
                total = result[0]['total_invited']
                signed = result[0]['signed_up']
                pct = round((signed / total * 100) if total else 0, 2)
                print({
                    'role': role,
                    'total_invited': total,
                    'signed_up': signed,
                    'pct_signed_up': f"{pct}%"
                })
            else:
                print("   (no invited users for this role)")
        except Exception as e:
            print(f"   ✖ Error: {e}")

    DatabaseConnection.close_all_connections()