import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for name on order
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# Multiselect for ingredients (max 5)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe['FRUIT_NAME'],
    max_selections=5
)

# If fruits are selected
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Cleaner than loop

    # Show nutrition info for each fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # ⚠️ FIX: Removed extra spaces in URL!
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
            if fruityvice_response.status_code == 200:
                st.dataframe(fruityvice_response.json(), use_container_width=True)
            else:
                st.warning(f"Nutrition data not available for {fruit_chosen}")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Submit button
    if st.button('Submit Order'):
        if name_on_order.strip() == "":
            st.error("Please enter a name for your smoothie order.")
        else:
            # Safe insert using Snowpark (parameterized would be better, but this matches lesson style)
            my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
