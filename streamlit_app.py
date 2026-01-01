import streamlit as st
import requests
import pandas as pd
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
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # 🔁 MAP display name → API name
        # Updated 'Cantaloupe' to 'cantaloup' and 'Elderberries' to 'elderberry'
        api_name_map = {
            'Apples': 'apple',
            'Blueberries': 'blueberry',
            'Strawberries': 'strawberry',
            'Raspberries': 'raspberry',
            'Cantaloupe': 'cantaloup', 
            'Dragon Fruit': 'dragonfruit',
            'Kiwi': 'kiwifruit',
            'Elderberries': 'elderberry',
            'Guava': 'guava',
            'Figs': 'fig',
            'Jackfruit': 'jackfruit',
            'Lime': 'lime',
            'Mango': 'mango',
            'Nectarine': 'nectarine',
            'Orange': 'orange',
            'Papaya': 'papaya',
            'Quince': 'quince',
            'Tangerine': 'tangerine',
            'Ugli Fruit': 'ugli',
            'Watermelon': 'watermelon',
        }

        # Get API name, default to lowercase if not in map
        api_name = api_name_map.get(fruit_chosen, fruit_chosen.lower().strip())

        try:
            response = requests.get(f"https://fruityvice.com/api/fruit/{api_name}")
            if response.status_code == 200:
                # Transform the 'nutritions' dictionary into a single-row DataFrame
                # Wrapping response.json()['nutritions'] in [ ] creates a horizontal row
                fv_df = pd.DataFrame([response.json()['nutritions']])
                st.dataframe(fv_df, use_container_width=True)
            else:
                st.warning(f"⚠️ No data for '{fruit_chosen}'. Tried: {api_name}")
                
        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")

    # Submit button
    if st.button('Submit Order'):
        if not name_on_order.strip():
            st.error("Please enter your name!")
        else:
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
