# Copilot-chan

Copilot-chan is an intelligent virtual assistant (AI Agent) built on a microservices architecture, leveraging the power of Google Gemini and Mem0 to deliver a natural and personalized conversational experience.

## Key Features

*   **Multi-model Strategy**: Combines `RootAgent` (fast, instant response) and `ReasonerAgent` (deep reasoning for complex tasks).
*   **Long-term Memory**: Remembers user preferences, habits, and important information using `Mem0`.
*   **Dynamic Instruction**: Automatically adjusts response style based on user memory.
*   **Google Search**: Integrates Google Search to retrieve the latest information.
*   **Microservices Architecture**: Separates Agent Server and API Server, facilitating easy scaling.

## System Requirements

*   Python >= 3.12
*   PostgreSQL (for Mem0 and Session storage)
*   Google Cloud Account (for Gemini API/Vertex AI)
*   Mem0 Account (if using managed service) or self-hosted.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd copilot-chan
    ```

2.  **Install dependencies:**
    The project uses `uv` for package management. If you don't have `uv`, install it first.
    ```bash
    pip install uv
    uv sync
    ```

3.  **Configure environment variables:**
    Copy `.env.example` to `.env` and fill in the necessary information:
    ```bash
    cp .env.example .env
    ```

    *   `GOOGLE_GENAI_USE_VERTEXAI`: `TRUE` to use Vertex AI, `FALSE` to use Gemini API Key.
    *   `GOOGLE_API_KEY`: Your API Key.
    *   `APP_NAME`: Application name.
    *   `MEM0_API_KEY`: Mem0 API Key.
    *   `DB_URL`: Database connection string (e.g., `postgresql://user:pass@localhost:5432/dbname`).
    *   `IS_DEV`: `true` to run in dev mode (hot reload, verbose).
    *   `LOCAL_AGENT_PORT`: Port for Agent Server (default 8001).

## Running the Application

The project consists of 2 main components running in parallel: Agent Server and Client App (FastAPI). `main.py` manages both processes.

```bash
python main.py
```

*   **Client App** will run at: `http://localhost:8000`
*   **Agent Server** will run at: `http://localhost:8001`

## Project Structure

*   `chat_agent/`: Contains logic for the main Chat Agent.
*   `app/`: Source code for API Server (FastAPI endpoints, router).
*   `core/`: Shared modules (tools, utils).
*   `main.py`: Entry point to launch the system.

## Contributing

All contributions are welcome! Please create a Pull Request or open an Issue for discussion.
