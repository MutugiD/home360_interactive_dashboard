# Task_Flow_Effectiveness.py

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
# 8) How many homeowners / family members are creating tasks?
# ────────────────────────────────────────────────────────────────────────────

def get_task_creators_by_role():
    """
    Count distinct users with role 'Admin' or 'Family' in HomeMember
    who appear as task creators in Task."createdByUserId".
    """
    query = """
    WITH creators AS (
      SELECT DISTINCT t."createdByUserId" AS user_id
        FROM public."Task" t
       WHERE t."createdByUserId" IS NOT NULL
    )
    SELECT
      COUNT(DISTINCT hm."userId") FILTER (WHERE hm."role" = 'Admin')  AS homeowner_creators,
      COUNT(DISTINCT hm."userId") FILTER (WHERE hm."role" = 'Family') AS family_creators
    FROM public."HomeMember" hm
    JOIN creators c
      ON c.user_id = hm."userId"
    WHERE hm."role" IN ('Admin', 'Family');
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 9) How many tasks are created per home / per user?
# ────────────────────────────────────────────────────────────────────────────

def get_tasks_per_home_per_user():
    """
    1. Tasks per home: group Task by Task."homeId".
    2. Tasks per user: group Task by Task."createdByUserId".
    """
    # Per-home
    per_home_query = """
    SELECT
      t."homeId"        AS home_id,
      COUNT(*)          AS tasks_created
    FROM public."Task" t
    WHERE t."homeId" IS NOT NULL
    GROUP BY t."homeId"
    ORDER BY tasks_created DESC;
    """
    # Per-user
    per_user_query = """
    SELECT
      t."createdByUserId" AS user_id,
      COUNT(*)            AS tasks_created
    FROM public."Task" t
    WHERE t."createdByUserId" IS NOT NULL
    GROUP BY t."createdByUserId"
    ORDER BY tasks_created DESC;
    """
    per_home = execute_query(per_home_query)
    per_user = execute_query(per_user_query)
    return per_home, per_user


# ────────────────────────────────────────────────────────────────────────────
# 10) How many staff members are checking tasks daily?
# ────────────────────────────────────────────────────────────────────────────

def get_daily_staff_task_checks():
    """
    Count distinct staff users who have a 'check' action in TaskActionDetails
    during the current day.
    """
    query = """
    SELECT
      COUNT(DISTINCT tad."actionByUserId") AS staff_checks_today
    FROM public."TaskActionDetails" tad
    JOIN public."HomeMember" hm
      ON hm."userId" = tad."actionByUserId"
    WHERE hm."role" = 'Staff'
      AND tad."action" = 'check'
      AND tad."createdAt" >= DATE_TRUNC('day', NOW())
      AND tad."createdAt" <  DATE_TRUNC('day', NOW() + INTERVAL '1 day');
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 11) What is the task completion rate by staff?
# ────────────────────────────────────────────────────────────────────────────

