import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.recipe_engine import RecipeEngine
from datetime import datetime

st.set_page_config(
    page_title="VegRecipe AI Agent - A Coruña",
    page_icon="🥗",
    layout="wide"
)

engine = RecipeEngine()

if "recipe" not in st.session_state:
    st.session_state.recipe = engine.get_daily_recipe()
    st.session_state.recipe_source = "today"

def show_recipe(recipe, source):
    shopping = engine.get_shopping_list(recipe)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"🍽️ {recipe['name']}")
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        meta_col1.metric("Cuisine", recipe['cuisine'])
        meta_col2.metric("Difficulty", recipe['difficulty'])
        meta_col3.metric("Calories", f"{recipe['nutrition']['calories']} kcal")

        st.markdown(f"**Prep:** {recipe['prep_time']} | **Cook:** {recipe['cook_time']} | **Meal:** {recipe['meal_type']}")
        st.markdown(f"**Protein:** {recipe['nutrition']['protein']} | **Carbs:** {recipe['nutrition']['carbs']} | **Fat:** {recipe['nutrition']['fat']}")

        st.markdown("### 📝 Instructions")
        for i, step in enumerate(recipe["instructions"], 1):
            st.markdown(f"**{i}.** {step}")

    with col2:
        st.subheader("🛒 Shopping List")
        st.markdown("*Where to buy in A Coruña city center*")

        for item in shopping:
            with st.expander(f"**{item['ingredient'].capitalize()}**", expanded=False):
                if item['shops']:
                    for shop in item['shops'][:5]:
                        st.markdown(f"🛍️ **{shop['name']}**")
                        st.caption(f"{shop['address']}")
                        st.caption(f"*{shop['description'][:80]}...*")
                else:
                    st.markdown("🛍️ **Supermercado Oriental** (Rúa de San Andrés, 146)")
                    st.caption("*Best bet for Indian/specialty ingredients*")

    if source == "today":
        st.caption(f"Recipe for {datetime.now().strftime('%A, %d %B %Y')} — this is today's fixed recipe")
    else:
        st.caption(f"Random recipe — keep clicking Surprise Me for more!")

st.title("🥗 Vegetarian Recipes - A Coruña")
st.markdown("Your vegetarian recipe companion with **where to buy ingredients** in the city center of **A Coruña, Galicia**.")

col_left, col_right = st.columns([1, 1])
with col_left:
    if st.button("📅 Today's Recipe", use_container_width=True):
        st.session_state.recipe = engine.get_daily_recipe()
        st.session_state.recipe_source = "today"
        st.rerun()
with col_right:
    if st.button("🎲 Surprise Me!", use_container_width=True, type="primary"):
        st.session_state.recipe = engine.get_random_recipe()
        st.session_state.recipe_source = "random"
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🍽️ Recipe", "🔍 Browse Recipes", "📋 All Recipes", "🏪 Shops Guide"])

with tab1:
    show_recipe(st.session_state.recipe, st.session_state.recipe_source)
    st.divider()
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        current_id = st.session_state.recipe["id"]
        prev_id = current_id - 1 if current_id > 1 else engine.get_total_recipes()
        if st.button(f"⬅ Previous", use_container_width=True):
            st.session_state.recipe = engine.get_recipe_by_id(prev_id)
            st.session_state.recipe_source = "browse"
            st.rerun()
    with c2:
        if st.button("🎲 Surprise Me", use_container_width=True):
            st.session_state.recipe = engine.get_random_recipe(exclude_ids={st.session_state.recipe["id"]})
            st.session_state.recipe_source = "random"
            st.rerun()
    with c3:
        next_id = current_id + 1 if current_id < engine.get_total_recipes() else 1
        if st.button(f"Next ➡", use_container_width=True):
            st.session_state.recipe = engine.get_recipe_by_id(next_id)
            st.session_state.recipe_source = "browse"
            st.rerun()

with tab2:
    st.subheader("🔍 Find Recipes")

    col1, col2 = st.columns(2)
    with col1:
        cuisine_filter = st.selectbox("Filter by cuisine", ["All"] + engine.get_all_cuisines())
    with col2:
        meal_filter = st.selectbox("Filter by meal type", ["All", "breakfast", "lunch_dinner", "starter_snack", "breakfast_lunch"])

    filtered = engine.recipes
    if cuisine_filter != "All":
        filtered = [r for r in filtered if r["cuisine"] == cuisine_filter]
    if meal_filter != "All":
        filtered = [r for r in filtered if meal_filter in r["meal_type"]]

    for recipe in filtered:
        label = f"**#{recipe['id']}** {recipe['name']} — {recipe['cuisine']} | {recipe['meal_type']} | ⏱ {recipe['prep_time']}+{recipe['cook_time']} | {recipe['nutrition']['calories']} kcal"
        with st.expander(label, expanded=False):
            for i, step in enumerate(recipe["instructions"], 1):
                st.markdown(f"**{i}.** {step}")

with tab3:
    st.subheader("📋 All Recipes")
    search = st.text_input("Search recipes by name or ingredient", "")

    for recipe in engine.recipes:
        if search and search.lower() not in recipe['name'].lower() and search.lower() not in " ".join(recipe['ingredients']).lower():
            continue
        with st.expander(f"#{recipe['id']} - {recipe['name']} ({recipe['cuisine']})"):
            st.markdown(f"**Difficulty:** {recipe['difficulty']} | **Time:** {recipe['prep_time']} + {recipe['cook_time']}")
            st.markdown(f"**Calories:** {recipe['nutrition']['calories']} kcal")
            st.markdown("**Ingredients:** " + ", ".join(recipe['ingredients']))
            if st.button(f"🛒 Show where to buy ingredients", key=f"shop_btn_{recipe['id']}"):
                shopping = engine.get_shopping_list(recipe)
                for item in shopping:
                    st.markdown(f"**{item['ingredient'].capitalize()}:**")
                    if item['shops']:
                        for shop in item['shops'][:3]:
                            st.markdown(f"- 🛍️ {shop['name']} ({shop['address']})")
                    st.markdown("---")

with tab4:
    st.subheader("🏪 Shops & Supermarkets in A Coruña City Center")
    st.markdown("Here are all the shops we recommend for getting your ingredients:")

    cols = st.columns(2)
    for i, (shop_key, shop) in enumerate(engine.shops.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{shop['name']}**")
                st.caption(f"📍 {shop['address']} | *{shop['zone'].replace('_', ' ').title()}*")
                st.markdown(f"{shop['description']}")
                with st.expander("What they sell"):
                    for s in sorted(set(shop['sells'])):
                        st.markdown(f"- {s}")

st.sidebar.markdown("## 🥗 VegRecipe AI Agent")
st.sidebar.markdown("Your daily vegetarian recipe companion for **A Coruña, Galicia**.")
st.sidebar.markdown("---")
st.sidebar.markdown("### Stats")
st.sidebar.markdown(f"- **Total recipes:** {engine.get_total_recipes()}")
st.sidebar.markdown(f"- **Cuisines:** {len(engine.get_all_cuisines())}")
st.sidebar.markdown(f"- **Shops mapped:** {len(engine.shops)}")
st.sidebar.markdown("---")

st.sidebar.markdown("Made with ❤️ for vegetarians in A Coruña")
