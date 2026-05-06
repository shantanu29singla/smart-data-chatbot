# 💬 Smart Data Chatbot (Natural Language → SQL)

A Streamlit-based AI chatbot that converts plain English questions into SQL queries and returns results with visualizations - powered by a hybrid AI-first engine using Groq LLM with a rule-based fallback.

---

## 🚀 What It Does

Ask questions in plain English like:

- "top 5 states by sales"
- "sales in california in 2017"
- "number of orders by month and year"

The chatbot:
1. Converts your question into SQL  
2. Runs it on a database  
3. Displays results with charts  

---

## 📸 Preview

### 🔹 Query Interface
![Dropdown](screenshot1.png)

### 🔹 Query Result with Chart
![Result](screenshot2.png)

---

## 🧠 How It Works

User Input (Natural Language)  
↓  
AI (Groq LLaMA 3.1) generates SQL → 🤖 AI Mode  
↓ (fallback if needed)  
Rule-Based Engine → ⚙ Rule Mode  
↓  
SQL executed on SQLite database  
↓  
Results displayed (Table + Chart)  

---

## ✅ Supported Query Types

- total sales  
- count of customers  
- sales by category  
- sales by region  
- top 5 states by sales  
- bottom 3 cities by sales  
- sales in Florida  
- sales in Texas and New York  
- sales of binder in Florida  
- sales in California in 2017  
- number of orders by month and year  
- sales greater than 500  
- top 10 products by profit  
- average discount by region  

---

## 🧰 Tech Stack

- Python  
- Streamlit  
- SQLite  
- Pandas  
- Groq API (LLaMA 3.1)  
- python-dotenv  

---

## 📂 Dataset

Superstore Sales dataset stored in `sales.db`.

Table: `sales_data`

Columns:
order_id, order_date, ship_date, ship_mode, customer_id,  
customer_name, segment, country, city, state, postal_code,  
region, product_id, category, sub_category, product_name,  
sales, quantity, discount, profit  

---

## ⚙️ Setup & Run

1. Clone the repository  
git clone https://github.com/shantanu29singla/smart-data-chatbot.git  
cd smart-data-chatbot  

2. Install dependencies  
pip install -r requirements.txt  

3. Add your Groq API key  
Create a `.env` file:  
GROQ_API_KEY=your_key_here  

Get key from: https://console.groq.com  

4. Load dataset (if needed)  
python load_data.py  

5. Run the app  
streamlit run app.py  

6. Open in browser  
http://localhost:8501  

---

## 📁 Project Structure

smart-data-chatbot/  
├── app.py  
├── load_data.py  
├── sales.db  
├── requirements.txt  
├── .env.example  
├── screenshot1.png  
└── screenshot2.png  

---

## ⚠️ Notes

- AI-generated SQL may sometimes be imperfect  
- Rule-based system improves reliability  
- Internet required for Groq API  

---

## 👨‍💻 Author

Shantanu Singla  
GitHub: https://github.com/shantanu29singla  
LinkedIn: https://linkedin.com/in/shantanu-singla  
