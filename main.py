import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

from utils import sort_layer_19_data, check_past_year_ppis

def query_all_data():
    # Define the base URL for the query endpoint
    url = "https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/19/query"

    # Query parameters
    params = {
        "where": "SOURCE=1",          # Filter for SOURCE=1
        "outFields": "*",            # Retrieve all fields
        "f": "json",                 # Return format as JSON
        "returnGeometry": "false",   # Exclude geometry to reduce payload size (set to "true" if you need it)
        "resultOffset": 0,           # Start at the first record
        "resultRecordCount": 1000    # Number of records per request (adjust based on server limits)
    }

    all_features = []
    while True:
        # Send the GET request
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            break
        
        # Parse the JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response")
            break

        # Check for errors in the response
        if "error" in data:
            print(f"Error from server: {data['error']['message']}")
            break

        # Extract features (records)
        features = data.get("features", [])
        if not features:
            break  # No more records to fetch

        # Append features to the result list
        all_features.extend(features)

        # Update the offset for the next batch
        params["resultOffset"] += params["resultRecordCount"]
        print(f"Fetched {len(all_features)} records so far...")

    return all_features

def main():
    # Fetch all data
    features = query_all_data()
    
    # Print the total number of records retrieved
    print(f"\nTotal records retrieved: {len(features)}")
    
    # Optionally, print a sample of the data (first record)
    if features:
        print("\nSample record:")
        print(json.dumps(features[0], indent=2))
    
    # Optionally, save the data to a JSON file
    with open("layer_19_data.json", "w") as f:
        json.dump(features, f, indent=2)
        print("\nData saved to 'layer_19_data.json'")

if __name__ == "__main__":
    main()