import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Pull fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe['FRUIT_NAME'],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # API Mapping to handle plural/singular mismatches
        api_name_map = {
            'Apples': 'apple',
            'Blueberries': 'blueberry',
            'Cantaloupe': 'cantaloup',
            'Elderberries': 'elderberry'
        }
        search_term = api_name_map.get(fruit_chosen, fruit_chosen.lower())

        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_term)
            if fruityvice_response.status_code == 200:
                # Extract 'nutritions' and wrap in [] to make it a single horizontal row
                fv_df = pd.DataFrame([fruityvice_response.json()['nutritions']])
                st.dataframe(fv_df, use_container_width=True)
            else:
                st.warning(f"No nutrition data found for {fruit_chosen}")
        except:
            st.error("Could not connect to the API.")

    # Submit Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if not name_on_order:
            st.error("Please provide a name!")
        else:
            # Note: Ensure your table has the order_filled column for the final lab
            my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('{ingredients_string.strip()}', '{name_on_order}')"""
            
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
