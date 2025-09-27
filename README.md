# NLP Query Engine for Employee Data - Backend Setup

This section provides instructions for setting up the **FastAPI Backend** for the NLP Query Engine for Employee Data, which handles schema discovery, document ingestion (embeddings + FAISS), query engine, and caching.

---

## Getting Started

1.  **Clone the Repository** Clone the project from GitHub to your local machine:
    ```bash
    git clone https://github.com/sushrutha777/NLP-Query-Engine.git
    cd NLP-Query-Engine
    ```

---

## Prerequisites
- **Python**: 3.8 or higher
- **Tools**: `pip`
- **Optional**: Virtual environment tool (e.g., `venv` or `virtualenv`)

---

## Backend Setup
1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment**:
    *For Linux/macOS:*
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *For Windows (PowerShell):*
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
4.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Initialize the sample SQLite database**:
    ```bash
    python sample_db_init.py
    ```
    This creates a `company_demo.db` file in the backend directory.

6.  **Run the FastAPI backend**:
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    The `--reload` flag enables auto-reload for development. The server will run on `http://localhost:8000`.

7.  **Verify the API**:
    Open your browser and navigate to `http://localhost:8000/docs` to view the FastAPI interactive API documentation.

---

## Frontend setup

1. **In a new terminal**:
    ```bash
    cd project/frontend
    npm install
    npm start

    ```


Open: http://localhost:3000

## Demo Flow

1. **Connect to Database**
   - In the UI, go to **DatabaseConnector**.
   - Use `sqlite:///company_demo.db`.
   - Click **Connect & Analyze**.

2. **Upload Documents (Optional)**
   - Upload documents in **txt**, **pdf**, or **docx** format.

3. **Run Queries from Query Panel**
   - How many employees do we have?
   - Average salary by department
   - List employees hired this year
   - Show me Python developers
   - Top 5 highest paid employees in each department
   - Document query: Show me resumes that mention leadership

4. **View Results**
   - Check results and metrics in the UI.


## Notes
- Ensure the `requirements.txt` file exists and contains all necessary Python packages (e.g., fastapi, uvicorn, faiss-cpu, etc.).
- Verify that the `sample_db_init.py` script successfully creates `company_demo.db`.
- Port `8000` should not be in use by other applications.
- For production, remove the `--reload` flag from the `uvicorn` command to disable auto-reload.

---

## Troubleshooting
- **Backend fails to start**: Check if `main.py` exists and the `app` object is correctly defined. Ensure all dependencies in `requirements.txt` are installed.
- **Database issues**: Verify that `company_demo.db` was created and is accessible in the backend directory.
