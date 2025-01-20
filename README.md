# AdminDashboardBackend
Backend to AdminDashboard developed using FastAPI. Shoul be run in port 7000

1. Clone the repository.
2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up the `.env` file with your OpenAI API key.
    ```bash
    OPENAI_API_KEY=your_openai_api_key
    ```

6. Run the application:
    ```bash
    uvicorn main:app --reload --port 7000
    ```
