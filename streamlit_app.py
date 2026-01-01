import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

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

# 2. Fetch fruit names from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()

# 3. Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

if ingredients_list:
    # Prepare the string for the database insert
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Normalize name for the API (lowercase and remove trailing spaces)
        search_term = fruit_chosen.lower().strip()
        
        # Specific overrides for tricky names
        if search_term == 'apples': search_term = 'apple'
        if search_term == 'blueberries': search_term = 'blueberry'

        try:
            # API Call
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_term}")
            
            if fruityvice_response.status_code == 200:
                # Convert the JSON response to a dataframe
                # We normalize the 'nutritions' part of the JSON for a cleaner table
                fv_df = pd.DataFrame([fruityvice_response.json()['nutritions']])
                st.dataframe(fv_df, use_container_width=True)
            else:
                st.error(f"Could not find nutrition data for {fruit_chosen}. (Tried: {search_term})")
                
        except Exception as e:
            st.error(f"Something went wrong connecting to the API: {e}")

    # 4. Submit Order Button
    if st.button('Submit Order'):
        if not name_on_order.strip():
            st.error("Please enter a name for the order!")
        else:
            # Construct the SQL Insert Statement
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            
            try:
                session.sql(my_insert_stmt).collect()
                st.success(f"✅ Your Smoothie is ordered, {name_on_order}!", icon="🚀")
            except Exception as e:
                st.error(f"Error submitting order: {e}")
