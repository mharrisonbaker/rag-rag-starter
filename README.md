# Plain Language Checker

This project is a web-based tool to help users write in plain language, using the Federal Plain Language Guidelines. It analyzes text for common issues like long sentences, passive voice, and jargon, and provides suggestions for improvement based on a Retrieval-Augmented Generation (RAG) system.

## Features

-   **Web-Based Editor:** A simple and intuitive web interface to paste or upload text for analysis.
-   **Plain Language Analysis:** Detects common writing issues, including:
    -   Long and complex sentences.
    -   Passive voice.
    -   Vague or undescriptive link text.
    -   Jargon and complex words.
-   **RAG-Powered Suggestions:** Uses a Retrieval-Augmented Generation (RAG) system to provide relevant excerpts from the Federal Plain Language Guidelines to help you improve your text.
-   **OpenAI-Powered Analysis:** The backend uses the OpenAI API to analyze your text and provide suggestions.

## Architecture

The application consists of two main components:

-   **Frontend:** A React application built with Vite that provides the user interface. (in `apps/plain-check-web`)
-   **Backend:** A Python-based API using FastAPI that performs the text analysis and RAG-based retrieval. (in `services/api`)

The backend uses a pre-indexed version of the Federal Plain Language Guidelines with vector embeddings for fast and accurate semantic search.

## Getting Started

### Prerequisites

-   Python 3.9+
-   Node.js and npm

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mharrisonbaker/rag-rag-starter.git
    cd rag-rag-starter
    ```

2.  **Set up the Python environment:**
    -   Create and activate a virtual environment:
        ```bash
        python -m venv plainlanguageenv
        source plainlanguageenv/bin/activate  # On Windows use `plainlanguageenv\Scripts\activate`
        ```
    -   Install Python dependencies:
        ```bash
        pip install -r services/ingest/requirements.txt
        pip install -r services/api/requirements.txt
        ```

3.  **Set up the Frontend:**
    -   Install Node.js dependencies:
        ```bash
        npm install --prefix apps/plain-check-web
        ```

4.  **Generate the Guideline Index:**
    -   The application uses a JSON index of the Federal Plain Language Guidelines. To generate the index with embeddings, run the following script from the project root:
        ```bash
        python scripts/generate_embeddings.py --input apps/plain-check-web/public/data/index.json --output apps/plain-check-web/public/data/guidelines.with_embeddings.json
        ```

### Running the Application

You need to run the backend and frontend servers in two separate terminals.

1.  **Start the Backend API Server:**
    -   In one terminal, from the project root, run:
        ```bash
        python -m uvicorn rag_rag_starter.services.api.main:app --reload --port 8000
        ```

2.  **Start the Frontend Web Application:**
    -   In a second terminal, from the project root, run:
        ```bash
        npm run dev --prefix apps/plain-check-web
        ```

3.  **Open the application:**
    -   Open your web browser and navigate to `http://localhost:5173` (or the address shown in the terminal).

## Usage

1.  Open the web application in your browser.
2.  Paste your text into the editor, or use the "Upload" button to load a `.txt` file.
3.  As you type, the tool will analyze your text and display findings and suggestions in the right-hand panel.


# Credits
## Authored by
### Matthew H. Baker