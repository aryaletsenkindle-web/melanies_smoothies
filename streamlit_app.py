import streamlit as st
import requests
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

# Get fruit names
fruit_df = session.sql("SELECT NAME FROM SMOOTHIES.PUBLIC.FRUIT_LIST")
fruit_rows = fruit_df.collect()
fruit_list = [row["0"] if "NAME" not in row else row["NAME"] for row in fruit_rows]
# ^ Safeguard in case column name isn't exactly "NAME" (Snowflake sometimes returns "0")

# Multiselect widget
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Check if any ingredients are selected
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        # ⚠️ Fix: Remove extra spaces in URL!
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}")

        if fruityvice_response.status_code == 200:
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Could not find data for {fruit_chosen}")

    # ✅ Only ONE submit button — outside the loop AND not duplicated
    if st.button('Submit Order'):
        insert_query = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES (?, ?)
        """
        session.sql(insert_query, params=[ingredients_string.strip(), name_on_order]).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
