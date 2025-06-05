# Meals_Feature_Usage.py

from src.database import DatabaseConnection, execute_query

def get_completed_meal_planners():
    """
    Count distinct users who have any row in MealInstance,
    using the 'createdByUserId' column to identify the user.
    """
    query = """
    SELECT
      COUNT(DISTINCT mi."createdByUserId") AS users_completed_setup
    FROM public."MealInstance" mi;
    """
    return execute_query(query)

def get_incomplete_meal_planners():
    """
    Cannot compute incomplete meal planning without a completion flag.
    """
    return None

def get_meal_planning_abandon_steps():
    """
    No 'currentStep' column is present in MealInstance, so abandon-step data is unavailable.
    """
    return None

def get_recipe_search_count():
    """
    Count total recipe search events from RecipeSearchReport.
    """
    query = """
    SELECT
      COUNT(*) AS total_search_events
    FROM public."RecipeSearchReport" rsr;
    """
    return execute_query(query)

def get_add_from_search_count():
    """
    Treat every MealRecipeInstanceToMealMembers entry as an 'add from search' proxy.
    """
    query = """
    SELECT
      COUNT(DISTINCT mrm."mealMemberId")   AS users_added_from_search,
      COUNT(*)                             AS total_adds_from_search
    FROM public."MealRecipeInstanceToMealMembers" mrm;
    """
    return execute_query(query)

def get_add_own_recipe_counts():
    """
    Count users and total additions of recipes broken down by 'source' in Recipe.
    Groups by each distinct source value.
    """
    query = """
    SELECT
      r."source"                  AS method,
      COUNT(DISTINCT r."addedByUserId") AS users_count,
      COUNT(*)                    AS total_count
    FROM public."Recipe" r
    GROUP BY r."source"
    ORDER BY r."source";
    """
    return execute_query(query)

if __name__ == "__main__":
    print("\n▶ Initializing connection pool...")
    DatabaseConnection.initialize_pool()

    # 16) Completed meal planning setup
    print("\n[16] Users who have any MealInstance entry (completed setup):")
    try:
        completed = get_completed_meal_planners()
        print(completed)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 17) Started but did not complete meal planning setup
    print("\n[17] Users who started but did not complete meal planning setup:")
    incomplete = get_incomplete_meal_planners()
    if incomplete is None:
        print("   • Cannot compute—no completion flag in MealInstance.")
    else:
        print(incomplete)

    # 17.1) Abandonment by step
    print("\n[17.1] Steps where users are abandoning meal planning:")
    abandon_steps = get_meal_planning_abandon_steps()
    if abandon_steps is None:
        print("   • Cannot compute—no 'currentStep' column in MealInstance.")
    else:
        print(abandon_steps)

    # 18.a) Recipe search usage
    print("\n[18.a] Total recipe search events:")
    try:
        search_counts = get_recipe_search_count()
        print(search_counts)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 18.a.i) Add a meal from search
    print("\n[18.a.i] Users adding meals from recipe search:")
    try:
        add_search = get_add_from_search_count()
        print(add_search)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    # 18.c) Add own recipes by method
    print("\n[18.c] Users adding their own recipes (broken down by source):")
    try:
        own_recipes = get_add_own_recipe_counts()
        print(own_recipes)
    except Exception as e:
        print(f"   ✖ Error: {e}")

    DatabaseConnection.close_all_connections()
