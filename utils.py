import os
import json
from datetime import datetime, timedelta

def sort_layer_19_data(): 
    if os.path.exists('layer_19_data.json'):
        with open('layer_19_data.json', 'r') as f:
            data = json.load(f)
            sorted_data = sorted(data, key=lambda x: x['attributes']['MODDATE'], reverse=True)

            for item in sorted_data:
                moddate_timestamp = item['attributes']['MODDATE']
                # Convert timestamp to readable date
                readable_date = datetime.fromtimestamp(moddate_timestamp / 1000).strftime('%Y-%m-%d')
                ppi = item['attributes']['PPI']
                print(f"PPI: {ppi} | MODDATE: {readable_date} ({moddate_timestamp})")
    else:
        print("Error: layer_19_data.json file not found.")

def check_past_year_ppis(years_back=1):
    
    # Get today's date at midnight
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate the cutoff date (years_back years ago from today)
    cutoff_date = today_start - timedelta(days=years_back * 365)
    cutoff_timestamp = cutoff_date.timestamp() * 1000  # Convert to milliseconds
    
    # Filter entries from the specified time period
    recent_entries = [entry for entry in sorted_data 
                     if entry['attributes']['MODDATE'] >= cutoff_timestamp]
    
    time_period = f"past {years_back} year{'s' if years_back != 1 else ''}"
    print(f"Found {len(recent_entries)} PPIs modified in the {time_period}:")
    
    for entry in recent_entries:
        ppi = entry['attributes']['PPI']
        moddate_timestamp = entry['attributes']['MODDATE']
        readable_date = datetime.fromtimestamp(moddate_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"PPI: {ppi} | Modified: {readable_date}")
    
    return recent_entries