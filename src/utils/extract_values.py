"""
extract_values.py: Cleans up interim datums to ensure consistently formatted inputs for agent actions.
"""

import re
from datetime import datetime


def extract_years_from_query(query: str):
    """
    Extract a date range from a query string using a simple pattern that matches:
      Absolute Years: "2000 to 2025", "2000 and 2025", or "2000-2025" or
      Relative Years: "last 3 years", "previous 3 years", or "past 3 years".
    Returns a tuple (min_year, max_year) if found; otherwise, returns None.
    """
    # Check for absolute years
    pattern = r'(\d{4})\s*(?:and|to|[-–])\s*(\d{4})'
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        min_year = int(match.group(1))
        max_year = int(match.group(2))
        cleaned_query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        return min_year, max_year, cleaned_query.strip()

    # Check for relative years
    pattern = r'(?:last|previous|past)\s+(\d+)\s+years?'
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        years = int(match.group(1))
        current_year = datetime.now().year
        min_year = current_year - years
        max_year = current_year
        cleaned_query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        return min_year, max_year, cleaned_query.strip()

    return None


def extract_query_from_markdown(text: str) -> str:
    """
    Extracts and returns the content between the first pair of triple backticks in the given text.
    If no such content is found, returns the original text.
    """
    # Extract content between triple backticks
    pattern = r'```(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        content = match.group(1).strip()
    else:
        content = text.strip()
    

    start_index = content.find('`')
    if start_index != -1:
        content = content[start_index:].strip()
    else:
        content = content.strip()

    # Remove any leading or trailing whitespace
    content = content.strip()

    start_index = content.find('(')
    if start_index != -1:
        content = content[start_index:].strip()
    else:
        content = content.strip()

    return content
