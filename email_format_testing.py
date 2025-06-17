from datetime import datetime, timedelta
import requests
import urllib.parse
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

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

def format_real_estate_email_report(report_data):
    """
    Formats Summit County real estate data for email communication.
    
    Args:
        report_data: List of dictionaries containing property information
        
    Returns:
        str: Formatted HTML email content
    """
    
    # Email header
    email_content = """
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; line-height: 1.6; }
        .header { background-color: #2c5aa0; color: white; padding: 20px; text-align: center; }
        .summary { background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #2c5aa0; }
        .property { border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }
        .property-header { background-color: #e9ecef; padding: 10px; margin: -15px -15px 10px -15px; border-radius: 5px 5px 0 0; }
        .property-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 10px 0; }
        .detail-item { margin: 5px 0; }
        .label { font-weight: bold; color: #2c5aa0; }
        .footer { margin-top: 30px; padding: 20px; background-color: #f8f9fa; text-align: center; font-size: 12px; color: #666; }
        .url-link { color: #2c5aa0; text-decoration: none; }
        .url-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Summit County Real Estate Report</h1>
        <p>Property Data Summary - Recent Updates</p>
    </div>
"""
    
    # Calculate summary statistics
    total_properties = len(report_data)
    properties_with_homes = sum(1 for prop in report_data if (prop.get('living_sqft', 0) or 0) > 0)
    total_acres = sum(prop.get('acres', 0) or 0 for prop in report_data)
    total_living_sqft = sum(prop.get('living_sqft', 0) or 0 for prop in report_data)
    
    # Group by town
    town_counts = {}
    for prop in report_data:
        town = prop.get('full_attributes', {}).get('TownName', 'Unknown').strip()
        town_counts[town] = town_counts.get(town, 0) + 1
    
    # Summary section
    email_content += f"""
    <div class="summary">
        <h2>Executive Summary</h2>
        <div class="property-grid">
            <div><span class="label">Total Properties:</span> {total_properties:,}</div>
            <div><span class="label">Properties with Structures:</span> {properties_with_homes:,}</div>
            <div><span class="label">Total Acreage:</span> {total_acres:,.2f} acres</div>
            <div><span class="label">Total Living Space:</span> {total_living_sqft:,} sq ft</div>
        </div>
        
        <h3>Properties by Location</h3>
        <ul>
"""
    
    for town, count in sorted(town_counts.items()):
        email_content += f"            <li><strong>{town}:</strong> {count} properties</li>\n"
    
    email_content += """
        </ul>
    </div>
    
    <h2>Property Details</h2>
"""
    
    # Individual property listings
    for i, prop in enumerate(report_data, 1):
        attrs = prop.get('full_attributes', {})
        
        # Format address
        full_address = attrs.get('FullAdd', 'Address Not Available')
        address_parts = full_address.split('|') if full_address != 'N/A' else []
        primary_address = address_parts[0] if address_parts else "Address Not Available"
        
        # Property type determination
        living_sqft = prop.get('living_sqft', 0) or 0
        acres = prop.get('acres', 0) or 0
        
        if living_sqft > 0:
            prop_type = "Residential Property"
        elif acres > 0:
            prop_type = "Vacant Land"
        else:
            prop_type = "Commercial/Other"
            
        # Format property details
        email_content += f"""
    <div class="property">
        <div class="property-header">
            <h3>Property #{i} - Schedule #{prop.get('schedule', 'N/A')}</h3>
            <p><strong>{prop_type}</strong> | {attrs.get('TownName', 'Unknown').strip()}</p>
        </div>
        
        <div class="detail-item">
            <span class="label">Address:</span> {primary_address}
        </div>
        
        <div class="detail-item">
            <span class="label">Details Link:</span> 
            <a href="{prop.get('url', '#')}" class="url-link" target="_blank">View Property Details</a>
        </div>
        
        <div class="property-grid">
"""
        
        # Basic property info
        if acres > 0:
            email_content += f'            <div><span class="label">Land Size:</span> {acres:.2f} acres</div>\n'
        
        if living_sqft > 0:
            email_content += f'            <div><span class="label">Living Space:</span> {living_sqft:,} sq ft</div>\n'
        
        square_feet = attrs.get('SquareFeet', 0) or 0
        if square_feet > 0 and square_feet != living_sqft:
            email_content += f'            <div><span class="label">Total Building:</span> {square_feet:,} sq ft</div>\n'
        
        # Residential details
        bedrooms = attrs.get('NumBedRms', 0) or 0
        if bedrooms > 0:
            email_content += f'            <div><span class="label">Bedrooms:</span> {bedrooms}</div>\n'
        
        bathrooms = attrs.get('TotBath', 0) or 0
        if bathrooms > 0:
            email_content += f'            <div><span class="label">Bathrooms:</span> {bathrooms:.1f}</div>\n'
        
        cars = attrs.get('NumOfCars', 0) or 0
        if cars > 0:
            garage_info = f"{cars} cars"
            garage_type = attrs.get('GarageType', '')
            if garage_type:
                garage_info += f" ({garage_type})"
            email_content += f'            <div><span class="label">Parking:</span> {garage_info}</div>\n'
        
        # Property identifiers
        ppi = attrs.get('PPI', 'N/A')
        email_content += f'            <div><span class="label">PPI:</span> {ppi}</div>\n'
        
        filing = attrs.get('Filing', '0')
        if filing and filing != "0":
            email_content += f'            <div><span class="label">Filing:</span> {filing}</div>\n'
        
        # Last updated
        mod_date = attrs.get('MODDATE', 'N/A')
        if mod_date != 'N/A':
            if isinstance(mod_date, str) and ' ' in mod_date:
                mod_date = mod_date.split()[0]  # Just the date part
            email_content += f'            <div><span class="label">Last Updated:</span> {mod_date}</div>\n'
        
        email_content += """        </div>
        
        <div class="detail-item">
            <span class="label">Description:</span> """ + attrs.get('ShortDesc', 'No description available') + """
        </div>
    </div>
"""
    
    # Footer
    email_content += """
    <div class="footer">
        <p>This report was generated from Summit County GIS data</p>
        <p>Report Date: """ + datetime.now().strftime('%Y-%m-%d %H:%M') + """</p>
        <p>For more information, visit: <a href="https://gis.summitcountyco.gov">Summit County GIS</a></p>
    </div>
</body>
</html>
"""
    
    return email_content

