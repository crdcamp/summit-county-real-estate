from datetime import datetime, timedelta
import requests
import urllib.parse
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

def format_value(value, no_commas=False):
    """Format values for display, handling None, empty, and special values"""
    if value is None or value == '' or value == 'N/A':
        return '<span style="color: #999; font-style: italic;">N/A</span>'
    if isinstance(value, (int, float)) and value == -1:
        return '<span style="color: #999; font-style: italic;">Not Available</span>'
    if isinstance(value, float):
        if no_commas:
            return f"{value:.2f}" if value < 1 else f"{value:.0f}"
        return f"{value:,.2f}" if value >= 1 else f"{value:.2f}"
    if isinstance(value, int):
        if no_commas:
            return str(value)
        return f"{value:,}"
    return str(value)

def create_html_email(report_data, start_date, end_date):
    """Create HTML formatted email from report data"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 5px 0;
                font-size: 16px;
                opacity: 0.9;
            }}

            .property-card {{
                background: white;
                margin-bottom: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .property-header {{
                background: #404040;
                color: white;
                padding: 20px;
            }}
            .property-header h3 {{
                margin: 0 0 10px 0;
                font-size: 20px;
            }}
            .property-header .address {{
                font-size: 16px;
                opacity: 0.9;
            }}
            .property-header .schedule {{
                font-size: 14px;
                opacity: 0.8;
                margin-top: 5px;
            }}
            .property-details {{
                padding: 25px;
            }}
            .details-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }}
            .detail-section {{
                background: #f8f8f8;
                padding: 15px;
                border-radius: 8px;
                border-left: 3px solid #666;
            }}
            .detail-section h4 {{
                margin: 0 0 15px 0;
                color: #333;
                font-size: 16px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 8px;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                padding: 5px 0;
            }}
            .detail-row:nth-child(even) {{
                background: rgba(0, 0, 0, 0.05);
                margin-left: -10px;
                margin-right: -10px;
                padding-left: 10px;
                padding-right: 10px;
                border-radius: 4px;
            }}
            .detail-label {{
                font-weight: 600;
                color: #555;
                flex: 1;
            }}
            .detail-value {{
                flex: 1;
                text-align: right;
                color: #333;
            }}
            .view-link {{
                display: inline-block;
                background: #333;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
                font-weight: 600;
            }}
            .view-link:hover {{
                background: #555;
            }}
            .footer {{
                background: #1a1a1a;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Summit County Property Data Report</h1>
            <p>Property modifications from {start_date.strftime('%B %d, %Y')}</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    """
    
    # Add each property
    for i, property_data in enumerate(report_data, 1):
        attrs = property_data.get('full_attributes', {})
        
        html += f"""
        <div class="property-card">
            <div class="property-header">
                <h3>Property #{i}</h3>
                <div class="address">{format_value(property_data.get('address', 'N/A'))}</div>
                <div class="schedule">Schedule: {format_value(property_data.get('schedule', 'N/A'), no_commas=True)}</div>
            </div>
            
            <div class="property-details">
                <div class="details-grid">
                    <!-- Basic Information -->
                    <div class="detail-section">
                        <h4>📊 Basic Information</h4>
                        <div class="detail-row">
                            <span class="detail-label">PPI:</span>
                            <span class="detail-value">{format_value(attrs.get('PPI'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Schedule:</span>
                            <span class="detail-value">{format_value(attrs.get('Schedule'), no_commas=True)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Filing:</span>
                            <span class="detail-value">{format_value(attrs.get('Filing'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Phase:</span>
                            <span class="detail-value">{format_value(attrs.get('Phase'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Description:</span>
                            <span class="detail-value">{format_value(attrs.get('ShortDesc'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Last Modified:</span>
                            <span class="detail-value">{format_value(attrs.get('MODDATE'))}</span>
                        </div>
                    </div>
                    
                    <!-- Address Information -->
                    <div class="detail-section">
                        <h4>📍 Address Information</h4>
                        <div class="detail-row">
                            <span class="detail-label">House Number:</span>
                            <span class="detail-value">{format_value(attrs.get('HouseNum'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Full Street:</span>
                            <span class="detail-value">{format_value(attrs.get('FullStreet'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Street Name:</span>
                            <span class="detail-value">{format_value(attrs.get('StreetName'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Town:</span>
                            <span class="detail-value">{format_value(attrs.get('TownName'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Postal Code:</span>
                            <span class="detail-value">{format_value(attrs.get('PostCode'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Full Address:</span>
                            <span class="detail-value">{format_value(attrs.get('FullAdd'))}</span>
                        </div>
                    </div>
                    
                    <!-- Property Size -->
                    <div class="detail-section">
                        <h4>📐 Property Size</h4>
                        <div class="detail-row">
                            <span class="detail-label">Total Acres:</span>
                            <span class="detail-value">{format_value(attrs.get('TotAcres'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Total Square Feet:</span>
                            <span class="detail-value">{format_value(attrs.get('SquareFeet'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Living Square Feet:</span>
                            <span class="detail-value">{format_value(attrs.get('SqeFtLiving'))}</span>
                        </div>
                    </div>
                    
                    <!-- Building Details -->
                    <div class="detail-section">
                        <h4>🏠 Building Details</h4>
                        <div class="detail-row">
                            <span class="detail-label">Basement Type:</span>
                            <span class="detail-value">{format_value(attrs.get('BsmtType'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Garage Type:</span>
                            <span class="detail-value">{format_value(attrs.get('GarageType'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Number of Cars:</span>
                            <span class="detail-value">{format_value(attrs.get('NumOfCars'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Garage Sq Ft:</span>
                            <span class="detail-value">{format_value(attrs.get('GarSqFt'))}</span>
                        </div>
                    </div>
                    
                    <!-- Room Information -->
                    <div class="detail-section">
                        <h4>🛏️ Room Information</h4>
                        <div class="detail-row">
                            <span class="detail-label">Number of Rooms:</span>
                            <span class="detail-value">{format_value(attrs.get('NumOfRms'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bedrooms:</span>
                            <span class="detail-value">{format_value(attrs.get('NumBedRms'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Lofts:</span>
                            <span class="detail-value">{format_value(attrs.get('NumLofts'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Kitchens:</span>
                            <span class="detail-value">{format_value(attrs.get('NumKitch'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Master Bathrooms:</span>
                            <span class="detail-value">{format_value(attrs.get('MasterBath'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Full Bathrooms:</span>
                            <span class="detail-value">{format_value(attrs.get('FullBath'))}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Total Bathrooms:</span>
                            <span class="detail-value">{format_value(attrs.get('TotBath'))}</span>
                        </div>
                    </div>
                </div>
                
                <a href="{property_data.get('url', '#')}" class="view-link" target="_blank">
                    View Full Details on County Website →
                </a>
            </div>
        </div>
        """
    
    html += """
        <div class="footer">
            <p>Summit County Property Data Email Report</p>
            <p>This report contains the most recent property modifications in Summit County, Colorado</p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_html_email(report_data, start_date, end_date):
    """Send HTML formatted email with property data"""
    
    # Load environment variables
    load_dotenv()
    
    # Email configuration
    sender_email = 'crdcamp@gmail.com'
    receiver_email = 'crdcamp@gmail.com' #'Johnvano@sweethomesinc.com'
    password = os.getenv('EMAIL_PASSWORD')
    
    if not password:
        print("ERROR: EMAIL_PASSWORD environment variable not found!")
        return False
    
    # Create HTML content
    html_content = create_html_email(report_data, start_date, end_date)
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Summit County Property Report - {len(report_data)} Properties Modified'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    # Create HTML part
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    try:
        # Send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        print(f"✅ Email sent successfully with {len(report_data)} properties!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

# Main execution code
def main():
    # Calculate date range
    minutes = 56000
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

    print(f"🔍 Querying properties modified from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Send request
    response = requests.get(url)
    layer_19_json_data = response.json()

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
        
        print(f"📊 Retrieved {len(ppi_values)} PPI values from layer 19")

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

            # Make the HTTP request to fetch results
            try:
                response = requests.get(url)
                response.raise_for_status()
                layer_12_json_data = response.json()

                # Extract schedule values and property attributes with MODDATE assignment
                schedule_values = [feature['attributes']['Schedule'] for feature in layer_12_json_data['features']]
                property_attributes = [feature['attributes'] for feature in layer_12_json_data['features']]
                
                print(f"🏠 Retrieved {len(schedule_values)} property records from layer 12")

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

                print(f"✅ Successfully processed {len(report_data)} records (sorted by most recent MODDATE)")
                
                # Print summary of MODDATE assignments
                matched_count = sum(1 for item in report_data if item['full_attributes'].get('MODDATE') != 'N/A')
                print(f"📅 MODDATE assigned to {matched_count} out of {len(report_data)} records")

                # Send HTML email
                if report_data:
                    print("📧 Sending HTML email...")
                    send_html_email(report_data, start_date, end_date)
                else:
                    print("❌ No data to send in email")

            except requests.RequestException as e:
                print(f"❌ Error querying layer 12: {e}")
        else:
            print("❌ No PPI values found to query layer 12")
    else:
        print("❌ No features found in layer 19 query results")

if __name__ == "__main__":
    main()