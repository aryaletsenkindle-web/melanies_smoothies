# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# 1. App Header
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# 2. User Input
name_on_order = st.text_input('Name on Smoothie:')
if name_on_order:
    st.write('The name on your Smoothie will be:', name_on_order)

# 3. Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# 4. Data Retrieval (Fixed the '0' to 'O' typo here)
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), 
    col("SEARCH_ON")
)

# Convert to Pandas for easier lookup later
pd_df = my_dataframe.to_pandas()

# 5. Ingredient Selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# 6. Process Selection
if ingredients_list:
    ingredients_string = ""
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        
        # Pull the search value from our Pandas DF
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        
        # 7. Nutrition API Call
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # Note: Ensure search_on is not null/empty
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            if fruityvice_response.status_code == 200:
                st.dataframe(fruityvice_response.json(), use_container_width=True)
            else:
                st.warning(f"Could not find nutrition data for {fruit_chosen}.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

    # 8. Submit Order to Snowflake
    if st.button('Submit Order'):
        # Strip trailing space and prepare SQL
        clean_ingredients = ingredients_string.strip()
        
        # Use a more secure formatting or confirm column names match your table
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{clean_ingredients}', '{name_on_order}')
        """
        
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f"Alright {name_on_order}, your order is saved!", icon="✅")
        else:
            st.error("Please add a name to the order before submitting.")
