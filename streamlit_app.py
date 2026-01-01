import streamlit as st
import pandas as pd
import requests

# 1. Header and Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# 2. Name Input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# 3. Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# 4. Get Fruit Options from Snowflake
# Note: Ensure your table name matches your lab (FRUIT_OPTIONS or FRUIT_LIST)
my_dataframe = session.table("smoothies.public.fruit_options").select(st.col('FRUIT_NAME'))

# 5. Multiselect for Ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# 6. API Nutrition Call and Submit Logic
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # --- FIX STARTS HERE ---
        # Change the URL to fruityvice.com
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        
        # We call .json() directly on the response object
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        # --- FIX ENDS HERE ---

    # 7. The Submit Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Build the SQL Insert Statement
        my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                values ('{ingredients_string}', '{name_on_order}')"""
        
        # Execute the insert
        if ingredients_string:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
