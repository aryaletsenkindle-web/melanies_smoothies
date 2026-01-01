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

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Extract SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit_chosen + " Nutrition Information")

        # API Calls (optional)
        try:
            fruityvice_response = requests.get(
                "https://fruityvice.com/api/fruit/" + fruit_chosen.lower()
            )
            if fruityvice_response.status_code == 200:
                st.dataframe(fruityvice_response.json(), use_container_width=True)
            else:
                st.error(f"No nutrition found for {fruit_chosen}")
        except:
            st.error("API connection failed.")
