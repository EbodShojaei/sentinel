"""
main.py: Entry point for the terminal-based AI agent that retrieves PubMed articles based on a user query.
"""

import argparse
import logging
import sys
from src.utils.extract_values import extract_years_from_query, extract_query_from_markdown
from src.agent import generate_research_purpose, generate_mesh_strategy
from src.utils.pubmed_search import run_pubmed_search
from src.utils.database import init_db, store_metadata, store_search_results, get_engine_session
from src.utils.xlsx_export import export_to_excel
from src.config import DEFAULT_DATE_RANGE

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI agent for PubMed searches")
    parser.add_argument("--query", type=str, help="User query for the search", required=False)
    parser.add_argument("--min_year", type=int, help="Minimum publication year", required=False)
    parser.add_argument("--max_year", type=int, help="Maximum publication year", required=False)
    parser.add_argument("--export", action="store_true", help="Export results to Excel file")
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Get user query either from argument or prompt
    if args.query:
        user_query = args.query
    else:
        user_query = input("Enter your search query: ")

    # logging.info("Processing query: %s", user_query)

    # Extract date range from query if not provided
    if not args.min_year and not args.max_year:
        extracted_years = extract_years_from_query(user_query)
        if extracted_years:
            min_year, max_year, user_query = extracted_years
            logging.info("Extracted date range from query: %d to %d", min_year, max_year)
        else:
            max_year = DEFAULT_DATE_RANGE["MAX_YEAR"]
            min_year = DEFAULT_DATE_RANGE["MIN_YEAR"]
            logging.warning("No date range found in the query. Using default values: %d to %d", min_year, max_year)
    else:
        min_year = args.min_year
        max_year = args.max_year

    # Generate research purpose using local phi3.5
    user_query.strip()
    research_purpose_raw = generate_research_purpose(user_query)
    research_purpose = extract_query_from_markdown(research_purpose_raw)
    logging.info(research_purpose)

    # Generate MeSH search strategy using local phi3.5
    mesh_strategy_raw = generate_mesh_strategy(user_query, research_purpose)
    mesh_strategy = extract_query_from_markdown(mesh_strategy_raw)
    logging.info(mesh_strategy)

    # Execute PubMed search
    logging.info("Executing PubMed search...")
    search_results = run_pubmed_search(mesh_strategy, min_year, max_year)
    logging.info("Retrieved %d search results", len(search_results))

    # Initialize database and store results
    engine = init_db()
    session = get_engine_session(engine)
    try:
        metadata_id = store_metadata(session, min_year, max_year,
                       research_purpose, mesh_strategy)
        store_search_results(session, search_results, metadata_id)
        session.commit()
        logging.info("Data stored successfully in the database.")
    except Exception as e:
        session.rollback()
        logging.error("Error storing data: %s", str(e))
    finally:
        session.close()

    # Export to Excel if requested
    if args.export:
        try:
            export_to_excel(session, metadata_id)
            logging.info("Data exported successfully to output.xlsx")
        except Exception as e:
            logging.error("Error exporting data: %s", str(e))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Process interrupted by user.")
