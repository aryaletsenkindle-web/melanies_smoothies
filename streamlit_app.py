import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App Titles
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# User input for name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# 1. Establish Snowflake connection and session
cnx = st.connection("snowflake")
session = cnx.session()

# 2. Get fruit names and convert to Pandas to fix the "ID/Number" issue
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
pd_df = my_dataframe.to_pandas()

# 3. Multiselect widget using the Fruit Name column
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=pd_df['FRUIT_NAME'],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Header for each fruit
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # 4. API Call for Nutrition Data
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        
        if fruityvice_response.status_code == 200:
            # Displays the JSON data as a horizontal table
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.warning(f"No nutrition data found for {fruit_chosen}")

    # 5. Submit Order Logic
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Construct SQL Insert Statement
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                             values ('""" + ingredients_string.strip() + """','""" + name_on_order + """')"""

        # Execute the insert
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
