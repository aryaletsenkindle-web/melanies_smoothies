import streamlit as st

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

# Insert into ORDERS table when button is clicked
if ingredients and st.button("Submit Order"):
    ingredients_string = " ".join(ingredients)

    # Safe SQL insert using bind parameters
    session.sql(
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
        params=[ingredients_string, name_on_order]
    ).collect()

    st.success("Your Smoothie is ordered!", icon="✅")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response


