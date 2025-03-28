"""
csv_export.py: Contains functions to export the search results and metadata to an Excel file with two tabs.
"""

import os
import pandas as pd
from datetime import datetime


def check_filename(filename):
    """
    Check if the filename is valid.
    - Filename should not be empty.
    - Filename should not contain slashes.
    - Filename should end with .xlsx
    - If no extension is provided, append .xlsx.
    - If no folder path is provided, use "data" as the default folder.
    - Ensure the output folder exists.
    - If filename does not contain folder path, prepend it.
    - Return the full path of the filename.
    """
    if not filename:
        raise ValueError("Filename cannot be empty.")

    if "/" in filename or "\\" in filename:
        raise ValueError("Filename should not contain slashes.")

    if not filename.endswith(".xlsx"):
        filename += ".xlsx"

    if not os.path.splitext(filename)[1]:
        filename += ".xlsx"

    if not os.path.exists("data"):
        os.makedirs("data")

    if not filename.startswith("data"):
        filename = os.path.join("data", filename)

    return filename


def export_to_excel(articles, min_year, max_year, research_purpose, mesh_strategy, filename="output.xlsx"):
    """
    Export search results and metadata to an Excel file with two sheets.
    Sheet1: Search Results
    Sheet2: Metadata
    """
    # Create DataFrame for search results
    results_data = []
    for article in articles:
        results_data.append({
            "RefID": article.get("RefID", ""),
            "PMID": article.get("PMID", ""),
            "Title": article.get("Title", ""),
            "Authors": article.get("Authors", ""),
            "Abstract": article.get("Abstract", ""),
            "DOI": article.get("DOI", ""),
            "Link": article.get("Link", "")
        })
    df_results = pd.DataFrame(results_data)

    # Create DataFrame for metadata
    metadata_data = {
        "min_year": [min_year],
        "max_year": [max_year],
        "research_purpose": [research_purpose],
        "mesh_strategy": [mesh_strategy],
        "export_date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    }
    df_metadata = pd.DataFrame(metadata_data)

    # Check the filename
    filename = check_filename(filename)

    # Export to Excel with two sheets
    with pd.ExcelWriter(filename) as writer:
        df_results.to_excel(writer, sheet_name="Search Results", index=False)
        df_metadata.to_excel(writer, sheet_name="Metadata", index=False)
