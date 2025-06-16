from datetime import datetime, timedelta
import requests
import json

def query_by_minutes(minutes):

    end_date = datetime.now()
    end_unix = int(end_date.timestamp())

    # Parameters
    start_date = end_date - timedelta(minutes=minutes)
    start_unix = int(start_date.timestamp())

    print(f"Start date: {start_date}")
    print(f"End date: {end_date}\n")

    print(f"Start Unix: {start_unix}")
    print(f"End unix: {end_unix}")

    url = f"https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/19/query?where=SOURCE%3D1&text=&objectIds=&time={start_unix}%2C+{end_unix}&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=OBJECTID%2C+PPI%2C+SOURCE%2C+MODDATE%2C+MODTYPE%2C+METHOD%2C+OPERATOR&returnGeometry=false&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=MODDATE&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=pjson"

    response = requests.get(url)
    data = response.json()
    
    # Save to JSON file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"parcel_query_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Data saved to {filename}")

query_by_minutes(1)