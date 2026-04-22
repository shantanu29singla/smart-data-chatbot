# 💬 Smart Data Chatbot (Natural Language → SQL)

A Streamlit-based chatbot that converts natural language queries into SQL and displays results with visualization.

---

## 📌 Overview
This project allows users to query data using simple English instead of writing SQL queries.

Users can ask questions like:
- "Top 5 states by sales"
- "Sales of binder in Florida"
- "Total sales"

The system converts these queries into SQL and retrieves results from a database.

---

## 📸 Preview

### Query Suggestions Dropdown
![Dropdown](screenshot1.png)

### Query Result Example
![Result](screenshot2.png)

---

## 🚀 Features

- Natural language queries  
- Automatic SQL generation  
- Data aggregation (SUM, AVG, MIN, MAX, COUNT)  
- Filtering (State, City, Category, Product)  
- Multi-condition queries  
- Product-based queries  
- Data visualization (charts)  
- Query suggestion dropdown  

---

## 🧰 Technologies Used

- Python  
- Streamlit  
- SQLite  
- Pandas  

---

## 📂 Dataset

Superstore Sales dataset stored in `sales.db`.

---

## 🖥️ How to Run

1. Install dependencies  
pip install streamlit pandas  

2. Run the app  
streamlit run app.py  

3. Open in browser  
http://localhost:8501  

---

## 🧪 Example Queries

- total sales  
- top 5 states by sales  
- bottom 3 cities by sales  
- sales in Florida  
- sales of binder in Florida  
- sales in Texas and New York  

---

## ⚠️ Limitations

- Rule-based system (not AI-based)  
- Limited understanding of complex queries  

---

## 🔮 Future Improvements

- Add AI integration  
- Improve UI  
- Handle typos  

---

## 👨‍💻 Author

Shantanu Singla
