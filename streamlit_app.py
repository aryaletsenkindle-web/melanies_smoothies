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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_0N'))
# st.dataframe(my_dataframe, use_container_width=True)
# st.stop()


pd_df = my_dataframe.to_pandas()

st.dataframe(pd_df)
st.stop()
ingredients_string = ""  # put this BEFORE the multiselect block

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=[row["FRUIT_NAME"] for row in my_dataframe.collect()],
    max_selections=5
)

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chchosen + " Nutrition Information")
        smoothie_fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        sf_df = st.dataframe(smoothie_fruityvice_response.json(), width="stretch")

my_insert_stmt = f"""
INSERT INTO smoothies.public.orders(ingredients, name_on_order)
VALUES ('{ingredients_string.strip()}', '{name_on_order}')
"""

if name_on_order and ingredients_string:
    session.sql(my_insert_stmt).collect()
    st.success("Order saved!")


import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# st.text(smoothiefroot_response.json())
sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

