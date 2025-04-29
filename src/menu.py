"""
menu.py: Menu class for the terminal-based AI agent for PubMed article searches.
"""

import argparse
import sys

from src.utils.extract_values import extract_years_from_query, extract_query_from_markdown
from src.agent import generate_research_purpose, generate_mesh_strategy
from src.utils.pubmed_search import run_pubmed_search
from src.utils.database import init_db, store_metadata, store_search_results, get_engine_session
from src.utils.database import retrieve_all_searches
from src.utils.xlsx_export import export_to_excel
from src.config import DEFAULT_DATE_RANGE


class Menu:
    def __init__(self):
        self.engine = init_db()

    def parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="AI agent for PubMed searches")
        parser.add_argument("--query", type=str,
                            help="User query for the search", required=False)
        parser.add_argument("--min_year", type=int,
                            help="Minimum publication year", required=False)
        parser.add_argument("--max_year", type=int,
                            help="Maximum publication year", required=False)
        parser.add_argument("--export", action="store_true",
                            help="Export results to Excel file")
        return parser.parse_args()

    def run_search(self):
        args = self.parse_arguments()

        # Get user query
        if args.query:
            user_query = args.query
        else:
            user_query = input("[Sentinel]: Enter your search query or 'r' to return: ").strip()
            if user_query.lower() == 'r':
                print("[Sentinel]: Returning to menu.")
                return

        # Extract date range
        if not args.min_year and not args.max_year:
            extracted = extract_years_from_query(user_query)
            if extracted:
                min_year, max_year, user_query = extracted
                print(f"Extracted date range: {min_year} to {max_year}")
            else:
                min_year = DEFAULT_DATE_RANGE["MIN_YEAR"]
                max_year = DEFAULT_DATE_RANGE["MAX_YEAR"]
                print(
                    f"No date range found. Using defaults: {min_year} to {max_year}")
        else:
            min_year = args.min_year
            max_year = args.max_year

        # Generate research purpose and MeSH strategy
        research_purpose_raw = generate_research_purpose(user_query)
        research_purpose = extract_query_from_markdown(research_purpose_raw)
        print(f"Research Purpose: {research_purpose}")

        mesh_strategy_raw = generate_mesh_strategy(
            user_query, research_purpose)
        mesh_strategy = extract_query_from_markdown(mesh_strategy_raw)
        print(f"MeSH Search Strategy: {mesh_strategy}")

        # Run PubMed search
        search_results = run_pubmed_search(mesh_strategy, min_year, max_year)
        print(
            f"Retrieved {len(search_results)} results" if search_results else "No results found.")

        # Retry mechanism
        if not search_results:
            self.retry_search(user_query, min_year, max_year)

        # Store in database
        session = get_engine_session(self.engine)
        try:
            metadata_id = store_metadata(
                session, min_year, max_year, research_purpose, mesh_strategy)
            store_search_results(session, search_results, metadata_id)
            session.commit()
            print("Data stored successfully.")
        except Exception as e:
            session.rollback()
            print(f"Database Error: {str(e)}")
        finally:
            session.close()

        # Optional export
        if args.export:
            try:
                session = get_engine_session(self.engine)
                export_to_excel(session, metadata_id)
                print("Data exported to output.xlsx")
            except Exception as e:
                print(f"Export Error: {str(e)}")
            finally:
                session.close()

    def retry_search(self, user_query, min_year, max_year):
        counter = 3
        instruction = "/clear session. Forget everything. You will only follow instructions concisely and correctly.\n\n"
        user_query = f"{instruction} {user_query}"

        while counter > 0:
            print(f"Retrying... Attempts left: {counter}")
            counter -= 1

            try:
                research_purpose_raw = generate_research_purpose(user_query)
                research_purpose = extract_query_from_markdown(
                    research_purpose_raw)
                print(f"Research Purpose: {research_purpose}")

                mesh_strategy_raw = generate_mesh_strategy(
                    user_query, research_purpose)
                mesh_strategy = extract_query_from_markdown(mesh_strategy_raw)
                print(f"MeSH Search Strategy: {mesh_strategy}")

                search_results = run_pubmed_search(
                    mesh_strategy, min_year, max_year)
                if search_results:
                    print(
                        f"Retrieved {len(search_results)} results after retry.")
                    return search_results
            except Exception as e:
                print(f"Retry failed: {str(e)}")

        print("No results found after retries.")
        return []

    def view_history_and_export(self):
        session = get_engine_session(self.engine)
        try:
            history = retrieve_all_searches(session)
            if not history:
                print("No previous searches found.")
                return

            for idx, search in enumerate(history, 1):
                print(
                    f"[{idx}] Research Purpose: {search.research_purpose}, Date Range: {search.min_year}-{search.max_year}")

            choice = input(
                "\n[Sentinel]: Would you like to export any of these? Enter number or 'r' to return: ").strip()
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(history):
                    selected = history[choice - 1]
                    export_to_excel(session, selected.id)
                    print("Exported selected search to output.xlsx")
                else:
                    print("Invalid selection.")
            else:
                print("[Sentinel]: Returning to menu.")

        except Exception as e:
            print(f"Error retrieving history: {str(e)}")
        finally:
            session.close()

    def quit_program(self):
        print("\n[Sentinel]: Goodbye!")
        sys.exit(0)

    def run(self):
        # parse arguments and automatically run search if provided
        args = self.parse_arguments()
        if args.query:
            self.run_search()
            return
        # otherwise, show menu
        print("\n[Sentinel]: Welcome to Sentinel, how can I assist you today?")
        while True:
            print("\nMenu:")
            print("1. Run new PubMed search")
            print("2. View history and export results")
            print("3. Quit")

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.run_search()
            elif choice == "2":
                self.view_history_and_export()
            elif choice == "3":
                self.quit_program()
            else:
                print("Invalid choice. Please try again.")
