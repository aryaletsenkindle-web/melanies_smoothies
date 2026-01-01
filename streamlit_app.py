# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""Choose the fruits you want in your custom Smoothie!""")

name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on smoothie will be:", name_on_order)

# Snowflake connection (this works in external Streamlit deployments connected to Snowflake)
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to Pandas for easier lookup (used for Fruityvice API search term)
pd_df = my_dataframe.to_pandas()

# Multiselect widget for choosing fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=my_dataframe.select('FRUIT_NAME'),  # Display only fruit names
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Find the correct search term for Fruityvice API (handles names like "Banana" vs "banana")
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        if fruityvice_response.status_code == 200:
            fv_df = pd.DataFrame(fruityvice_response.json(), index=[0])
            st.dataframe(fv_df, use_container_width=True)
        else:
            st.error(f"Could not retrieve data for {fruit_chosen}.")

    # Submit order button
    if name_on_order and st.button('Submit Order'):
        my_insert_stmt = f""" 
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
