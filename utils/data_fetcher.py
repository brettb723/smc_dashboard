import requests
import json
import os
import pandas as pd 



def fetch_appfolio_report(report_name, columns=None):
    # Load credentials from the JSON file
    client_id = os.environ.get("APPFOLIO_CLIENT_ID")
    client_secret = os.environ.get("APPFOLIO_CLIENT_SECRET")
    base_url = "standardmgmtco.appfolio.com/api/v1/reports"

    # Construct the URL without the date range
    url = f"https://{client_id}:{client_secret}@{base_url}/{report_name}.json?paginate_results=false&from_date=01/01/2020&to_date=12/30/2025"

    # If columns are provided, add them as query parameters
    if columns:
        columns_str = ",".join(columns)
        url += f"&columns={columns_str}"

    # Make the GET request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        return None

def view_report(report_name):
    """
    Fetches the report with the given name and displays the first five rows as key-value pairs.

    :param report_name: The name of the report to fetch and display.
    """
    data = fetch_appfolio_report(report_name)

    # Check if the data is valid and has the expected structure
    if data and isinstance(data, list) and len(data) > 0:
        # Loop through the first five records and print each as key-value pairs
        for i, record in enumerate(data[:500]):
            print(f"Record {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
            print()  # Add a newline for spacing between records
    else:
        print("No data available or invalid format.")

if __name__ == "__main__":
    data = fetch_appfolio_report("work_order")
    print(json.dumps(data, indent=4))
    if data and isinstance(data, list) and data[0]:
        columns = list(data[0].keys())
        print(columns)
