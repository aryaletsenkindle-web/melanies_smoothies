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
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Prepare API-safe name
        fruit_api_name = fruit_chosen.lower().replace(" ", "")

        try:
            response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_api_name}")
            if response.status_code == 200:
                data = response.json()
                nutrition = data.get("nutritions", {})
                nutrition_df = pd.DataFrame([nutrition])
                st.dataframe(nutrition_df, use_container_width=True)
            else:
                st.error(f"Could not retrieve data for {fruit_chosen}. Status code: {response.status_code}")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

