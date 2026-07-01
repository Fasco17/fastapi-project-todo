# Multi-Currency Wallet API 🚀

An asynchronous REST API built with FastAPI for managing personal user wallets, tracking financial operations, and performing inter-wallet transfers with currency conversion.

## 🛠 Tech Stack

* **Language:** Python 3.11+
* **Framework:** FastAPI (Asynchronous Web Framework)
* **ASGI Server:** Uvicorn
* **Database & ORM:** SQLite + SQLAlchemy 2.0
* **Data Validation:** Pydantic v2
* **Testing:** Pytest
* **HTTP Client:** HTTPX / Requests (for external exchange rate integration)

## 💡 Key Features

* **User Authentication:** Secure registration and login.
* **Wallet Management:** Create and manage multiple wallets in different currencies (`USD`, `EUR`, `CZK`).
* **Transactions & Transfers:** Perform internal transfers between wallets with automatic conversion based on exchange rates.
* **Operation History:** Track and retrieve a complete list of all financial operations.
* **Automated Testing:** Core logic covered with robust unit tests via `pytest`.

## 🚀 Local Setup Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Fasco17/fastapi-project-todo.git
   cd fast-api-todo-app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open in your browser:**
   [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)