# smart-data-chatbot
Chatbot that converts English queries into SQL
# 💬 Smart Data Chatbot (SQL + NLP)

## 📌 Project Overview
This project is a **Natural Language to SQL chatbot** that allows users to query a dataset using simple English sentences.

Instead of writing SQL queries manually, users can ask questions like:
- "top 5 states by sales"
- "sales of binder in Florida"
- "total sales"

The system converts these queries into SQL and fetches results from a database.

---

## ⚙️ Technologies Used
- Python
- Streamlit (UI)
- SQLite (Database)
- Pandas (Data Handling)
- Regex (Query Parsing)

---

## 📂 Dataset Used
- Superstore Sales Dataset (CSV)
- Columns include:
  - Order Date
  - Customer Name
  - Region
  - State
  - Category
  - Product Name
  - Sales

---

## 🧠 Features

### ✅ Natural Language Queries
Users can type queries in English instead of SQL.

### ✅ SQL Generation
The system converts user input into SQL queries automatically.

### ✅ Dynamic Filtering
Supports:
- State
- City
- Region
- Category
- Product

### ✅ Aggregations
- SUM
- AVG
- MAX
- MIN
- COUNT

### ✅ Top / Bottom Analysis
- Top N results
- Bottom N results

### ✅ Product Search
Example:
> "sales of binder in Florida"

### ✅ Multi-Condition Queries
Example:
> "sales in Texas and California"

### ✅ Data Visualization
- Bar charts generated automatically

### ✅ Dropdown Suggestions
- Predefined queries for quick access

---

## 🖥️ How to Run

1. Install dependencies:
```bash
pip install streamlit pandas
