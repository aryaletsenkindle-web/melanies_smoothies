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

# 1. Establish Connection
cnx = st.connection("snowflake")
session = cnx.session()

# 2. Fetch fruit names and convert to a list
# We use .distinct() to ensure no duplicates and .tolist() for the multiselect
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe,use_container_width=True)
# st.stop()

pd_df=my_dataframe.to-pandas()
st.dataframe(pd_df)
st.stop()

# 3. Multiselect using the list of names
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,  
    max_selections=5
)

# 4. Processing the selection
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        # Build the string for the database (e.g., "Apple Banana ")
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME']==fruit_chosen,'SEARCH_ON'].iloc[0]
        st.write('The search value for',fruit_chosen,'is',search_on,'.')
        
        # Display nutrition from API for each chosen fruit
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # API Call
        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
            if fruityvice_response.status_code == 200:
                fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
            else:
                st.error(f"Could not find nutrition data for {fruit_chosen}.")
        except Exception as e:
            st.error("API connection failed.")

    # 5. Submit Button
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string.strip() + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        else:
            st.warning("Please enter a name before submitting.")
