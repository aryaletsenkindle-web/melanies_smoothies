import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name Input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Get the current session (for Streamlit in Snowflake)
session = get_active_session()

# Fetch fruit options from Snowflake table
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('FRUIT_NAME'))

# Convert to pandas for easier handling
pd_df = my_dataframe.to_pandas()

# Get the list of fruit names for multiselect
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Process selections
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Display nutrition info from Fruityvice API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen.lower())
            if fruityvice_response.status_code == 200:
                fv_df = pd.DataFrame(fruityvice_response.json(), index=[0])
                st.dataframe(fv_df, use_container_width=True)
            else:
                st.warning(f"Nutrition data not available for {fruit_chosen}.")
        except Exception:
            st.error("Failed to fetch nutrition data.")

    # Prepare insert statement
    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Submit button
    submit_button = st.button('Submit Order')

    if submit_button:
        if name_on_order and ingredients_list:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
        elif not name_on_order:
            st.warning("Please enter your name before submitting.")
        else:
            st.warning("Please select at least one ingredient.")
