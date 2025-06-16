from datetime import datetime, timedelta
import requests
import json

#https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/19/query?where=SOURCE%3D1+AND+MODDATE+%3E%3D+DATE+%271900-01-01%27+AND+MODDATE+%3C%3D+DATE+%272050-12-31%27&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=OBJECTID%2C+PPI%2C+SOURCE%2C+MODDATE%2C+MODTYPE%2C+METHOD%2C+OPERATOR&returnGeometry=false&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=MODDATE&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=pjson

# WORKING QUERY!!!
# SOURCE=1 AND MODDATE >= DATE '2024-01-01' AND MODDATE <= DATE '2025-12-31'

import requests
import json
from datetime import datetime, timedelta
import urllib.parse

def query_by_minutes(minutes):
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=minutes)
    
    # Format dates as YYYY-MM-DD for ArcGIS DATE 'YYYY-MM-DD' syntax
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"Start date: {start_date_str}")
    print(f"End date: {end_date_str}")
    
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
    data = response.json()
    
    # Save response to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"parcel_query_{timestamp}.json"
    
    data_json = json.dump(data, f, indent=2)
    
    # Check for errors in response
    if 'error' in data:
        print(f"Error: {data['error']}")
    else:
        print(f"Query successful, retrieved {len(data.get('features', []))} records")

    print(data_json)

# Example: Query for the last 43,800 minutes (~30 days)
query_by_minutes(43800)

def query_by_ppi(query_result):
    ppi_values = [feature['attributes']['PPI'] for feature in query_result['features']]

    for ppi in ppi_values:
        print(ppi)
