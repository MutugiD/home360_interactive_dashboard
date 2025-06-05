from flask import Flask, render_template, jsonify, request
import os
import atexit
from dotenv import load_dotenv

# Database utilities
from src.database import DatabaseConnection, execute_query # Changed import
from src.filters import parse_request_filters, combine_filters

from src.signup_funnel import (
    get_total_users,
    get_logged_in_users,
    get_logged_in_users_with_and_without_home,
    get_creation_vs_dropoff,
    get_invites_separated_by_role,
    get_invited_signup_rate_for
)

from src.engagement_retention import (
    count_recent_logins,
    get_dau_wau_mau,
    get_average_session_length,
    get_retention_rates
)

from src.invite_flow import (
    get_invite_to_signup_times
)

from src.task_flow_effectiveness import (
    get_task_creators_by_role,
    get_tasks_per_home_per_user,
    get_daily_staff_task_checks,
    get_task_completion_rate_by_staff,
    get_avg_task_completion_delay
)

from src.meals_feature import (
    get_completed_meal_planners,
    get_recipe_search_count,
    get_add_from_search_count,
    get_add_own_recipe_counts
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize and close database connection pool
DatabaseConnection.initialize_pool() # Changed call
atexit.register(DatabaseConnection.close_all_connections) # Changed call

# Helper function to get filtered data
def get_filtered_metrics(filters=None):
    """Get metrics with optional filtering"""
    try:
        # For now, basic metrics don't support complex filtering
        # This would need to be implemented in individual query functions
        total_users_data = get_total_users()
        new_users_data = count_recent_logins()

        num_total_users = total_users_data[0]['total_users'] if total_users_data and total_users_data[0] else 0
        num_new_users = new_users_data[0]['recent_login_count'] if new_users_data and new_users_data[0] else 0

        return {
            'total_users': num_total_users,
            'new_users': num_new_users
        }
    except Exception as e:
        print(f"Error in get_filtered_metrics: {e}")
        return {'total_users': 0, 'new_users': 0}

@app.route('/')
def index():
    try:
        filters = parse_request_filters(request)
        metrics = get_filtered_metrics(filters)
        growth_trend_data = get_dau_wau_mau()

        # Get available filter options
        homes = execute_query('SELECT "id", "name" FROM public."Home" ORDER BY "name" LIMIT 50;')
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember" ORDER BY "role";')

        return render_template('index.html',
                             metrics=metrics,
                             growth_trend=growth_trend_data,
                             user_distribution=[],
                             homes=homes,
                             roles=roles,
                             current_filters=filters)
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('index.html',
                             metrics={'total_users': 0, 'new_users': 0},
                             growth_trend=[],
                             user_distribution=[],
                             homes=[],
                             roles=[],
                             current_filters={})

@app.route('/signup-funnel')
def signup_funnel_page():
    try:
        filters = parse_request_filters(request)

        # Combining multiple metrics for a funnel view
        funnel_data = {
            "total_users_app_downloads": get_total_users(),
            "total_logged_in": get_logged_in_users(),
            "logged_in_with_without_home": get_logged_in_users_with_and_without_home(),
            "home_creation_vs_dropoff": get_creation_vs_dropoff(),
            "invites_by_home_owners": get_invites_separated_by_role(),
            "signup_rate_invited_family": get_invited_signup_rate_for(role='Family'),
            "signup_rate_invited_staff": get_invited_signup_rate_for(role='Staff')
        }

        # Get filter options
        homes = execute_query('SELECT "id", "name" FROM public."Home" ORDER BY "name" LIMIT 50;')
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember" ORDER BY "role";')

        return render_template('signup_funnel.html',
                             funnel_data=funnel_data,
                             homes=homes,
                             roles=roles,
                             current_filters=filters)
    except Exception as e:
        print(f"Error in signup_funnel_page route: {e}")
        return render_template('signup_funnel.html',
                             funnel_data={},
                             homes=[],
                             roles=[],
                             current_filters={})

@app.route('/user-engagement')
def user_engagement_page():
    try:
        filters = parse_request_filters(request)

        engagement_data = {
            "dau_wau_mau": get_dau_wau_mau(),
            "average_session_length": get_average_session_length(),
            "retention_rates": get_retention_rates()
        }

        # Get filter options
        homes = execute_query('SELECT "id", "name" FROM public."Home" ORDER BY "name" LIMIT 50;')
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember" ORDER BY "role";')

        return render_template('user_engagement.html',
                             engagement_data=engagement_data,
                             homes=homes,
                             roles=roles,
                             current_filters=filters)
    except Exception as e:
        print(f"Error in user_engagement_page route: {e}")
        return render_template('user_engagement.html',
                             engagement_data={},
                             homes=[],
                             roles=[],
                             current_filters={})

@app.route('/acquisition')
def acquisition_page():
    try:
        filters = parse_request_filters(request)

        # Using invite success rates as a proxy for acquisition
        acquisition_data = {
            "invite_to_signup_times": get_invite_to_signup_times(), # from invite_flow
            "signup_rate_invited_family": get_invited_signup_rate_for(role='Family'), # from signup_funnel
            "signup_rate_invited_staff": get_invited_signup_rate_for(role='Staff')   # from signup_funnel
        }

        # Get filter options
        homes = execute_query('SELECT "id", "name" FROM public."Home" ORDER BY "name" LIMIT 50;')
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember" ORDER BY "role";')

        return render_template('acquisition.html',
                             acquisition_data=acquisition_data,
                             homes=homes,
                             roles=roles,
                             current_filters=filters)
    except Exception as e:
        print(f"Error in acquisition_page route: {e}")
        return render_template('acquisition.html',
                             acquisition_data={},
                             homes=[],
                             roles=[],
                             current_filters={})

@app.route('/task-analysis')
def task_analysis_page():
    try:
        filters = parse_request_filters(request)

        task_data = {
            "creators_by_role": get_task_creators_by_role(),
            "tasks_per_home_user": get_tasks_per_home_per_user(), # This returns two lists
            "daily_staff_checks": get_daily_staff_task_checks(),
            "completion_rate_staff": get_task_completion_rate_by_staff(),
            "avg_completion_delay": get_avg_task_completion_delay()
        }

        # Get filter options
        homes = execute_query('SELECT "id", "name" FROM public."Home" ORDER BY "name" LIMIT 50;')
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember" ORDER BY "role";')

        return render_template('task_analysis.html',
                             task_data=task_data,
                             homes=homes,
                             roles=roles,
                             current_filters=filters)
    except Exception as e:
        print(f"Error in task_analysis_page route: {e}")
        return render_template('task_analysis.html',
                             task_data={},
                             homes=[],
                             roles=[],
                             current_filters={})

@app.route('/feature-usage')
def feature_usage_page():
    try:
        filters = parse_request_filters(request)

        feature_data = {
            "completed_meal_planners": get_completed_meal_planners(),
            "recipe_search_count": get_recipe_search_count(),
            "add_from_search_count": get_add_from_search_count(),
            "add_own_recipe_counts": get_add_own_recipe_counts()
            # 'Need Help' feature data is not available from current src modules
        }

        # Get filter options
        homes = execute_query('SELECT "id", "name" FROM public."Home" ORDER BY "name" LIMIT 50;')
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember" ORDER BY "role";')

        return render_template('feature_usage.html',
                             feature_data=feature_data,
                             homes=homes,
                             roles=roles,
                             current_filters=filters)
    except Exception as e:
        print(f"Error in feature_usage_page route: {e}")
        return render_template('feature_usage.html',
                             feature_data={},
                             homes=[],
                             roles=[],
                             current_filters={})

# NEW MISSING PAGES - Drop-Off Analysis
@app.route('/drop-off-analysis')
def drop_off_analysis_page():
    try:
        filters = parse_request_filters(request)

        # Combine funnel data for drop-off analysis
        drop_off_data = {
            "signup_funnel": {
                "total_users": get_total_users(),
                "logged_in": get_logged_in_users(),
                "with_home": get_logged_in_users_with_and_without_home(),
                "created_home": get_creation_vs_dropoff()
            },
            "task_completion": get_task_completion_rate_by_staff(),
            "invite_conversion": {
                "family": get_invited_signup_rate_for(role='Family'),
                "staff": get_invited_signup_rate_for(role='Staff')
            }
        }

        # Get filter options
        homes = execute_query('SELECT "id", "name" FROM public."Home" ORDER BY "name" LIMIT 50;')
        roles = execute_query('SELECT DISTINCT "role" FROM public."HomeMember" ORDER BY "role";')

        return render_template('drop_off_analysis.html',
                             drop_off_data=drop_off_data,
                             homes=homes,
                             roles=roles,
                             current_filters=filters)
    except Exception as e:
        print(f"Error in drop_off_analysis_page route: {e}")
        return render_template('drop_off_analysis.html',
                             drop_off_data={},
                             homes=[],
                             roles=[],
                             current_filters={})

# API Routes with Filtering Support
@app.route('/api/metrics')
def api_metrics():
    try:
        filters = parse_request_filters(request)
        metrics = get_filtered_metrics(filters)
        return jsonify(metrics)
    except Exception as e:
        print(f"Error in api_metrics route: {e}")
        return jsonify({'total_users': 0, 'new_users': 0})

@app.route('/api/growth-trend')
def api_growth_trend():
    try:
        filters = parse_request_filters(request)
        # TODO: Implement filtering in get_dau_wau_mau function
        return jsonify(get_dau_wau_mau())
    except Exception as e:
        print(f"Error in api_growth_trend route: {e}")
        return jsonify([])

@app.route('/api/user-distribution')
def api_user_distribution():
    try:
        filters = parse_request_filters(request)
        # Get user distribution by role
        query = """
        SELECT
            hm."role" as role,
            COUNT(DISTINCT hm."userId") as count
        FROM public."HomeMember" hm
        WHERE 1=1
        """

        # Apply filters if provided
        filter_sql, filter_params = combine_filters(**filters)
        query += filter_sql
        query += ' GROUP BY hm."role" ORDER BY count DESC;'

        distribution = execute_query(query, filter_params)
        return jsonify(distribution)
    except Exception as e:
        print(f"Error in api_user_distribution route: {e}")
        return jsonify([])

@app.route('/api/signup-funnel')
def api_signup_funnel():
    try:
        filters = parse_request_filters(request)
        # TODO: Implement filtering in signup funnel functions
        funnel_data = {
            "total_users_app_downloads": get_total_users(),
            "total_logged_in": get_logged_in_users(),
            "logged_in_with_without_home": get_logged_in_users_with_and_without_home(),
            "home_creation_vs_dropoff": get_creation_vs_dropoff(),
            "invites_by_home_owners": get_invites_separated_by_role(),
            "signup_rate_invited_family": get_invited_signup_rate_for(role='Family'),
            "signup_rate_invited_staff": get_invited_signup_rate_for(role='Staff')
        }
        return jsonify(funnel_data)
    except Exception as e:
        print(f"Error in api_signup_funnel route: {e}")
        return jsonify({})

@app.route('/api/user-engagement')
def api_user_engagement():
    try:
        filters = parse_request_filters(request)
        # TODO: Implement filtering in engagement functions
        engagement_data = {
            "dau_wau_mau": get_dau_wau_mau(),
            "average_session_length": get_average_session_length(),
            "retention_rates": get_retention_rates()
        }
        return jsonify(engagement_data)
    except Exception as e:
        print(f"Error in api_user_engagement route: {e}")
        return jsonify({})

@app.route('/api/acquisition')
def api_acquisition():
    try:
        filters = parse_request_filters(request)
        # TODO: Implement filtering in acquisition functions
        acquisition_data = {
            "invite_to_signup_times": get_invite_to_signup_times(),
            "signup_rate_invited_family": get_invited_signup_rate_for(role='Family'),
            "signup_rate_invited_staff": get_invited_signup_rate_for(role='Staff')
        }
        return jsonify(acquisition_data)
    except Exception as e:
        print(f"Error in api_acquisition route: {e}")
        return jsonify({})

@app.route('/api/task-analysis')
def api_task_analysis():
    try:
        filters = parse_request_filters(request)
        # TODO: Implement filtering in task analysis functions
        task_data = {
            "creators_by_role": get_task_creators_by_role(),
            "tasks_per_home_user": get_tasks_per_home_per_user(),
            "daily_staff_checks": get_daily_staff_task_checks(),
            "completion_rate_staff": get_task_completion_rate_by_staff(),
            "avg_completion_delay": get_avg_task_completion_delay()
        }
        return jsonify(task_data)
    except Exception as e:
        print(f"Error in api_task_analysis route: {e}")
        return jsonify({})

@app.route('/api/feature-usage')
def api_feature_usage():
    try:
        filters = parse_request_filters(request)
        # TODO: Implement filtering in feature usage functions
        feature_data = {
            "completed_meal_planners": get_completed_meal_planners(),
            "recipe_search_count": get_recipe_search_count(),
            "add_from_search_count": get_add_from_search_count(),
            "add_own_recipe_counts": get_add_own_recipe_counts()
        }
        return jsonify(feature_data)
    except Exception as e:
        print(f"Error in api_feature_usage route: {e}")
        return jsonify({})

@app.route('/api/drop-off-analysis')
def api_drop_off_analysis():
    try:
        filters = parse_request_filters(request)
        # TODO: Implement filtering in drop-off analysis functions
        drop_off_data = {
            "signup_funnel": {
                "total_users": get_total_users(),
                "logged_in": get_logged_in_users(),
                "with_home": get_logged_in_users_with_and_without_home(),
                "created_home": get_creation_vs_dropoff()
            },
            "task_completion": get_task_completion_rate_by_staff(),
            "invite_conversion": {
                "family": get_invited_signup_rate_for(role='Family'),
                "staff": get_invited_signup_rate_for(role='Staff')
            }
        }
        return jsonify(drop_off_data)
    except Exception as e:
        print(f"Error in api_drop_off_analysis route: {e}")
        return jsonify({})

# API Routes for legacy support
@app.route('/api/dau-wau-mau')
def api_dau_wau_mau():
    try:
        return jsonify(get_dau_wau_mau())
    except Exception as e:
        print(f"Error in api_dau_wau_mau route: {e}")
        return jsonify([])

@app.route('/api/average-session-length')
def api_avg_session_length():
    try:
        return jsonify(get_average_session_length())
    except Exception as e:
        print(f"Error in api_avg_session_length route: {e}")
        return jsonify([])

@app.route('/api/retention-rates')
def api_retention_rates():
    try:
        return jsonify(get_retention_rates())
    except Exception as e:
        print(f"Error in api_retention_rates route: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)