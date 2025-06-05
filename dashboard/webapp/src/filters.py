from datetime import datetime, timedelta
from typing import Optional, Dict, Any

def build_date_filter(date_range: str = "all", start_date: str = None, end_date: str = None) -> tuple[str, tuple]:
    """
    Build date filter SQL and parameters
    Args:
        date_range: "all", "7days", "30days", "custom"
        start_date: "YYYY-MM-DD" for custom range
        end_date: "YYYY-MM-DD" for custom range
    Returns:
        (sql_where_clause, parameters)
    """
    if date_range == "all":
        return "", ()

    if date_range == "7days":
        cutoff_date = datetime.now() - timedelta(days=7)
        return 'AND "createdAt" >= %s', (cutoff_date,)

    if date_range == "30days":
        cutoff_date = datetime.now() - timedelta(days=30)
        return 'AND "createdAt" >= %s', (cutoff_date,)

    if date_range == "custom" and start_date and end_date:
        return 'AND "createdAt" >= %s AND "createdAt" <= %s', (start_date, end_date)

    return "", ()

def build_role_filter(role: str = "all") -> tuple[str, tuple]:
    """
    Build role filter SQL and parameters
    Args:
        role: "all", "Admin", "Family", "Staff"
    Returns:
        (sql_where_clause, parameters)
    """
    if role == "all":
        return "", ()

    return 'AND hm."role" = %s', (role,)

def build_home_filter(home_id: int = None) -> tuple[str, tuple]:
    """
    Build home filter SQL and parameters
    Args:
        home_id: specific home ID to filter by
    Returns:
        (sql_where_clause, parameters)
    """
    if not home_id:
        return "", ()

    return 'AND "homeId" = %s', (home_id,)

def build_user_filter(user_id: int = None) -> tuple[str, tuple]:
    """
    Build user filter SQL and parameters
    Args:
        user_id: specific user ID to filter by
    Returns:
        (sql_where_clause, parameters)
    """
    if not user_id:
        return "", ()

    return 'AND "userId" = %s', (user_id,)

def combine_filters(**filters) -> tuple[str, tuple]:
    """
    Combine multiple filters into a single SQL clause
    Args:
        **filters: keyword arguments for different filter types
    Returns:
        (combined_sql_where_clause, combined_parameters)
    """
    where_clauses = []
    parameters = []

    # Date filter
    if 'date_range' in filters:
        date_sql, date_params = build_date_filter(
            filters.get('date_range', 'all'),
            filters.get('start_date'),
            filters.get('end_date')
        )
        if date_sql:
            where_clauses.append(date_sql)
            parameters.extend(date_params)

    # Role filter
    if 'role' in filters:
        role_sql, role_params = build_role_filter(filters.get('role', 'all'))
        if role_sql:
            where_clauses.append(role_sql)
            parameters.extend(role_params)

    # Home filter
    if 'home_id' in filters:
        home_sql, home_params = build_home_filter(filters.get('home_id'))
        if home_sql:
            where_clauses.append(home_sql)
            parameters.extend(home_params)

    # User filter
    if 'user_id' in filters:
        user_sql, user_params = build_user_filter(filters.get('user_id'))
        if user_sql:
            where_clauses.append(user_sql)
            parameters.extend(user_params)

    combined_sql = ' '.join(where_clauses)
    return combined_sql, tuple(parameters)

def parse_request_filters(request) -> Dict[str, Any]:
    """
    Parse filters from Flask request object
    Args:
        request: Flask request object
    Returns:
        Dictionary of parsed filters
    """
    filters = {}

    # Date range filter
    date_range = request.args.get('date_range', 'all')
    filters['date_range'] = date_range

    if date_range == 'custom':
        filters['start_date'] = request.args.get('start_date')
        filters['end_date'] = request.args.get('end_date')

    # Role filter
    role = request.args.get('role', 'all')
    filters['role'] = role

    # Home ID filter
    home_id = request.args.get('home_id')
    if home_id and home_id.isdigit():
        filters['home_id'] = int(home_id)

    # User ID filter
    user_id = request.args.get('user_id')
    if user_id and user_id.isdigit():
        filters['user_id'] = int(user_id)

    return filters