"""
main.py: Entry point for the terminal-based AI agent that retrieves PubMed articles based on a user query.
"""

import sys
from src.menu import Menu

def main():
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Process interrupted by user.")
