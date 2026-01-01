# Import required libraries
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Set up the title of the app
st.title('🥤 Customize Your Smoothie! 🥤')
st.write('Choose the fruits you want in your custom Smoothie!')

# Get the current credentials for Snowflake
session = cnx.session()

# 1. Load the fruit options from the Snowflake table
# We select both FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# 2. Convert the Snowpark Dataframe to a Pandas Dataframe 
# This is necessary so we can use the .loc function to find specific values
pd_df = my_dataframe.to_pandas()

# 3. Create the Multiselect widget for fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# 4. Processing the selection
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # 5. The "Match" Logic
        # We look up the 'SEARCH_ON' value in our Pandas DF that matches the selected 'FRUIT_NAME'
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # 6. API call using the 'search_on' value instead of the display name
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        # 7. Display the JSON response as a dataframe in the app
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
