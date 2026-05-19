#!/usr/bin/env python3
"""VegRecipe AI Agent - Daily Vegetarian Recipe Suggester for A Coruña"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.recipe_engine import RecipeEngine
from datetime import datetime

def main():
    engine = RecipeEngine()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "today":
            recipe = engine.get_daily_recipe()
            shopping = engine.get_shopping_list(recipe)
            print(engine.get_recipe_of_day_message(recipe, shopping))

        elif cmd == "list":
            print(f"\nTotal recipes: {engine.get_total_recipes()}")
            print(f"\n{'ID':<4} {'Recipe':<35} {'Cuisine':<25} {'Meal Type':<20}")
            print("-" * 84)
            for r in engine.recipes:
                print(f"{r['id']:<4} {r['name']:<35} {r['cuisine']:<25} {r['meal_type']:<20}")

        elif cmd == "show":
            if len(sys.argv) > 2:
                recipe_id = int(sys.argv[2])
                recipe = engine.get_recipe_by_id(recipe_id)
                if recipe:
                    shopping = engine.get_shopping_list(recipe)
                    print(engine.get_recipe_of_day_message(recipe, shopping))
                else:
                    print(f"Recipe ID {recipe_id} not found.")
            else:
                print("Usage: python main.py show <recipe_id>")

        elif cmd == "cuisines":
            print("\nAvailable cuisines:")
            for c in engine.get_all_cuisines():
                print(f"  - {c}")

        elif cmd == "by-cuisine":
            if len(sys.argv) > 2:
                cuisine = sys.argv[2]
                recipes = engine.get_recipes_by_cuisine(cuisine)
                if recipes:
                    print(f"\nRecipes with cuisine '{cuisine}':")
                    for r in recipes:
                        print(f"  {r['id']}. {r['name']}")
                else:
                    print(f"No recipes found for cuisine '{cuisine}'.")
            else:
                print("Usage: python main.py by-cuisine <cuisine_name>")

        elif cmd == "random":
            exclude = set()
            count = 1
            if len(sys.argv) > 2:
                count = max(1, int(sys.argv[2]))
            for _ in range(count):
                recipe = engine.get_random_recipe(exclude_ids=exclude)
                exclude.add(recipe["id"])
                shopping = engine.get_shopping_list(recipe)
                print(engine.get_recipe_of_day_message(recipe, shopping))
                print("\n")
            if count > 1:
                print(f"Showing {count} random recipes (use a number to get more, e.g. 'random 5')")

        elif cmd == "date":
            if len(sys.argv) > 2:
                try:
                    date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
                    recipe = engine.get_daily_recipe(date)
                    shopping = engine.get_shopping_list(recipe)
                    print(f"\nRecipe for {sys.argv[2]}:")
                    print(engine.get_recipe_of_day_message(recipe, shopping))
                except ValueError:
                    print("Invalid date. Use YYYY-MM-DD format.")
            else:
                print("Usage: python main.py date 2026-06-15")

        elif cmd == "help" or cmd == "--help":
            print_help()
        else:
            print(f"Unknown command: {cmd}")
            print_help()
    else:
        recipe = engine.get_daily_recipe()
        shopping = engine.get_shopping_list(recipe)
        print(engine.get_recipe_of_day_message(recipe, shopping))


def print_help():
    print("""
VegRecipe AI Agent - Daily Vegetarian Recipe Suggester
=======================================================
Usage:
  python main.py                  Show today's recipe
  python main.py today            Show today's recipe
  python main.py list             List all recipes
  python main.py show <id>        Show a specific recipe
  python main.py date YYYY-MM-DD  Show recipe for a specific date
  python main.py random [n]       Show random recipe(s) (e.g. random 3)
  python main.py cuisines         List available cuisines
  python main.py by-cuisine <c>   List recipes by cuisine
""")

if __name__ == "__main__":
    main()
