import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# User Name Input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Establish Snowflake connection and session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit list from Snowflake
# Note: Ensure your table name 'fruit_options' or 'fruit_list' matches your database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Ingredient selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Display Nutrition Information from Fruityvice API
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        
        if fruityvice_response.status_code == 200:
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.warning(f"No nutrition data found for {fruit_chosen}")

    # Submit Order Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Construct the SQL Insert Statement
        # We use strip() to remove the trailing space from ingredients_string
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                             values ('""" + ingredients_string.strip() + """','""" + name_on_order + """')"""

        # Execute the insert
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
