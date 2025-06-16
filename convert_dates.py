import json
from datetime import datetime, timezone

def convert_moddate_to_date(input_file, output_file=None, date_format="%Y-%m-%d"):
    """
    Convert MODDATE (milliseconds since Unix epoch) to a readable date in a JSON file.
    
    Args:
        input_file (str): Path to input JSON file.
        output_file (str, optional): Path to save output JSON file. If None, prints results.
        date_format (str): Format for the output date (default: YYYY-MM-DD).
    """
    # Read the JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process each feature
    for feature in data.get('features', []):
        moddate_ms = feature['attributes'].get('MODDATE')
        if moddate_ms is not None:
            # Convert milliseconds to seconds and create datetime (UTC)
            moddate_sec = moddate_ms / 1000
            moddate_dt = datetime.fromtimestamp(moddate_sec, tz=timezone.utc)
            # Format as string
            feature['attributes']['MODDATE'] = moddate_dt.strftime(date_format)
    
    # Output results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Converted data saved to {output_file}")
    else:
        # Print for inspection
        for feature in data['features']:
            print(f"PPI: {feature['attributes']['PPI']}, MODDATE: {feature['attributes']['MODDATE']}")
    
    return data

# Example usage
input_json = "parcel_query_20250616_144902.json"
output_json = "parcel_query_converted_20250616_144902.json"

# Convert MODDATE to YYYY-MM-DD and save to new file
convert_moddate_to_date(input_json, output_json)

# Optional: Convert with time component (uncomment to use)
# convert_moddate_to_date(input_json, output_json, date_format="%Y-%m-%d %H:%M:%S")