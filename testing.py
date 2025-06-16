from datetime import datetime, timedelta
import requests
import json
import urllib.parse

def convert_timestamp_to_datetime_obj(timestamp, as_string=False):
    """Convert Unix timestamp (in milliseconds) to datetime object or string"""
    if timestamp == 'N/A' or timestamp is None:
        return 'N/A' if as_string else datetime.min
    try:
        timestamp_seconds = int(timestamp) / 1000
        dt = datetime.fromtimestamp(timestamp_seconds)
        return dt.strftime('%Y-%m-%d %H:%M:%S') if as_string else dt
    except (ValueError, TypeError, OSError):
        return 'Invalid Date' if as_string else datetime.min

# Example WHERE clause:
# # SOURCE=1 AND MODDATE >= DATE '2025-01-01' AND MODDATE <= DATE '2025-12-31'

# Calculate date range
minutes = 525600
end_date = datetime.now()
start_date = end_date - timedelta(minutes=minutes)

# Format dates as YYYY-MM-DD for ArcGIS DATE 'YYYY-MM-DD' syntax
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Construct WHERE clause with DATE keyword
where_clause = f"SOURCE=1 AND MODDATE >= DATE '{start_date_str}' AND MODDATE <= DATE '{end_date_str}'"

# URL-encode the WHERE clause
encoded_where = urllib.parse.quote(where_clause)

# Build the full query URL
url = (
    "https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/19/query?"
    f"where={encoded_where}&"
    "text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&"
    "geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&"
    "distance=&units=esriSRUnit_Foot&relationParam=&"
    "outFields=OBJECTID%2C+PPI%2C+SOURCE%2C+MODDATE%2C+MODTYPE%2C+METHOD%2C+OPERATOR&"
    "returnGeometry=false&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&"
    "outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&"
    "orderByFields=MODDATE&groupByFieldsForStatistics=&outStatistics=&"
    "returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&"
    "resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&"
    "datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&"
    "featureEncoding=esriDefault&f=pjson"
)

# Send request
response = requests.get(url)
layer_19_json_data = response.json()

# Save layer_19_json_data as JSON file
layer_19_filename = f"layer_19_data_{start_date_str}_to_{end_date_str}.json"
try:
    with open(layer_19_filename, 'w', encoding='utf-8') as f:
        json.dump(layer_19_json_data, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved layer 19 data to {layer_19_filename}")
except Exception as e:
    print(f"Error saving layer 19 JSON file: {e}")

# Find PPI Values and create PPI to MODDATE mapping
if layer_19_json_data and 'features' in layer_19_json_data:
    ppi_values = [feature['attributes']['PPI'] for feature in layer_19_json_data['features']]
    
    # Create mapping from PPI to MODDATE for later assignment
    ppi_to_moddate = {
        feature['attributes']['PPI']: feature['attributes']['MODDATE'] 
        for feature in layer_19_json_data['features']
    }
    
    # Convert timestamps to readable dates in the mapping
    ppi_to_moddate_readable = {
        ppi: convert_timestamp_to_datetime_obj(timestamp, as_string=True)
        for ppi, timestamp in ppi_to_moddate.items()
    }
    
    print(f"\nRetrieved {len(ppi_values)} PPI values from {start_date} to {end_date}\n")

    # Construct the WHERE clause with IN operator
    if ppi_values:
        # Format PPI values as a comma-separated string with single quotes
        ppi_list = ",".join(f"'{ppi}'" for ppi in ppi_values)
        where_clause = f"PPI IN ({ppi_list})"
        encoded_where_clause = urllib.parse.quote(where_clause)

        # Base URL for the query with specified outFields and f=pjson
        base_url = (
            "https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/12/query"
            "?text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps"
            "&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects"
            "&distance=&units=esriSRUnit_Foot&relationParam="
            "&outFields=PPI,Schedule,Filing,Phase,ShortDesc,HouseNum,FullStreet,StreetName,TownName,PostCode,FullAdd,TotAcres,SquareFeet,SqeFtLiving,BsmtType,GarageType,NumOfCars,GarSqFt,NumOfRms,NumBedRms,NumLofts,NumKitch,MasterBath,FullBath,TotBath"
            "&returnGeometry=false&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR="
            "&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields="
            "&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false"
            "&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset="
            "&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation="
            "¶meterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=pjson"
        )

        # Construct the full URL with the encoded WHERE clause
        url = f"{base_url}&where={encoded_where_clause}"
        #print(f"Query URL: {url}")

        # Optionally, make the HTTP request to fetch results
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            layer_12_json_data = response.json()

            #print(layer_12_json_data)

            # Extract schedule values and property attributes with MODDATE assignment
            schedule_values = [feature['attributes']['Schedule'] for feature in layer_12_json_data['features']]
            property_attributes = [feature['attributes'] for feature in layer_12_json_data['features']]
            
            print(f"Retrieved {len(schedule_values)} Schedules from {start_date} to {end_date}\n")

            report_data = []
            for schedule, attributes in zip(schedule_values, property_attributes):
                url = f'https://gis.summitcountyco.gov/map/DetailData.aspx?Schno={schedule}'
                address = attributes.get('FullAdd', 'N/A')
                living_sqft = attributes.get('SqeFtLiving', 'N/A')
                acres = attributes.get('TotAcres', 'N/A')
                ppi = attributes.get('PPI')
                
                # Assign MODDATE from layer 19 if PPI matches
                moddate_readable = ppi_to_moddate_readable.get(ppi, 'N/A')
                
                # Add readable MODDATE to the full attributes
                attributes_with_moddate = attributes.copy()
                attributes_with_moddate['MODDATE'] = moddate_readable
                
                report_data.append({
                    'url': url,
                    'schedule': schedule,
                    'address': address,
                    'living_sqft': living_sqft,
                    'acres': acres,
                    'full_attributes': attributes_with_moddate
                })

            # Sort report_data by MODDATE (most recent first)
            report_data.sort(
                key=lambda x: convert_timestamp_to_datetime_obj(
                    ppi_to_moddate.get(x['full_attributes'].get('PPI'))
                ),
                reverse=True
            )

            # Save report_data as JSON
            output_filename = f"layer_12_data_{start_date_str}_to_{end_date_str}.json"

            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                print(f"Successfully saved {len(report_data)} records to {output_filename} (sorted by most recent MODDATE)\n")
                
                # Print summary of MODDATE assignments
                matched_count = sum(1 for item in report_data if item['full_attributes'].get('MODDATE') != 'N/A')
                print(f"MODDATE assigned to {matched_count} out of {len(report_data)} records")
                
            except Exception as e:
                print(f"Error saving JSON file: {e}")

        except requests.RequestException as e:
            print(f"Error querying URL: {e}")
    else:
        print("No PPI values found to query.")
else:
    print("No features found in query results.")