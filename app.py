import streamlit as st
import sqlite3
import pandas as pd
import re

# DB connect
conn = sqlite3.connect("sales.db")

st.title("💬 Smart Data Chatbot")

# 🔥 DROPDOWN SUGGESTIONS
suggestions = [
    "",
    "total sales",
    "top 5 states by sales",
    "bottom 3 cities by sales",
    "sales in Florida",
    "sales in California in 2017",
    "sales of binder in Florida",
    "sales by category",
    "count of customers",
]

selected_query = st.selectbox("💡 Choose a sample query:", suggestions)

# INPUT (auto-filled if dropdown used)
user_input = st.text_input(
    "Enter your question:",
    value=selected_query
)

# Load values
def get_unique_values(column):
    query = f"SELECT DISTINCT {column} FROM sales_data"
    return pd.read_sql(query, conn)[column].str.lower().tolist()

states = get_unique_values("state")
cities = get_unique_values("city")

# Normalize
def normalize_input(text):
    text = text.lower()
    text = text.replace("states", "state")
    text = text.replace("cities", "city")
    text = text.replace("revenue", "sales")
    return text


def generate_sql(user_input):
    user_input = normalize_input(user_input)

    if "sales" not in user_input and "customer" not in user_input:
        return None

    # METRIC
    if "customer" in user_input:
        agg = "COUNT(DISTINCT customer_id)"
    else:
        agg = "SUM(sales)"

    # GROUP BY
    group_by = None
    if "state" in user_input:
        group_by = "state"
    elif "city" in user_input:
        group_by = "city"
    elif "category" in user_input:
        group_by = "category"

    select_part = f"{group_by}, {agg}" if group_by else agg

    # TOP/BOTTOM
    order_by = ""
    limit = ""

    match = re.search(r"(top|bottom)\s*(\d+)", user_input)
    if match:
        t = match.group(1)
        n = match.group(2)
        limit = f" LIMIT {n}"
        order_by = f" ORDER BY {agg} {'DESC' if t == 'top' else 'ASC'}"

    # CONDITIONS
    conditions = []

    # MULTIPLE STATES
    matched_states = [s for s in states if s in user_input]
    if matched_states:
        vals = "', '".join([s.title() for s in matched_states])
        conditions.append(f"state IN ('{vals}')")

    # MULTIPLE CITIES
    matched_cities = [c for c in cities if c in user_input]
    if matched_cities:
        vals = "', '".join([c.title() for c in matched_cities])
        conditions.append(f"city IN ('{vals}')")

    # 🔥 PRODUCT SEARCH
    words = user_input.split()
    product_conditions = []

    for word in words:
        if len(word) > 3 and word not in ["sales","state","city","category"]:
            product_conditions.append(f"product_name LIKE '%{word}%'")

    if product_conditions:
        conditions.append("(" + " OR ".join(product_conditions) + ")")

    # BUILD QUERY
    query = f"SELECT {select_part} FROM sales_data"

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if group_by:
        query += f" GROUP BY {group_by}"

    query += order_by + limit

    return query


# RUN
if st.button("Run Query"):
    if user_input:
        query = generate_sql(user_input)

        if query is None:
            st.error("❌ Cannot understand query")
        else:
            st.code(query)

            try:
                result = pd.read_sql(query, conn)

                if result.empty:
                    st.warning("⚠️ No data found")
                else:
                    st.write(result)

                    if len(result.columns) == 2:
                        st.bar_chart(result.set_index(result.columns[0]))

            except Exception as e:
                st.error(e)