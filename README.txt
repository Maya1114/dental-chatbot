# DENTAL CHATBOT
An AI assistant designed for a dental office to answer staff questions 
by querying patient and appointment data stored in Azure CosmosDB. Uses 
OpenAI’s GPT-4o-mini model to convert natural language queries into 
CosmosDB SQL queries and to generate human-friendly responses.

## Features
1. Natural language interface for querying patient and appointment data
2. Intelligent query builder for generating SQL that is compatible with CosmosDB
3. Handles questions about patient details, appointment statuses, and scheduling
4. Provides clear, concise, and professional responses suitable for dental office staff

## Tech Stack
- Python 3.13
- Azure Cosmos
- OpenAI API (gpt-4o-mini)
- Typer CLI

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/dental-chatbot.git
   cd dental-chatbot
   ```
2. Create and activate your venv
    ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```
3. Install dependencies
    ```bash
   pip install -r requirements.txt
   ```
4. Create .env file with your DB and OpenAI keys
    ```bash
    COSMOS_URL = <>
    COSMOS_KEY = <>
    COSMOS_DB = <>
    OPENAI_API_KEY = <>
    ```

## Usage
1. Test the cli for DB and API connections
    ```bash
    python src/cli.py ping #test connections/view DB schema
    ```
2. Use the ask command to ask your questions
    ```bash
    python src/cli.py ask "your question here"
    ```

## Project Structure

- src/cli.py: Command line interface using Typer.
- src/router.py: Handles OpenAI prompt building, query generation, and answer generation.
- src/cosmos_client.py: Azure CosmosDB client, schema loading, and query execution.
- .env: Environment variables (load your own DB and API keys).
- requirements.txt: Project dependencies.

## Notes

- Queries are generated with strict rules to ensure CosmosDB compatibility.
    e.g. No JOINs or unsupported SQL features are used.

- Chatbot uses a detailed prompt engineering approach for reliable SQL generation.

- For any unsupported question, the system will notify the user instead of failing silently.
