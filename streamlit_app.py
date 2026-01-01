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
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    st.subheader("Nutrition Information for Selected Fruits")
    
    # Note: The API currently only supports one fruit at a time and is hardcoded.
    # For now, we'll just fetch info for the first selected fruit as an example.
    if ingredients_list:
        first_fruit = ingredients_list[0].lower().replace(" ", "-")  # e.g., "Strawberry Kiwi" → not supported yet
        # The real API likely expects fruit names like "watermelon", "banana", etc.
        # Adjust this when you know the correct endpoint format.
        api_url = f"https://my.smoothiefoot.com/api/fruit/{first_fruit}"
        
        try:
            smoothiefroot_response = requests.get(api_url)
            smoothiefroot_response.raise_for_status()  # Raises error for bad status
            nutrition_data = smoothiefroot_response.json()
            
            # Display as dataframe
            st_df = st.dataframe(
                data=nutrition_data,
                use_container_width=True
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Could not fetch data for {ingredients_list[0]}: {e}")
        except ValueError:
            st.error("Invalid JSON response from API.")
