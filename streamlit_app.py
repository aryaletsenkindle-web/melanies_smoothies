import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col
import re

# App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name Input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# 1. Establish Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# 2. Fetch fruit names and search values
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convert to Pandas DataFrame correctly
pd_df = my_dataframe.to_pandas()

# Display for debugging (optional)
st.dataframe(pd_df, use_container_width=True)

# 3. Multiselect using fruit names
fruit_list = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# 4. Process selection
if ingredients_list:
    ingredients_string = ''

    for fruit_chchosen in ingredients_list:
        ingredients_string += fruit_chchosen + ' '

        # Extract SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chchosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit_chchosen + " Nutrition Information")

        # API 1 (smoothiefroot)
        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )
            if smoothiefroot_response.status_code == 200:
                st.dataframe(smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"No data found for {fruit_chchosen}")
        except:
            st.error("Smoothiefroot API connection failed.")

        # API 2 (Fruityvice)
        try:
            fruityvice_response = requests.get(
                "https://fruityvice.com/api/fruit/" + fruit_chchosen.lower()
            )
            if fruityvice_response.status_code == 200:
                st.dataframe(fruityvice_response.json(), use_container_width=True)
            else:
                st.error(f"Could not find Fruityvice data for {fruit_chchosen}")
        except:
            st.error("Fruityvice API connection failed.")

    # 5. Insert Order SQL
    my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('""" + ingredients_string.strip() + """','""" + name_on_order + """')"""

    # 6. Submit Button
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        else:
            st.warning("Please enter a name before submitting!")
