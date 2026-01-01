import streamlit as st
import requests  # placed before first API use to avoid crash

st.title("Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie!")

# Input from user
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection from Streamlit secrets
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names using direct SQL (avoids describe failure)
fruit_df = session.sql("SELECT NAME FROM SMOOTHIES.PUBLIC.FRUIT_LIST")

# Display the fruit list table
st.dataframe(fruit_df, use_container_width=True)

# Convert result to Python list for multiselect
fruit_rows = fruit_df.collect()
fruit_list = [row["NAME"] for row in fruit_rows]

# Multiselect widget
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# ❗ FIXED HERE: was using undefined ingredients_list
if ingredients:  # was: if ingredients_list
    ingredients_string = ""

    for fruit_chosen in ingredients:  # was: for fruit_chosen in ingredients_list
        ingredients_string += fruit_chosen + " "

    smoothie_root_response = requests.get("https://my.smoothieroot.com/api/fruit/watermelon")
    st_df = st.dataframe(data=smoothie_root_response.json(), use_container_width=True)

    # Safe SQL insert using bind parameters
    session.sql(
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
        params=[ingredients_string, name_on_order]
    ).collect()

    st.success("Your Smoothie is ordered!", icon="✅")

# Second API call display (same code kept)
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
