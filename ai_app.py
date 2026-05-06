import streamlit as st
import sqlite3
import pandas as pd
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Smart Data Chatbot", page_icon="🤖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d0d0d; color: #e8e8e8; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 760px; }
.hero { text-align: center; padding: 2.5rem 0 2rem 0; border-bottom: 1px solid #222; margin-bottom: 2rem; }
.hero h1 { font-family: 'Space Mono', monospace; font-size: 1.9rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em; margin-bottom: 0.3rem; }
.hero p { color: #666; font-size: 0.9rem; font-weight: 300; letter-spacing: 0.04em; }
.hero .dot { color: #00ff9d; }
label, .stTextInput label, .stSelectbox label { font-family: 'Space Mono', monospace !important; font-size: 0.72rem !important; letter-spacing: 0.1em !important; color: #555 !important; text-transform: uppercase !important; }
.stTextInput input { background: #141414 !important; border: 1px solid #2a2a2a !important; border-radius: 8px !important; color: #e8e8e8 !important; font-size: 0.95rem !important; padding: 0.65rem 1rem !important; }
.stTextInput input:focus { border-color: #00ff9d !important; box-shadow: 0 0 0 3px rgba(0,255,157,0.08) !important; }
.stSelectbox > div > div { background: #141414 !important; border: 1px solid #2a2a2a !important; border-radius: 8px !important; color: #e8e8e8 !important; }
.stButton > button { background: #00ff9d !important; color: #0d0d0d !important; border: none !important; border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important; font-weight: 700 !important; padding: 0.65rem 2rem !important; width: 100% !important; }
.stButton > button:hover { opacity: 0.88 !important; }
.badge { display: inline-block; padding: 0.2rem 0.75rem; border-radius: 999px; font-family: 'Space Mono', monospace; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 1rem; }
.badge-rule { background: #1a2a1f; color: #00ff9d; border: 1px solid #00ff9d33; }
.badge-ai { background: #1a1a2a; color: #7b8cff; border: 1px solid #7b8cff33; }
.result-meta { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #444; letter-spacing: 0.06em; margin-bottom: 0.75rem; }
.stAlert { border-radius: 8px !important; font-size: 0.88rem !important; }
hr { border-color: #1a1a1a !important; }
.footer { text-align: center; font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #333; letter-spacing: 0.08em; padding-top: 2.5rem; border-top: 1px solid #1a1a1a; margin-top: 3rem; }
</style>
""", unsafe_allow_html=True)

# ── GROQ CLIENT ──
@st.cache_resource
def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Add it to your .env file.")
        st.stop()
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

# ── DB ──
@st.cache_resource
def get_connection():
    return sqlite3.connect("sales.db", check_same_thread=False)

client = get_client()
conn   = get_connection()

# ── HERO ──
st.markdown("""
<div class="hero">
    <h1>Smart Data Chatbot<span class="dot">.</span></h1>
    <p>NATURAL LANGUAGE → SQL → INSIGHTS</p>
</div>
""", unsafe_allow_html=True)

# ── SUGGESTIONS ──
suggestions = [
    "",
    "total sales",
    "sales by region",
    "sales by category",
    "sales by sub-category",
    "top 5 states by sales",
    "top 10 states by sales",
    "bottom 5 states by sales",
    "top 10 products by profit",
    "top 5 customers by sales",
    "sales in Florida",
    "sales in California",
    "sales in California in 2017",
    "sales in Texas and New York",
    "sales of binder in Florida",
    "sales by city in California",
    "sales greater than 500",
    "profit greater than 100",
    "number of orders by month and year",
    "number of orders by month in 2017",
    "total sales in 2017",
    "sales by year",
    "count of customers",
]

selected   = st.selectbox("💡 Sample queries", suggestions)
user_input = st.text_input("Ask anything about the data", value=selected, placeholder="e.g. top 10 states by sales")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    run = st.button("⚡ Run Query", use_container_width=True)

# ── CLEAN SQL ──
def clean_sql(raw: str) -> str:
    raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE).strip()
    raw = raw.strip("`").strip()
    raw = raw.split(";")[0].strip() + ";"
    return raw

# ── AI SQL ──
def ai_sql(query: str):
    system_prompt = (
        "You are a precise SQL expert working with a retail sales database.\n\n"
        "Table: sales_data\n"
        "Columns: row_id, order_id, order_date, ship_date, ship_mode, customer_id, customer_name,\n"
        "         segment, country, city, state, postal_code, region, product_id, category,\n"
        "         sub_category, product_name, sales, quantity, discount, profit\n\n"
        "CRITICAL: order_date is stored as DD-MM-YYYY string (e.g. 15-04-2017)\n"
        "Use substr() to extract dates — NEVER use strftime():\n"
        "  - Day:   substr(order_date, 1, 2)\n"
        "  - Month: substr(order_date, 4, 2)\n"
        "  - Year:  substr(order_date, 7, 4)\n\n"
        "Date examples:\n"
        "  - Filter year 2017: WHERE substr(order_date, 7, 4) = '2017'\n"
        "  - Group by year: GROUP BY substr(order_date, 7, 4)\n"
        "  - Group by month+year: SELECT substr(order_date, 7, 4) AS year, substr(order_date, 4, 2) AS month, COUNT(DISTINCT order_id) AS order_count FROM sales_data GROUP BY substr(order_date, 7, 4), substr(order_date, 4, 2) ORDER BY year ASC, month ASC\n"
        "  - NEVER add year WHERE filter unless user says a specific year\n\n"
        "Rules:\n"
        "- Return ONLY raw SQL, no markdown, no explanation, no backticks\n"
        "- Use ROUND(value, 2) for sales, profit, discount\n"
        "- Count orders: COUNT(DISTINCT order_id) AS order_count\n"
        "- Count customers: COUNT(DISTINCT customer_id) AS customer_count\n"
        "- Products: product_name LIKE '%keyword%'\n"
        "- Always end with semicolon\n"
        "- ORDER BY main metric DESC unless time-based trend\n"
    )
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": query}
            ],
            temperature=0.1,
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        cleaned = clean_sql(raw)
        if "SELECT" not in cleaned.upper():
            return None
        return cleaned
    except Exception:
        return None

# ── RULE-BASED FALLBACK (clean explicit rules) ──
def rule_based_sql(query: str):
    q = query.lower().strip()

    # total sales
    if "total sales" in q:
        return "SELECT ROUND(SUM(sales), 2) AS total_sales FROM sales_data;"

    # sales by region
    if "sales by region" in q:
        return "SELECT region, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY region ORDER BY total_sales DESC;"

    # sales by category
    if "sales by category" in q:
        return "SELECT category, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY category ORDER BY total_sales DESC;"

    # sales by sub-category
    if "sub" in q and "category" in q:
        return "SELECT sub_category, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY sub_category ORDER BY total_sales DESC;"

    # profit by category
    if "profit by category" in q:
        return "SELECT category, ROUND(SUM(profit), 2) AS total_profit FROM sales_data GROUP BY category ORDER BY total_profit DESC;"

    # quantity by category
    if "quantity by category" in q:
        return "SELECT category, SUM(quantity) AS total_quantity FROM sales_data GROUP BY category ORDER BY total_quantity DESC;"

    # average discount by region
    if "average discount" in q and "region" in q:
        return "SELECT region, ROUND(AVG(discount), 4) AS avg_discount FROM sales_data GROUP BY region ORDER BY avg_discount DESC;"

    # top N states by sales
    if "top" in q and "state" in q and "sales" in q:
        match = re.search(r'top\s+(\d+)', q)
        n = match.group(1) if match else "5"
        return f"SELECT state, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY state ORDER BY total_sales DESC LIMIT {n};"

    # bottom N states by sales
    if "bottom" in q and "state" in q and "sales" in q:
        match = re.search(r'bottom\s+(\d+)', q)
        n = match.group(1) if match else "5"
        return f"SELECT state, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY state ORDER BY total_sales ASC LIMIT {n};"

    # top N products by profit
    if "top" in q and "product" in q and "profit" in q:
        match = re.search(r'top\s+(\d+)', q)
        n = match.group(1) if match else "10"
        return f"SELECT product_name, ROUND(SUM(profit), 2) AS total_profit FROM sales_data GROUP BY product_name ORDER BY total_profit DESC LIMIT {n};"

    # top N products by sales
    if "top" in q and "product" in q and "sales" in q:
        match = re.search(r'top\s+(\d+)', q)
        n = match.group(1) if match else "10"
        return f"SELECT product_name, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY product_name ORDER BY total_sales DESC LIMIT {n};"

    # top N customers by sales
    if "top" in q and "customer" in q and "sales" in q:
        match = re.search(r'top\s+(\d+)', q)
        n = match.group(1) if match else "10"
        return f"SELECT customer_name, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY customer_name ORDER BY total_sales DESC LIMIT {n};"

    # count of customers
    if "count" in q and "customer" in q:
        return "SELECT COUNT(DISTINCT customer_id) AS customer_count FROM sales_data;"

    # sales greater/less than
    if "sales greater than" in q or "sales more than" in q or "sales above" in q:
        match = re.search(r'(\d+)', q)
        val = match.group(1) if match else "500"
        return f"SELECT * FROM sales_data WHERE sales > {val} ORDER BY sales DESC;"

    if "sales less than" in q or "sales below" in q or "sales under" in q:
        match = re.search(r'(\d+)', q)
        val = match.group(1) if match else "500"
        return f"SELECT * FROM sales_data WHERE sales < {val} ORDER BY sales DESC;"

    # profit greater than
    if "profit greater than" in q or "profit more than" in q:
        match = re.search(r'(\d+)', q)
        val = match.group(1) if match else "100"
        return f"SELECT * FROM sales_data WHERE profit > {val} ORDER BY profit DESC;"

    # orders by month and year
    if "order" in q and "month" in q and "year" in q:
        year_match = re.search(r'\b(201[4-9]|202[0-9])\b', q)
        if year_match:
            yr = year_match.group(1)
            return f"SELECT substr(order_date, 4, 2) AS month, COUNT(DISTINCT order_id) AS order_count FROM sales_data WHERE substr(order_date, 7, 4) = '{yr}' GROUP BY substr(order_date, 4, 2) ORDER BY month ASC;"
        return "SELECT substr(order_date, 7, 4) AS year, substr(order_date, 4, 2) AS month, COUNT(DISTINCT order_id) AS order_count FROM sales_data GROUP BY substr(order_date, 7, 4), substr(order_date, 4, 2) ORDER BY year ASC, month ASC;"

    # orders by month only
    if "order" in q and "month" in q:
        year_match = re.search(r'\b(201[4-9]|202[0-9])\b', q)
        if year_match:
            yr = year_match.group(1)
            return f"SELECT substr(order_date, 4, 2) AS month, COUNT(DISTINCT order_id) AS order_count FROM sales_data WHERE substr(order_date, 7, 4) = '{yr}' GROUP BY month ORDER BY month ASC;"
        return "SELECT substr(order_date, 4, 2) AS month, COUNT(DISTINCT order_id) AS order_count FROM sales_data GROUP BY month ORDER BY month ASC;"

    # sales by year
    if "sales by year" in q or "sales per year" in q or "yearly sales" in q:
        return "SELECT substr(order_date, 7, 4) AS year, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY year ORDER BY year ASC;"

    # total sales in year
    if "total sales in" in q or ("sales in" in q and re.search(r'\b(201[4-9]|202[0-9])\b', q) and "state" not in q and "city" not in q):
        year_match = re.search(r'\b(201[4-9]|202[0-9])\b', q)
        if year_match:
            yr = year_match.group(1)
            return f"SELECT ROUND(SUM(sales), 2) AS total_sales FROM sales_data WHERE substr(order_date, 7, 4) = '{yr}';"

    # sales by city in state
    if "sales by city" in q:
        state_map = {
            "california": "California", "florida": "Florida",
            "texas": "Texas", "new york": "New York",
            "washington": "Washington", "illinois": "Illinois",
            "ohio": "Ohio", "arizona": "Arizona", "michigan": "Michigan",
            "georgia": "Georgia", "north carolina": "North Carolina",
        }
        for key, val in state_map.items():
            if key in q:
                return f"SELECT city, ROUND(SUM(sales), 2) AS total_sales FROM sales_data WHERE state = '{val}' GROUP BY city ORDER BY total_sales DESC;"
        return "SELECT city, ROUND(SUM(sales), 2) AS total_sales FROM sales_data GROUP BY city ORDER BY total_sales DESC LIMIT 20;"

    # sales in state(s) with optional year and product
    if "sales in" in q or "sales of" in q:
        state_map = {
            "california": "California", "florida": "Florida",
            "texas": "Texas", "new york": "New York",
            "washington": "Washington", "illinois": "Illinois",
            "ohio": "Ohio", "arizona": "Arizona", "michigan": "Michigan",
            "georgia": "Georgia", "north carolina": "North Carolina",
            "pennsylvania": "Pennsylvania", "virginia": "Virginia",
        }
        found_states = [val for key, val in state_map.items() if key in q]
        year_match   = re.search(r'\b(201[4-9]|202[0-9])\b', q)
        prod_match   = re.search(r'sales of (.+?) in', q)

        if found_states:
            state_conditions = " OR ".join([f"state = '{s}'" for s in found_states])
            sql = f"SELECT * FROM sales_data WHERE ({state_conditions})"
            if prod_match:
                product = prod_match.group(1).strip()
                sql += f" AND LOWER(product_name) LIKE '%{product.lower()}%'"
            if year_match:
                sql += f" AND substr(order_date, 7, 4) = '{year_match.group(1)}'"
            sql += " ORDER BY sales DESC;"
            return sql

    return None

# ── DISPLAY ──
def display_results(sql_query, source):
    badge_class = "badge-ai" if source == "ai" else "badge-rule"
    badge_label = "✦ AI · Groq" if source == "ai" else "⚙ Rule-Based"
    st.markdown(f'<span class="badge {badge_class}">{badge_label}</span>', unsafe_allow_html=True)

    with st.expander("VIEW GENERATED SQL"):
        st.code(sql_query, language="sql")

    result = pd.read_sql(sql_query, conn)

    if result.empty:
        st.warning("No data found.")
        return

    st.markdown(
        f'<div class="result-meta">{len(result)} ROW{"S" if len(result) != 1 else ""} RETURNED</div>',
        unsafe_allow_html=True
    )
    st.dataframe(result, use_container_width=True, hide_index=True)

    if (
        len(result.columns) == 2
        and pd.api.types.is_numeric_dtype(result.iloc[:, 1])
        and 1 < len(result) <= 50
    ):
        st.markdown("---")
        st.bar_chart(result.set_index(result.columns[0]), color="#00ff9d", use_container_width=True)

# ── MAIN ──
if run:
    if not user_input.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Thinking..."):
            sql_query = ai_sql(user_input)
            source    = "ai"
            if sql_query is None:
                sql_query = rule_based_sql(user_input)
                source    = "rule-based"

        if sql_query is None:
            st.error("Could not understand that query. Try rephrasing it.")
        else:
            try:
                display_results(sql_query, source)
            except Exception as e:
                if source == "ai":
                    fallback = rule_based_sql(user_input)
                    if fallback:
                        try:
                            display_results(fallback, "rule-based")
                        except Exception as e2:
                            st.error(f"SQL Error: {e2}")
                    else:
                        st.error(f"SQL Error: {e}")
                else:
                    st.error(f"SQL Error: {e}")

st.markdown('<div class="footer">SMART DATA CHATBOT · BUILT BY SHANTANU SINGLA</div>', unsafe_allow_html=True)