def format_text_email_report(report_data):
    """
    Formats Summit County real estate data for plain text email.
    
    Args:
        report_data: List of dictionaries containing property information
        
    Returns:
        str: Formatted plain text email content
    """
    
    text_content = """
SUMMIT COUNTY REAL ESTATE REPORT
Property Data Summary - Recent Updates
==================================================

"""
    
    # Calculate summary statistics
    total_properties = len(report_data)
    properties_with_homes = sum(1 for prop in report_data if (prop.get('living_sqft', 0) or 0) > 0)
    total_acres = sum(prop.get('acres', 0) or 0 for prop in report_data)
    total_living_sqft = sum(prop.get('living_sqft', 0) or 0 for prop in report_data)
    
    # Group by town
    town_counts = {}
    for prop in report_data:
        town = prop.get('full_attributes', {}).get('TownName', 'Unknown').strip()
        town_counts[town] = town_counts.get(town, 0) + 1
    
    # Summary section
    text_content += f"""EXECUTIVE SUMMARY
--------------------------------------------------
Total Properties:           {total_properties:,}
Properties with Structures: {properties_with_homes:,}
Total Acreage:             {total_acres:,.2f} acres
Total Living Space:        {total_living_sqft:,} sq ft

PROPERTIES BY LOCATION
--------------------------------------------------
"""
    
    for town, count in sorted(town_counts.items()):
        text_content += f"{town:<30} {count:>3} properties\n"
    
    text_content += "\n\nPROPERTY DETAILS\n" + "="*50 + "\n\n"
    
    # Individual property listings
    for i, prop in enumerate(report_data, 1):
        attrs = prop.get('full_attributes', {})
        
        # Format address
        full_address = attrs.get('FullAdd', 'Address Not Available')
        address_parts = full_address.split('|') if full_address != 'N/A' else []
        primary_address = address_parts[0] if address_parts else "Address Not Available"
        
        # Property type determination
        living_sqft = prop.get('living_sqft', 0) or 0
        acres = prop.get('acres', 0) or 0
        
        if living_sqft > 0:
            prop_type = "Residential Property"
        elif acres > 0:
            prop_type = "Vacant Land"
        else:
            prop_type = "Commercial/Other"
        
        text_content += f"PROPERTY #{i} - Schedule #{prop.get('schedule', 'N/A')}\n"
        text_content += f"Type: {prop_type} | Location: {attrs.get('TownName', 'Unknown').strip()}\n"
        text_content += f"Address: {primary_address}\n"
        text_content += f"Details: {prop.get('url', 'N/A')}\n"
        text_content += "-" * 50 + "\n"
        
        if acres > 0:
            text_content += f"Land Size:      {acres:.2f} acres\n"
        
        if living_sqft > 0:
            text_content += f"Living Space:   {living_sqft:,} sq ft\n"
        
        bedrooms = attrs.get('NumBedRms', 0) or 0
        if bedrooms > 0:
            text_content += f"Bedrooms:       {bedrooms}\n"
        
        bathrooms = attrs.get('TotBath', 0) or 0
        if bathrooms > 0:
            text_content += f"Bathrooms:      {bathrooms:.1f}\n"
        
        cars = attrs.get('NumOfCars', 0) or 0
        if cars > 0:
            garage_info = f"{cars} cars"
            garage_type = attrs.get('GarageType', '')
            if garage_type:
                garage_info += f" ({garage_type})"
            text_content += f"Parking:        {garage_info}\n"
        
        text_content += f"PPI:            {attrs.get('PPI', 'N/A')}\n"
        
        mod_date = attrs.get('MODDATE', 'N/A')
        if mod_date != 'N/A' and isinstance(mod_date, str) and ' ' in mod_date:
            mod_date = mod_date.split()[0]
        text_content += f"Last Updated:   {mod_date}\n"
        
        text_content += f"Description:    {attrs.get('ShortDesc', 'No description available')}\n"
        text_content += "\n" + "="*50 + "\n\n"
    
    # Footer
    text_content += f"""
REPORT INFORMATION
--------------------------------------------------
Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M')}
Data Source:  Summit County GIS
Website:      https://gis.summitcountyco.gov

This report contains property information from Summit County, Colorado.
For questions or additional information, please contact the appropriate county office.
"""
    
    return text_content

