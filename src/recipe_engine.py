import json
import random
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RECIPES_FILE = os.path.join(DATA_DIR, "recipes.json")
SHOPS_FILE = os.path.join(DATA_DIR, "shops.json")

class RecipeEngine:
    def __init__(self):
        with open(RECIPES_FILE, "r", encoding="utf-8") as f:
            self.recipes = json.load(f)
        with open(SHOPS_FILE, "r", encoding="utf-8") as f:
            self.shops_data = json.load(f)
        self.shops = self.shops_data["shops"]
        self.ingredient_shop_map = self.shops_data["ingredient_shop_mapping"]

    def get_daily_recipe(self, date=None):
        if date is None:
            date = datetime.now()
        day_of_year = date.timetuple().tm_yday
        recipe_index = (day_of_year - 1) % len(self.recipes)
        return self.recipes[recipe_index]

    def get_random_recipe(self, exclude_ids=None):
        if exclude_ids is None:
            exclude_ids = set()
        candidates = [r for r in self.recipes if r["id"] not in exclude_ids]
        if not candidates:
            candidates = self.recipes
        return random.choice(candidates)

    def get_recipe_by_id(self, recipe_id):
        for r in self.recipes:
            if r["id"] == recipe_id:
                return r
        return None

    def get_recipes_by_cuisine(self, cuisine):
        return [r for r in self.recipes if cuisine.lower() in r["cuisine"].lower()]

    def get_recipes_by_meal_type(self, meal_type):
        return [r for r in self.recipes if meal_type.lower() in r["meal_type"].lower()]

    def find_shops_for_ingredient(self, ingredient):
        ingredient_lower = ingredient.lower().strip()
        if ingredient_lower in self.ingredient_shop_map:
            shop_keys = self.ingredient_shop_map[ingredient_lower]
            return [self.shops[k] for k in shop_keys if k in self.shops]
        matches = []
        for shop_key, shop in self.shops.items():
            sells_lower = [s.lower() for s in shop["sells"]]
            if ingredient_lower in sells_lower:
                matches.append(shop)
        return matches

    def get_shopping_list(self, recipe):
        shopping = []
        for ingredient in recipe["ingredients"]:
            shops = self.find_shops_for_ingredient(ingredient)
            shopping.append({
                "ingredient": ingredient,
                "shops": shops[:5]
            })
        return shopping

    def find_recipes_by_ingredients(self, user_input):
        raw_ings = [i.strip().lower() for i in user_input.replace(",", " ").split() if i.strip()]
        scored = []
        for r in self.recipes:
            r_ings_lower = [i.lower() for i in r["ingredients"]]
            matches = sum(1 for ui in raw_ings if any(ui in ri for ri in r_ings_lower))
            if matches == 0:
                continue
            score = matches / max(len(r_ings_lower), 1)
            scored.append((score, matches, r))
        scored.sort(key=lambda x: (-x[0], -x[1]))
        return scored

    def get_all_cuisines(self):
        cuisines = set()
        for r in self.recipes:
            cuisines.add(r["cuisine"])
        return sorted(cuisines)

    def get_total_recipes(self):
        return len(self.recipes)

    def get_recipe_of_day_message(self, recipe, shopping_list):
        lines = []
        lines.append("=" * 60)
        lines.append(f"  {recipe['name']}")
        lines.append(f"  Cuisine: {recipe['cuisine']}")
        lines.append(f"  Meal: {recipe['meal_type']}  |  Difficulty: {recipe['difficulty']}")
        lines.append(f"  Time: {recipe['prep_time']} prep + {recipe['cook_time']} cook")
        lines.append(f"  Calories: {recipe['nutrition']['calories']} kcal")
        lines.append("=" * 60)
        lines.append("")
        lines.append("INGREDIENTS & WHERE TO BUY IN A CORUÑA:")
        lines.append("-" * 50)
        for item in shopping_list:
            ing = item["ingredient"]
            shops = item["shops"]
            lines.append(f"  {ing.capitalize()}:")
            if shops:
                for s in shops[:5]:
                    lines.append(f"    - {s['name']} ({s['address']})")
            else:
                lines.append(f"    - Check Supermercado Oriental (San Andrés) or Alahan")
            lines.append("")
        lines.append("-" * 50)
        lines.append("INSTRUCTIONS:")
        for i, step in enumerate(recipe["instructions"], 1):
            lines.append(f"  {i}. {step}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("  Buen provecho!")
        return "\n".join(lines)
