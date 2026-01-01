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
# Multiselect widget - assigned to 'ingredients'
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)
# Check if ingredients is not empty

if ingredients:
    # Join list into a single string separated by spaces
    ingredients_string = " ".join(ingredients)
    # Display selection for user
    st.write("Selected Ingredients:", ingredients_string)
    # API Call - Note: Using 'smoothiefroot' (checked common tutorial naming)
    # Using the last item selected to show specific fruit info
    last_fruit = ingredients[-1]
    st.subheader(f'Nutritional Information for {last_fruit}')
    try:
        # Example API endpoint (Ensure this URL is correct for your specific lesson)
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{last_fruit}")
        if response.status_code == 200:
            st.dataframe(data=response.json(), use_container_width=True)
        else:
            st.warning("Could not retrieve nutritional data at this time.")
    except Exception as e:
        st.error(f"API Error: {e}")
    # SQL Insert

    submit_submit = st.button('Submit Order')
    if submit_submit:

        insert_query = """

            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)

            VALUES (?, ?)

        """
        session.sql(insert_query, params=[ingredients_string, name_on_order]).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
