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

# 2. FIX: Fetch fruit names and convert to a list to avoid seeing numbers/IDs
my_dataframe = session.table("smoothies.public.fruit_options").select('FRUIT_NAME')
# Convert Snowpark dataframe column to a simple Python list
fruit_list = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()

# 3. Multiselect using the list of names
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,  # This ensures names show up, not numbers
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Display nutrition from API for each chosen fruit
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Correct URL from your course image
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        
        if fruityvice_response.status_code == 200:
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.warning(f"No nutrition data found for {fruit_chosen}")

    # 4. Submit Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                             values ('""" + ingredients_string.strip() + """','""" + name_on_order + """')"""

        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
