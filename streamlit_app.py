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

# 1. Establish Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# 2. Fetch fruit names and search values
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)
# Convert to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Optional: Display the fruit options for debugging
# st.dataframe(pd_df, use_container_width=True)

# 3. Multiselect using fruit names
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# 4. Process selection
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list) + ' '

    # Display the order summary
    if name_on_order:
        st.write(f"{name_on_order}'s smoothie will contain: {ingredients_string}")

    # Loop through each selected fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Get the SEARCH_ON value for better API matching
        search_on_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        if not search_on_row.empty:
            search_term = search_on_row.iloc[0]
            if pd.isna(search_term):
                search_term = fruit_chosen
        else:
            search_term = fruit_chosen

        # Normalize search term (lowercase, remove extra spaces)
        search_term = re.sub(r'\s+', '-', search_term.strip().lower())

        # Call Fruityvice API
        try:
            fruityvice_response = requests.get(f"https://www.fruityvice.com/api/fruit/{search_term}")
            if fruityvice_response.status_code == 200:
                # The response is a single dict, not a list
                fv_data = fruityvice_response.json()
                # Convert to DataFrame for nice display (flatten nutritions)
                nutrition_df = pd.DataFrame({
                    "Nutrient": ["Calories", "Fat (g)", "Sugar (g)", "Carbohydrates (g)", "Protein (g)"],
                    "Amount (per 100g)": [
                        fv_data["nutritions"]["calories"],
                        fv_data["nutritions"]["fat"],
                        fv_data["nutritions"]["sugar"],
                        fv_data["nutritions"]["carbohydrates"],
                        fv_data["nutritions"]["protein"]
                    ]
                })
                st.dataframe(nutrition_df, use_container_width=True)
            else:
                st.warning(f"No nutrition data found for '{fruit_chosen}' (tried '{search_term}')")
        except Exception as e:
            st.error("Failed to connect to the nutrition API. Please try again later.")
