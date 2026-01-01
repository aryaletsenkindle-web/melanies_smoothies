import streamlit as st
import pandas as pd
import requests

# Set up the title and description
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# 1. Name Input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# 2. Snowflake Connection & Data Retrieval
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names for the multiselect
my_dataframe = session.table("smoothies.public.fruit_options").select(st.col('FRUIT_NAME'))

# 3. Ingredients Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# 4. Processing Selections & API Calls
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Call the Fruityvice API (Correct URL for the Lab)
        # We use the fruit name at the end of the URL
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        
        # Display the nutrition data as a dataframe
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # 5. The "Submit Order" Button & SQL Insert
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Build the INSERT statement
        my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                values ('{ingredients_string}', '{name_on_order}')"""
        
        # Execute the insert
        if ingredients_string:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
