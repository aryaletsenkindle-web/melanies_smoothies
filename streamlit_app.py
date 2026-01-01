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
fruit_list = [row["NAME"] for row in fruit_rows]

# Multiselect widget
selected_ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Check if any ingredients are selected
if selected_ingredients:
    ingredients_string = " ".join(selected_ingredients)
    st.write("Selected Ingredients:", ingredients_string)

    # Show nutritional info for the last selected fruit
    last_fruit = selected_ingredients[-1]
    st.subheader(f'Nutritional Information for {last_fruit}')
    
    try:
        # Fix: remove extra spaces in URL
        response = requests.get(f"https://www.fruityvice.com/api/fruit/{last_fruit.lower()}")
        if response.status_code == 200:
            fruit_data = response.json()
            st.dataframe(data=fruit_data, use_container_width=True)
        else:
            st.warning(f"Could not retrieve data for '{last_fruit}'. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"API Error: {e}")

    # Submit button
    if st.button('Submit Order'):
        insert_query = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES (?, ?)
        """
        session.sql(insert_query, params=[ingredients_string, name_on_order]).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
