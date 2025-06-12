import json
import os
from datetime import datetime

def sort_layer_19_data(): 
    if os.path.exists('layer_19_data.json'):
        with open('layer_19_data.json', 'r') as f:
            data = json.load(f)

        # Sort by MODDATE
        def parse_date(item):
            date_str = item['attributes']['MODDATE']
            return datetime.strptime(date_str, "%d-%m-%Y %H.%M")

        sorted_data = sorted(data, key=parse_date)

        with open('layer_19_data.json', 'w') as f:
            json.dump(sorted_data, f, indent=2)

    else:
        print('Error: layer_19_data.json not found.')