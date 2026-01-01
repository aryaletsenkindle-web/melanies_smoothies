import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# 1. Pull the data and convert it to a Pandas Dataframe
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# 2. Update the multiselect to use the column values specifically
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe['FRUIT_NAME'], # <--- This tells it to use the text column
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Fruityvice API Call (Fixed URL for Lesson 10)
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        
        # Use .json() directly
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # Submit Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                values ('{ingredients_string}', '{name_on_order}')"""
        
        if ingredients_string:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
