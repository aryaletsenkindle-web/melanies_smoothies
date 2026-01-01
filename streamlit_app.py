# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Get the current Snowflake session (required for external Streamlit deployments like Streamlit Community Cloud)
session = get_active_session()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""Choose the fruits you want in your custom Smoothie!""")

name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your smoothie will be:", name_on_order)

# Load fruit options from Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to Pandas for easier lookup
pd_df = my_dataframe.to_pandas()

# Multiselect widget
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=pd_df['FRUIT_NAME'].tolist(),  # Clean list of fruit names
    max_selections=5
)

ingredients_string = ""
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        
        # Lookup the correct SEARCH_ON value for Fruityvice API
        search_on_row = pd_df[pd_df['FRUIT_NAME'] == fruit_chosen]['SEARCH_ON']
        if not search_on_row.empty:
            search_on = search_on_row.iloc[0]
        else:
            search_on = fruit_chosen.lower()  # Fallback
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        if fruityvice_response.status_code == 200:
            fv_json = fruityvice_response.json()
            # Focus on nutritions for cleaner display
            if 'nutritions' in fv_json:
                nutrition_df = pd.DataFrame([fv_json['nutritions']])
                st.dataframe(nutrition_df, use_container_width=True)
            else:
                st.dataframe(pd.DataFrame([fv_json]), use_container_width=True)
        else:
            st.error(f"Could not retrieve data for {fruit_chosen} (used search term: {search_on}).")

    # Submit button (outside the loop)
    if name_on_order and st.button("Submit Order"):
        insert_stmt = """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (%s, %s)
        """
        try:
            session.sql(insert_stmt, params=[ingredients_string.strip(), name_on_order]).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! 🍓", icon="✅")
        except Exception as e:
            st.error(f"Failed to place order: {e}")
