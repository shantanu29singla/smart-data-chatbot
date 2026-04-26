💬 Smart Data Chatbot (Natural Language → SQL)
A Streamlit-based AI chatbot that converts plain English questions into SQL queries and returns results with visualizations — powered by a hybrid AI-first engine using Groq LLM with a strong rule-based fallback.

🚀 What it does
Type a question in plain English like "top 5 states by sales" or "number of orders by month and year" — the chatbot converts it to SQL, runs it on the database, and shows you the result with a chart.

---

## 📸 Preview

### Query Suggestions Dropdown
![Dropdown](screenshot1.png)

### Query Result Example
![Result](screenshot2.png)

---

🧠 How It Works
User types a question
        ↓
Groq AI (LLaMA 3 70B) generates SQL      →   ✦ AI · Groq badge
        ↓ (if AI fails)
Rule-based engine handles it             →   ⚙ Rule-Based badge
        ↓ (if AI SQL crashes on execution)
Rule-based retries automatically
        ↓
SQL runs on sales.db → Table + Bar Chart 

---
✅ Supported Query Types
CategoryExampleSimple aggregationstotal sales, count of customersGroup by dimensionsales by category, sales by regionTop / Bottom Ntop 5 states by sales, bottom 3 citiesLocation filtersales in Florida, sales in Texas and New YorkProduct searchsales of binder in FloridaDate filtersales in California in 2017Month/Year trendsnumber of orders by month and yearThreshold filtersales greater than 500Profit queriestop 10 products by profitAverageaverage discount by region

## 🧰 Technologies Used

- Python  
- Streamlit  
- SQLite  
- Pandas  
- Groq API (LLaMA 3 70B)AI SQL generation
- python-dotenvSecure API key management
---

📂 Dataset
Superstore Sales dataset loaded into sales.db via load_data.py.
Table: sales_data
Columns: order_id, order_date, ship_date, ship_mode, customer_id, customer_name, segment, country, city, state, postal_code, region, product_id, category, sub_category, product_name, sales, quantity, discount, profit
---
⚙️ Setup & Run
1. Clone the repo
bashgit clone https://github.com/shantanu29singla/smart-data-chatbot.git
cd smart-data-chatbot
2. Install dependencies
bashpip install -r requirements.txt
3. Add your Groq API key
bashcp .env.example .env
# Open .env and paste your Groq API key
# Get a free key at: console.groq.com
4. Load the dataset
bashpython load_data.py
5. Run the app
bashstreamlit run app.py
6. Open in browser
http://localhost:8501

📁 Project Structure
smart-data-chatbot/
├── app.py              # Main Streamlit app (AI-first hybrid engine)
├── load_data.py        # Loads CSV dataset into SQLite
├── sales.db            # SQLite database (Superstore Sales)
├── requirements.txt    # Python dependencies
├── .env.example        # API key template (safe to share)
├── screenshot1.png     # UI preview
└── screenshot2.png     # Result preview

👨‍💻 Author
Shantanu Singla



