# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.write(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

import streamlit as st

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
st.dataframe(my_dataframe, use_container_width=True)

ingredients_string = ""  # put this BEFORE the multiselect block

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=[row["FRUIT_NAME"] for row in my_dataframe.collect()],
    max_selections=5
)

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

my_insert_stmt = f"""
INSERT INTO smoothies.public.orders(ingredients, name_on_order)
VALUES ('{ingredients_string.strip()}', '{name_on_order}')
"""

if name_on_order and ingredients_string:
    session.sql(my_insert_stmt).collect()
    st.success("Order saved!")

