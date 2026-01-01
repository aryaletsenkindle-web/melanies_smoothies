import streamlit as st
import pandas as pd
import requests  # <-- Must be imported at the top

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

# If fruits selected, build string and fetch nutrition info
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(fruit_chosen + " Nutrition Information")

        smoothie_root = requests.get("https://smoothiefood.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothie_root.response.json(), use_container_width=True)
