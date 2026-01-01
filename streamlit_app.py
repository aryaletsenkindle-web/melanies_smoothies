import streamlit as st
from datetime import datetime

st.title("Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie!")

# Input from user
name_on_order = st.text_input("Name on Smoothie:").strip()
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names
fruit_df = session.sql("SELECT NAME FROM SMOOTHIES.PUBLIC.FRUIT_LIST")
st.dataframe(fruit_df, use_container_width=True)

fruit_rows = fruit_df.collect()
fruit_list = [row["NAME"] for row in fruit_rows]

# Multiselect widget
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Insert into ORDERS table
if ingredients and st.button("Submit Order"):
    # 🔑 SORT ingredients to ensure stable HASH
    ingredients_string = " ".join(sorted(ingredients))

    session.sql(
        """
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (INGREDIENTS, NAME_ON_ORDER, ORDER_TS, ORDER_FILLED)
        VALUES (?, ?, ?, ?)
        """,
        params=[
            ingredients_string,
            name_on_order,
            datetime.now(),
            False
        ]
    ).collect()

    st.success("Your Smoothie is ordered!", icon="✅")
