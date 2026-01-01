import streamlit as st
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Fetch data from Snowflake
df = session.table("smoothies.public.fruit_list").select(col("NAME"))

# Convert Snowpark DF → Python list
fruit_rows = df.collect()
fruit_list = [row["NAME"] for row in fruit_rows]  # extract NAME column

# Display table
st.dataframe(data=df, use_container_width=True)

# Now multiselect gets a real list
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Build ingredients string
ingredients_string = " ".join(ingredients_list)

if ingredients_list:
    insert_sql = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(insert_sql).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
