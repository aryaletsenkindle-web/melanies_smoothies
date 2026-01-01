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
        # Call API safely
        response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower().strip()}")
        if response.status_code == 200:
            data = response.json()
            nutrition = data.get("nutritions", {}) # Extract only nutrition part
            nutrition_df = pd.DataFrame([nutrition]) # Convert to single row table
            st.dataframe(nutrition_df, use_container_width=True)
        else:
            st.error(f"Could not retrieve data for {fruit_chosen}. Status code: {response.status_code}")
# Submit button outside loop
if ingredients_string and name_on_order and st.button("Submit Order"):
    insert_query = """
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES (?, ?)
    """
    try:
        session.sql(insert_query, params=[ingredients_string.strip(), name_on_order]).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
    except Exception as e:
        st.error(f"Failed to place order: {e}")
