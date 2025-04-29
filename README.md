# Sentinel | Terminal-Based AI Agent for PubMed Search

This application is a terminal-based AI agent that:

- Accepts a natural language search query from the user.
- Uses a local phi3.5 model (via Ollama and phidata) to generate a research purpose and a detailed MeSH search strategy.
- Executes the search on PubMed using a free API (via Entrez from Biopython).
- Retrieves the top 250 relevant articles, sorted by relevance and publication year.
- Stores the search results and metadata in a relational SQL database.
- Allows the user to export the search results and metadata to an Excel file with two tabs.

Watch the demo (as of version 1.0.3): [Video](https://youtu.be/MO7oLftEFaY?si=zbub_zpP1GBzms8R)

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
python main.py --query "efficacy of placebo injections in knee osteoarthritis patients between 2000 and 2025" --export
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
No date range found in the query. Using default values: 2020 to 2025
Research Purpose: To investigate the efficacy and impacts of placebo injections on pain management and joint function outcomes among patients diagnosed with knee osteoarthritis undergoing randomized controlled trials.
MeSH Search Strategy: (placebo OR therapeutic injections) AND knee osteoarthritis AND (pain relief OR improved joint function) AND randomized AND control trial
Found 96 PubMed IDs
Retrieved 96 search results
Data stored successfully in the database.
```

With custom non-default date in query:

```bash
python main.py
Using PubMed API key for enhanced rate limits.
Enter your search query: efficacy of placebo injections in knee osteoarthritis patients between 2000 and 2025
Extracted date range from query: 2000 to 2025
Research Purpose: (placebo) versus active interventions in reducing pain and improving joint function for knee osteoarthritis patients undergoing clinical studies.
MeSH Search Strategy: (placebo OR sham treatment) AND knee osteoarthritis patients] AND ([pain reduction OR improved joint function])
Found 250 PubMed IDs
Retrieved 249 search results
Data stored successfully in the database.
```

With wider outcome criteria (wider scope of efficacy outcomes e.g., pain relief):

```bash
python main.py --export
Using PubMed API key for enhanced rate limits.
Enter your search query: efficacy of placebo injections in knee osteoarthritis patients
No date range found in the query. Using default values: 2020 to 2025
Research Purpose: To evaluate the therapeutic effectiveness and potential benefits on patient-reported pain levels in knee osteoarthritis patients receiving placebo injections as compared to a control group not undergoing any intervention or those treated with standard pharmacological therapies.
MeSH Search Strategy: (Pain OR pain) AND ("Knee Osteoarthritis" OR Knees OR arthrosis OR osteophytes) AND Placebo And Effectiveness NOT Drug Or Medication
Found 250 PubMed IDs
Retrieved 250 search results
Data stored successfully in the database.
Data exported successfully to output.xlsx
```

If search fails to return any entries, the ai tries again:

```bash
python main.py --query "efficacy of placebo injections in knee osteoarthritis patients between 2000 and 2025" --export
Using PubMed API key for enhanced rate limits.
Extracted date range from query: 2000 to 2025
Research Purpose: The purpose of this study is to assess whether placebo injections provide therapeutic benefits or improvement in knee function among patients aged between 65-74 suffering from osteoarthritis.
MeSH Search Strategy: (no time zone provided) Reasoning Steps for Boolean Search Query Formulation To assess studies on placebo injections' efficacy, focusing specifically on knee osteoarthritis patients aged between 65 to 74 years old without considering date ranges or using compound terms. The boolean search query constructed should combine relevant keywords related to the intervention (placebo/sham treatment), outcome measures of interest such as 'knee pain' and 'reduced mobility', along with population-specific criteria:
Found 0 PubMed IDs
Retrieved 0 search results
No results found. Retries: 3
Research Purpose: To investigate the impact and effectiveness of placebo injections specifically as pain management or therapeutic intervention for knee osteoarthritis patients, with a focus on treatment outcomes.
MeSH Search Strategy: (osteoarthritis OR joint disease) AND knees AND (pain relief OR analgesic OR therapeutic treatment OR intervention therapy) AND placebo injection
Found 250 PubMed IDs
Retrieved 249 search results after retry.
Data stored successfully in the database.
Data exported successfully to output.xlsx
```

## License

This project is released under the MIT License.
