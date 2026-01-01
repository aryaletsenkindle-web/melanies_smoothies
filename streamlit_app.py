import streamlit as st
import pandas as pd
st.title("Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie!")
# Input from user
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)
# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()
# Get fruit names from Snowflake
fruit_df = session.sql("SELECT NAME FROM SMOOTHIES.PUBLIC.FRUIT_LIST")
fruit_rows = fruit_df.collect()
# Extract fruit names safely
fruit_list = [row["NAME"] for row in fruit_rows]
# Multiselect widget
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)
# If fruits selected, fetch nutrition
ingredients_string = ""
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    smoothiefoot_response = requests.get("https://my.smoothiefoot.com/api/fruit/watermelon")
    sf_df = st.dataframe(data=smoothiefoot_response.json(), use_container_width=True)


import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st_df=st.dataframe(data=smoothiefroot_response.json(), use _container_width=True)