def get_task_completion_rate_by_staff():
    """
    Calculate:
      total_assigned_staff_tasks = number of TaskActionDetails rows with action = 'assign'
                                  where the actor's role is 'Staff'.
      total_completed_staff_tasks = number of TaskActionDetails rows with action = 'complete'
                                   where the actor's role is 'Staff'.

    Completion rate = completed / assigned * 100.
    """
    query = """
    WITH staff_assigned AS (
      SELECT DISTINCT tad."taskScheduleDetailsId" AS task_id, tad."actionByUserId" AS user_id
        FROM public."TaskActionDetails" tad
      JOIN public."HomeMember" hm
        ON hm."userId" = tad."actionByUserId"
      WHERE hm."role" = 'Staff'
        AND tad."action" = 'assign'
        AND tad."actionByUserId" IS NOT NULL
    ),
    staff_completed AS (
      SELECT DISTINCT tad."taskScheduleDetailsId" AS task_id, tad."actionByUserId" AS user_id
        FROM public."TaskActionDetails" tad
      JOIN public."HomeMember" hm
        ON hm."userId" = tad."actionByUserId"
      WHERE hm."role" = 'Staff'
        AND tad."action" = 'complete'
        AND tad."actionByUserId" IS NOT NULL
    )
    SELECT
      COUNT(sa.*)      AS total_assigned_staff_tasks,
      COUNT(sc.*)      AS total_completed_staff_tasks,
      ROUND(
        CASE
          WHEN COUNT(sa.*) = 0 THEN 0
          ELSE (COUNT(sc.*)::decimal / COUNT(sa.*)) * 100
        END
      , 2)             AS pct_completed_by_staff
    FROM staff_assigned sa
    LEFT JOIN staff_completed sc
      ON sc."task_id" = sa."task_id"
     AND sc."user_id" = sa."user_id";
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# 12) What is the average delay in task completion (scheduled vs actual)?
# ────────────────────────────────────────────────────────────────────────────

def get_avg_task_completion_delay():
    """
    Compute average delay in hours between scheduled date (TaskScheduleDetails."taskDate")
    and actual completion (TaskScheduleDetails."completedAt").
    Only for tasks that were scheduled and completed.
    """
    query = """
    WITH scheduled AS (
      SELECT
        tsd."id"       AS schedule_id,
        tsd."taskId"   AS task_id,
        tsd."taskDate" AS scheduled_for,
        tsd."completedAt" AS completed_at
      FROM public."TaskScheduleDetails" tsd
      WHERE tsd."taskDate" IS NOT NULL
        AND tsd."completedAt" IS NOT NULL
    ),
    delays AS (
      SELECT
        s.schedule_id,
        EXTRACT(
          EPOCH FROM (s.completed_at - s.scheduled_for)
        ) / 3600.0                AS hours_delay
      FROM scheduled s
      WHERE s.completed_at >= s.scheduled_for
    )
    SELECT
      ROUND(AVG(hours_delay)::numeric, 2) AS avg_delay_hours
    FROM delays;
    """
    return execute_query(query)


# ────────────────────────────────────────────────────────────────────────────
# Main: Inspect Schemas and Run All Task‐Flow Metrics
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n▶ Initializing connection pool...")
    DatabaseConnection.initialize_pool()

    # Inspect columns of Task and related tables to confirm assumptions
    print("\n▶ Discovering public.\"Task\" columns:")
    task_cols = [c["column_name"] for c in list_table_columns("Task")]
    print(task_cols)

    print("\n▶ Discovering public.\"HomeMember\" columns:")
    hm_cols = [c["column_name"] for c in list_table_columns("HomeMember")]
    print(hm_cols)

    print("\n▶ Discovering public.\"TaskActionDetails\" columns:")
    tad_cols = [c["column_name"] for c in list_table_columns("TaskActionDetails")]
    print(tad_cols)

    print("\n▶ Discovering public.\"TaskScheduleDetails\" columns:")
    tsd_cols = [c["column_name"] for c in list_table_columns("TaskScheduleDetails")]
    print(tsd_cols)

    # 8) How many homeowners / family members are creating tasks?
    print("\n[8] Number of homeowner vs. family task creators:")
    try:
        creators = get_task_creators_by_role()
        print(creators)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 9) How many tasks are created per home / per user?
    print("\n[9] Tasks created per home and per user:")
    try:
        per_home, per_user = get_tasks_per_home_per_user()
        print("  • Tasks per home:")
        for row in per_home:
            print("    ", row)
        print("  • Tasks per user:")
        for row in per_user:
            print("    ", row)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 10) How many staff members are checking tasks daily?
    print("\n[10] Number of staff members checking tasks today:")
    try:
        staff_checks = get_daily_staff_task_checks()
        print(staff_checks)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 11) Task completion rate by staff
    print("\n[11] Task completion rate by staff:")
    try:
        completion_rate = get_task_completion_rate_by_staff()
        print(completion_rate)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 12) Average delay in task completion (hours)
    print("\n[12] Average delay in task completion (hours):")
    try:
        avg_delay = get_avg_task_completion_delay()
        print(avg_delay)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    DatabaseConnection.close_all_connections()
