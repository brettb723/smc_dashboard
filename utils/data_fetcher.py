import requests
import json
import os



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

if __name__ == "__main__":
    data = fetch_appfolio_report("work_order")
    print(json.dumps(data, indent=4))
    if data and isinstance(data, list) and data[0]:
        columns = list(data[0].keys())
        print(columns)
