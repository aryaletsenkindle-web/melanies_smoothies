import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Get Snowflake Snowpark session
session = get_active_session()

# App UI
st.title("Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie!")

# User input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Fetch fruit list from Snowflake
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_LIST").select("NAME")
fruit_rows = fruit_df.collect()

# Extract names
fruit_list = [row["NAME"] for row in fruit_rows]

# Multiselect widget
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Build ingredients string & call API
ingredients_string = ""
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower().strip()}")
        if response.status_code == 200:
            data = response.json()
            nutrition = data.get("nutritions", {})
            nutrition_df = pd.DataFrame([nutrition])
            st.dataframe(nutrition_df, use_container_width=True)
        else:
            st.error(f"Could not retrieve data for {fruit_chosen}. Status code: {response.status_code}")

# Submit order button
if ingredients_string and name_on_order and st.button("Submit Order"):
    try:
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
            params=[ingredients_string.strip(), name_on_order]
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

    except Exception as e:
        st.error(f"Failed to place order: {e}")