def send_formatted_email(report_data, receiver_email, sender_email=None, send_html=True):
    """
    Send a formatted real estate report via email
    
    Args:
        report_data: List of property dictionaries
        receiver_email: Email address to send to
        sender_email: Sender email (defaults to receiver_email)
        send_html: Whether to send HTML email (True) or plain text (False)
    """
    
    if sender_email is None:
        sender_email = receiver_email
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Summit County Real Estate Report - {len(report_data)} Properties - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    # Create both HTML and plain text versions
    text_content = format_text_email_report(report_data)
    html_content = format_real_estate_email_report(report_data)
    
    # Attach parts
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    
    msg.attach(part1)
    if send_html:
        msg.attach(part2)
    
    # Send email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, os.getenv('EMAIL_PASSWORD'))
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent successfully to {receiver_email}")
        print(f"📊 Report contains {len(report_data)} properties")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Main execution code
if __name__ == "__main__":
    # Calculate date range
    minutes = 525600  # 1 year
    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=minutes)
    
    # Format dates as YYYY-MM-DD for ArcGIS DATE 'YYYY-MM-DD' syntax
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Construct WHERE clause with DATE keyword
    where_clause = f"SOURCE=1 AND MODDATE >= DATE '{start_date_str}' AND MODDATE <= DATE '{end_date_str}'"
    
    # URL-encode the WHERE clause
    encoded_where = urllib.parse.quote(where_clause)
    
    # Build the full query URL for layer 19
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
    
    print(f"🔍 Querying properties modified between {start_date_str} and {end_date_str}")
    
    # Send request to layer 19
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
        
        print(f"📋 Retrieved {len(ppi_values)} PPI values from layer 19")
    
        # Construct the WHERE clause with IN operator for layer 12
        if ppi_values:
            # Format PPI values as a comma-separated string with single quotes
            ppi_list = ",".join(f"'{ppi}'" for ppi in ppi_values)
            where_clause = f"PPI IN ({ppi_list})"
            encoded_where_clause = urllib.parse.quote(where_clause)
    
            # Base URL for layer 12 query
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
    
            # Make the HTTP request to fetch results from layer 12
            try:
                response = requests.get(url)
                response.raise_for_status()
                layer_12_json_data = response.json()
    
                # Extract schedule values and property attributes with MODDATE assignment
                schedule_values = [feature['attributes']['Schedule'] for feature in layer_12_json_data['features']]
                property_attributes = [feature['attributes'] for feature in layer_12_json_data['features']]
                
                print(f"🏠 Retrieved {len(schedule_values)} properties from layer 12")
    
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
    
                # Send formatted email
                email = 'crdcamp@gmail.com'
                receiver_email = 'Johnvano@sweethomesinc.com'
                
                if report_data:
                    print(f"\n📧 Sending formatted email report...")
                    send_formatted_email(report_data, receiver_email, email, send_html=True)
                else:
                    print("⚠️ No property data found to send in email")
    
            except requests.RequestException as e:
                print(f"❌ Error querying layer 12: {e}")
        else:
            print("⚠️ No PPI values found to query in layer 12")
    else:
        print("⚠️ No features found in layer 19 query results")