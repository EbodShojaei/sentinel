# Sentinel | Terminal-Based AI Agent for PubMed Search

This application is a terminal-based AI agent that:

- Accepts a natural language search query from the user.
- Uses a local phi3.5 model (via Ollama and phidata) to generate a research purpose and a detailed MeSH search strategy.
- Executes the search on PubMed using a free API (via Entrez from Biopython).
- Retrieves the top 250 relevant articles, sorted by relevance and publication year.
- Stores the search results and metadata in a relational SQL database.
- Allows the user to export the search results and metadata to an Excel file with two tabs.

## File Structure

```plaintext
sentinel/
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   └── utils/
│       ├── __init__.py
│       ├── xlsx_export.py
│       ├── database.py
│       ├── extract_values.py
│       └── pubmed_search.py
├── tests/
│   ├── __init__.py
│   └── test_pubmed_search.py
├── main.py
├── requirements.txt
└── setup.sh
```

## Requirements

The application uses the following Python packages:

- phidata
- ollama
- sqlalchemy
- requests
- biopython
- openpyxl
- pandas
- python-dotenv

Setup virtual Python environment and install all dependencies with:

```bash
./setup.sh
```

## Configuration

Create a `.env` file (make a copy of `.env.example`) in the project root with your configuration. For example:

```dotenv
# .env file
ENTREZ_EMAIL=your.email@example.com
PUBMED_API_KEY=your_pubmed_api_key
MODEL_ID=phi3.5
```

## Usage

Run the application from the terminal:

```bash
python main.py --query "I want the most relevant retrospective articles for knee osteoarthritis patients treated with placebo between 2000 and 2025" --export
```

- If `--query` is not provided, you will be prompted to enter it interactively.
- Optionally specify `--min_year` and `--max_year` for the publication date range (defaults to the last 5 years).
- The `--export` flag will export the results to an Excel file (`output.xlsx`).

## Example Output

See the below example for running a custom query:

```bash
python main.py
Using PubMed API key for enhanced rate limits.
Enter your search query: efficacy of placebo injections in knee osteoarthritis patients
2025-03-28 19:18:15,801 [WARNING] No date range found in the query. Using default values.
2025-03-28 19:18:22,224 [INFO] HTTP Request: POST http://127.0.0.1:11434/api/chat "HTTP/1.1 200 OK"
2025-03-28 19:18:22,591 [INFO] HTTP Request: POST https://api.phidata.com/v1/telemetry/agent/run/create "HTTP/1.1 200 OK"
2025-03-28 19:18:35,854 [INFO] HTTP Request: POST http://127.0.0.1:11434/api/chat "HTTP/1.1 200 OK"
2025-03-28 19:18:36,203 [INFO] HTTP Request: POST https://api.phidata.com/v1/telemetry/agent/run/create "HTTP/1.1 200 OK"
2025-03-28 19:18:36,204 [INFO] To determine the impact of placebo injections on symptom relief and quality of life improvement for patients with knee osteoarthritis.
2025-03-28 19:18:56,448 [INFO] HTTP Request: POST http://127.0.0.1:11434/api/chat "HTTP/1.1 200 OK"
2025-03-28 19:18:56,791 [INFO] HTTP Request: POST https://api.phidata.com/v1/telemetry/agent/run/create "HTTP/1.1 200 OK"
2025-03-28 19:19:07,519 [INFO] HTTP Request: POST http://127.0.0.1:11434/api/chat "HTTP/1.1 200 OK"
2025-03-28 19:19:07,862 [INFO] HTTP Request: POST https://api.phidata.com/v1/telemetry/agent/run/create "HTTP/1.1 200 OK"
2025-03-28 19:19:07,864 [INFO] (knee osteoarthritis OR arthritis knees) AND (placebo injection NOT actual medication) AND symptom relief OR quality of life improvement
2025-03-28 19:19:07,864 [INFO] Executing PubMed search...
Final query for PubMed: (knee osteoarthritis OR arthritis knees) AND (placebo injection NOT actual medication) AND symptom relief OR quality of life improvement AND "2020/01/01"[dp] : "2025/12/31"[dp]
Found 250 PubMed IDs
2025-03-28 19:19:17,112 [INFO] Retrieved 250 search results
2025-03-28 19:19:17,170 [INFO] Data stored successfully in the database.
```

## License

This project is released under the MIT License.
