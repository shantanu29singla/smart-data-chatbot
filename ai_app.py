import streamlit as st
import sqlite3
import pandas as pd
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

# ── ENV & CONFIG ─────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="Smart Data Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d0d0d; color: #e8e8e8; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 760px; }

.hero {
    text-align: center;
    padding: 2.5rem 0 2rem 0;
    border-bottom: 1px solid #222;
    margin-bottom: 2rem;
}
.hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 0.3rem;
}
.hero p { color: #666; font-size: 0.9rem; font-weight: 300; letter-spacing: 0.04em; }
.hero .dot { color: #00ff9d; }

label, .stTextInput label, .stSelectbox label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    color: #555 !important;
    text-transform: uppercase !important;
}

.stTextInput input {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1rem !important;
    transition: border-color 0.2s ease;
}
.stTextInput input:focus {
    border-color: #00ff9d !important;
    box-shadow: 0 0 0 3px rgba(0, 255, 157, 0.08) !important;
}
.stSelectbox > div > div {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e8e8e8 !important;
}
.stButton > button {
    background: #00ff9d !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s ease, transform 0.1s ease;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px); }
.stButton > button:active { transform: translateY(0px); }

.badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}
.badge-rule { background: #1a2a1f; color: #00ff9d; border: 1px solid #00ff9d33; }
.badge-ai   { background: #1a1a2a; color: #7b8cff; border: 1px solid #7b8cff33; }

.result-meta {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #444;
    letter-spacing: 0.06em;
    margin-bottom: 0.75rem;
}
.streamlit-expanderHeader {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #555 !important;
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
}
.stAlert { border-radius: 8px !important; font-size: 0.88rem !important; }
hr { border-color: #1a1a1a !important; }

.footer {
    text-align: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #333;
    letter-spacing: 0.08em;
    padding-top: 2.5rem;
    border-top: 1px solid #1a1a1a;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# ── GROQ CLIENT ───────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Add it to your .env file.")
        st.stop()
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

# ── DB CONNECTION ─────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return sqlite3.connect("sales.db", check_same_thread=False)

client = get_client()
conn   = get_connection()

# ── LOAD UNIQUE VALUES ────────────────────────────────────────
@st.cache_data
def get_unique_values(column):
    query = f"SELECT DISTINCT {column} FROM sales_data"
    return pd.read_sql(query, conn)[column].str.lower().tolist()

states     = get_unique_values("state")
cities     = get_unique_values("city")
categories = get_unique_values("category")

# ── HERO ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Smart Data Chatbot<span class="dot">.</span></h1>
    <p>NATURAL LANGUAGE → SQL → INSIGHTS</p>
</div>
""", unsafe_allow_html=True)

# ── SAMPLE QUERIES ────────────────────────────────────────────
suggestions = [
    "",
    # ── Simple aggregations ──
    "total sales",
    "count of customers",
    # ── Group by ──
    "sales by category",
    "sales by region",
    "sales by sub-category",
    "sales by segment",
    "average discount by region",
    "total profit by category",
    # ── Top / Bottom ──
    "top 5 states by sales",
    "top 10 products by profit",
    "top 5 customers by sales",
    "bottom 3 cities by sales",
    # ── Location filters ──
    "sales in Florida",
    "sales in California",
    "sales in Texas and New York",
    # ── Product search ──
    "sales of binder in Florida",
    "sales of chair by region",
    # ── Date filters ──
    "sales in California in 2017",
    "total sales in 2016",
    "number of orders by month and year",
    "number of orders by month in 2017",
    "sales by year",
    # ── Threshold ──
    "sales greater than 500",
    "profit greater than 100",
]

selected   = st.selectbox("💡 Sample queries", suggestions, help="Pick one or type your own below")
user_input = st.text_input("Ask anything about the data", value=selected, placeholder="e.g. number of orders by month and year")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run = st.button("⚡ Run Query", use_container_width=True)

# ── CLEAN SQL ─────────────────────────────────────────────────
def clean_sql(raw: str) -> str:
    raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE).strip()
    raw = raw.strip("`").strip()
    raw = raw.split(";")[0].strip() + ";"
    return raw

# ── AI SQL (PRIMARY) ──────────────────────────────────────────
def ai_sql(query: str):
    system_prompt = (
        "You are a precise SQL expert working with a retail sales database.\n\n"
        "Table: sales_data\n"
        "Columns: row_id, order_id, order_date, ship_date, ship_mode, customer_id, customer_name,\n"
        "         segment, country, city, state, postal_code, region, product_id, category,\n"
        "         sub_category, product_name, sales, quantity, discount, profit\n\n"
        "CRITICAL: order_date is stored as MM-DD-YYYY string format (e.g. 08-11-2017)\n"
        "So to extract dates you MUST use substr():\n"
        "  - Extract day:  substr(order_date, 4, 2)\n"
        "  - Extract month: substr(order_date, 4, 2)\n"
        "  - Extract year:   substr(order_date, 7, 4)\n"
        "  - NEVER use strftime() as it will not work with this date format\n\n"
        "Date examples:\n"
        "  - Filter by year 2017: WHERE substr(order_date, 7, 4) = '2017'\n"
        "  - Group by year: GROUP BY substr(order_date, 7, 4)\n"
        "  - Group by month and year: GROUP BY substr(order_date, 7, 4), substr(order_date, 4, 2)\n"
        "    with SELECT substr(order_date, 7, 4) AS year, substr(order_date, 4, 2) AS month\n"
        "  - NEVER add year WHERE filter unless user mentions a specific year\n\n"
        "STRICT Rules:\n"
        "- Return ONLY the raw SQL query, no explanation, no markdown, no backticks\n"
        "- Use exact column names (all lowercase with underscores)\n"
        "- Use ROUND(value, 2) for sales, profit, discount\n"
        "- Always end with semicolon\n\n"
        "Counting:\n"
        "- Count orders: COUNT(DISTINCT order_id) AS order_count\n"
        "- Count customers: COUNT(DISTINCT customer_id) AS customer_count\n\n"
        "Filtering:\n"
        "- Products: product_name LIKE '%keyword%'\n"
        "- Value threshold: WHERE sales > 500\n"
        "- Multiple states: WHERE state IN ('California', 'Texas')\n\n"
        "For time-based trends ORDER BY year ASC, month ASC.\n"
        "For all other queries ORDER BY the main metric DESC."
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

# ── NORMALIZE ─────────────────────────────────────────────────
def normalize(text):
    text = text.lower()
    text = text.replace("states",      "state")
    text = text.replace("cities",      "city")
    text = text.replace("revenue",     "sales")
    text = text.replace("orders",      "order")
    text = text.replace("sub-category","sub_category")
    text = text.replace("subcategory", "sub_category")
    text = text.replace("number of order", "order count")
    text = text.replace("how many order",  "order count")
    return text

# ── RULE-BASED FALLBACK ───────────────────────────────────────
def rule_based_sql(user_input: str):
    q = normalize(user_input)

    has_intent = any(k in q for k in [
        "sales", "customer", "profit", "order", "discount",
        "quantity", "revenue", "count", "total", "average", "avg"
    ])
    if not has_intent:
        return None

    # ── METRIC ──
    if "order count" in q or ("count" in q and "order" in q):
        agg, agg_label = "COUNT(DISTINCT order_id)", "order_count"
    elif "count" in q and "customer" in q:
        agg, agg_label = "COUNT(DISTINCT customer_id)", "customer_count"
    elif "average" in q or "avg" in q:
        if "discount" in q:
            agg, agg_label = "ROUND(AVG(discount), 4)", "avg_discount"
        elif "profit" in q:
            agg, agg_label = "ROUND(AVG(profit), 2)", "avg_profit"
        elif "quantity" in q:
            agg, agg_label = "ROUND(AVG(quantity), 2)", "avg_quantity"
        else:
            agg, agg_label = "ROUND(AVG(sales), 2)", "avg_sales"
    elif "profit" in q:
        agg, agg_label = "ROUND(SUM(profit), 2)", "total_profit"
    elif "quantity" in q:
        agg, agg_label = "SUM(quantity)", "total_quantity"
    elif "discount" in q:
        agg, agg_label = "ROUND(AVG(discount), 4)", "avg_discount"
    else:
        agg, agg_label = "ROUND(SUM(sales), 2)", "total_sales"

    # ── GROUP BY ──
    # NOTE: date format is MM-DD-YYYY so we use substr()
    group_by     = None
    group_label  = None
    extra_select = ""

    if ("month" in q and "year" in q) or "month and year" in q:
        group_by     = "substr(order_date, 7, 4), substr(order_date, 4, 2)"
        group_label  = "month_year"
        extra_select = "substr(order_date, 7, 4) AS year, substr(order_date, 4, 2) AS month, "
    elif "by year" in q or "each year" in q or "yearly" in q:
        group_by     = "substr(order_date, 7, 4)"
        group_label  = "year"
        extra_select = "substr(order_date, 7, 4) AS year, "
    elif "by month" in q or "each month" in q or "monthly" in q:
        group_by     = "substr(order_date, 4, 2)"
        group_label  = "month"
        extra_select = "substr(order_date, 4, 2) AS month, "
    elif "by state" in q:
        group_by, group_label = "state", "state"
    elif "by city" in q:
        group_by, group_label = "city", "city"
    elif "by sub_category" in q or "by sub" in q:
        group_by, group_label = "sub_category", "sub_category"
    elif "by category" in q:
        group_by, group_label = "category", "category"
    elif "by region" in q:
        group_by, group_label = "region", "region"
    elif "by segment" in q:
        group_by, group_label = "segment", "segment"
    elif "by ship" in q:
        group_by, group_label = "ship_mode", "ship_mode"
    elif "by product" in q:
        group_by, group_label = "product_name", "product_name"
    elif "by customer" in q:
        group_by, group_label = "customer_name", "customer_name"

    if group_by:
        if extra_select:
            select_part = f"{extra_select}{agg} AS {agg_label}"
        else:
            select_part = f"{group_by}, {agg} AS {agg_label}"
    else:
        select_part = f"{agg} AS {agg_label}"

    # ── TOP / BOTTOM ──
    order_by = ""
    limit    = ""
    match = re.search(r"(top|bottom)\s*(\d+)", q)
    if match:
        direction = match.group(1)
        n         = match.group(2)
        limit     = f" LIMIT {n}"
        order_by  = f" ORDER BY {agg} {'DESC' if direction == 'top' else 'ASC'}"
    elif group_by:
        if group_label in ["month_year", "year", "month"]:
            order_by = " ORDER BY year ASC, month ASC" if group_label == "month_year" else f" ORDER BY {group_label} ASC"
        else:
            order_by = f" ORDER BY {agg} DESC"

    # ── CONDITIONS ──
    conditions = []

    # Year filter — only when specific year mentioned AND not grouping by year/month
    if group_label not in ["year", "month", "month_year"]:
        year_match = re.search(r"\b(201[4-9]|202[0-9])\b", q)
        if year_match:
            conditions.append(f"substr(order_date, 7, 4) = '{year_match.group(1)}'")
    else:
        # If grouping by year/month but a specific year is mentioned, filter to that year
        year_match = re.search(r"\b(201[4-9]|202[0-9])\b", q)
        if year_match and group_label == "month":
            conditions.append(f"substr(order_date, 7, 4) = '{year_match.group(1)}'")

    # Value threshold
    thresh = re.search(r"(greater than|more than|above|over|less than|below|under)\s+(\d+(?:\.\d+)?)", q)
    if thresh:
        direction = thresh.group(1)
        value     = thresh.group(2)
        col       = "profit" if "profit" in q else "sales"
        op        = ">" if direction in ["greater than", "more than", "above", "over"] else "<"
        conditions.append(f"{col} {op} {value}")

    # State filter
    matched_states = [s for s in states if s in q]
    if matched_states:
        vals = "', '".join([s.title() for s in matched_states])
        conditions.append(f"state IN ('{vals}')")

    # City filter
    matched_cities = [c for c in cities if c in q]
    if matched_cities:
        vals = "', '".join([c.title() for c in matched_cities])
        conditions.append(f"city IN ('{vals}')")

    # Category filter
    matched_cats = [c for c in categories if c in q]
    if matched_cats:
        vals = "', '".join([c.title() for c in matched_cats])
        conditions.append(f"category IN ('{vals}')")

    # Product keyword search
    skip_words = {
        "sales", "state", "city", "category", "region", "product",
        "total", "count", "top", "bottom", "show", "what", "give",
        "profit", "order", "customer", "average", "find", "list",
        "the", "and", "for", "from", "with", "that", "this", "in",
        "by", "of", "is", "are", "where", "how", "many", "month",
        "year", "greater", "than", "more", "above", "over", "less",
        "below", "under", "number", "discount", "quantity", "avg",
        "sub_category", "segment", "ship", "mode", "between", "per",
        "which", "each", "every", "across", "monthly", "yearly", "give"
    }
    words = q.split()
    product_keywords = [
        w for w in words
        if len(w) > 3
        and w not in skip_words
        and not re.match(r"201[4-9]|202[0-9]", w)
        and w not in [s.lower() for s in matched_states]
        and w not in [c.lower() for c in matched_cities]
        and w not in [c.lower() for c in matched_cats]
    ]
    if product_keywords:
        product_conditions = [f"product_name LIKE '%{w}%'" for w in product_keywords]
        conditions.append("(" + " OR ".join(product_conditions) + ")")

    # ── BUILD QUERY ──
    sql = f"SELECT {select_part} FROM sales_data"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    if group_by:
        sql += f" GROUP BY {group_by}"
    sql += order_by + limit + ";"

    return sql

# ── DISPLAY RESULTS ───────────────────────────────────────────
def display_results(sql_query, source):
    badge_class = "badge-ai" if source == "ai" else "badge-rule"
    badge_label = "✦ AI · Groq" if source == "ai" else "⚙ Rule-Based"
    st.markdown(f'<span class="badge {badge_class}">{badge_label}</span>', unsafe_allow_html=True)

    with st.expander("VIEW GENERATED SQL"):
        st.code(sql_query, language="sql")

    result = pd.read_sql(sql_query, conn)

    if result.empty:
        st.warning("No data found for that query.")
        return

    st.markdown(
        f'<div class="result-meta">{len(result)} ROW{"S" if len(result) != 1 else ""} RETURNED</div>',
        unsafe_allow_html=True
    )
    st.dataframe(result, use_container_width=True, hide_index=True)

    # Show bar chart when it makes sense
    if (
        len(result.columns) == 2
        and pd.api.types.is_numeric_dtype(result.iloc[:, 1])
        and len(result) > 1
    ):
        st.markdown("---")
        st.bar_chart(
            result.set_index(result.columns[0]),
            color="#00ff9d",
            use_container_width=True
        )

# ── MAIN LOGIC ────────────────────────────────────────────────
if run:
    if not user_input.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Thinking..."):
            # AI FIRST
            sql_query = ai_sql(user_input)
            source    = "ai"

            # RULE-BASED FALLBACK if AI returns nothing
            if sql_query is None:
                sql_query = rule_based_sql(user_input)
                source    = "rule-based"

        if sql_query is None:
            st.error("Could not understand that query. Try rephrasing it.")
        else:
            try:
                display_results(sql_query, source)
            except Exception as e:
                # If AI SQL fails at execution, retry with rule-based
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

# ── FOOTER ────────────────────────────────────────────────────
st.markdown('<div class="footer">SMART DATA CHATBOT · BUILT BY SHANTANU SINGLA</div>', unsafe_allow_html=True)
