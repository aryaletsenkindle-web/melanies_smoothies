import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name Input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# 1. Establish Connection
cnx = st.connection("snowflake")
session = cnx.session()

# 2. Fetch fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()

# 3. Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # cleaner and safer

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # 🔧 FIXED: Remove extra spaces + normalize fruit name for API
        fruit_api_name = fruit_chosen.lower().rstrip('s')  # "Apples" → "apple"

        # Handle special cases (optional but improves results)
        special_cases = {
            'cantaloupe': 'cantaloup',
            'dragon fruit': 'dragonfruit',
            'blueberries': 'blueberry',
            'strawberries': 'strawberry',
            'raspberries': 'raspberry',
            'kiwi': 'kiwifruit',
        }
        fruit_api_name = special_cases.get(fruit_chosen.lower(), fruit_api_name)

        try:
            # ✅ CORRECT URL: NO EXTRA SPACES!
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_api_name}")

            if fruityvice_response.status_code == 200:
                st.dataframe(fruityvice_response.json(), use_container_width=True)
            else:
                # Friendly message for exotic fruits not in API
                if fruit_chosen.lower() in ['vanilla fruit', 'ximenia', 'yerba mate', 'ziziphus jujube']:
                    st.info(f"🌱 '{fruit_chosen}' is an exotic ingredient — no nutrition data available.")
                else:
                    st.warning(f"⚠️ No data for '{fruit_chosen}'. Tried API name: '{fruit_api_name}'")
        except Exception as e:
            st.error(f"❌ Error fetching nutrition info: {e}")

    # 4. Submit Button
    if st.button('Submit Order'):
        if not name_on_order.strip():
            st.error("Please enter a name for your smoothie!")
        else:
            # Safe insert (for lesson purposes)
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
