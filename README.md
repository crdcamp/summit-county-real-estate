# Overview

This project utilizes the ArcGIS database for the [Summit County Colorado Property Information Search Map](https://experience.arcgis.com/experience/706a6886322445479abadb904db00bc0) to scan for recently modified documents. The results are then sent via email to update a user for newly modified real estate documents.

Results are queried using a URL structure that accesses [Layer 12](https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/12) (the "Schedule" layer) and [Layer 19](https://gis.summitcountyco.gov/arcgis/rest/services/ParcelQueryTool/SummitMap1_Pro321/MapServer/19) (the "Parcel" layer) of the Summit County ArcGIS database. The results are then cross referenced using the PPI identification numbers from Layer 19 to find recently modified documents found in Layer 12.

When cross referencing using the PPI numbers is complete (assuming there are any new updates), the results are sent in a pleasantly structured HTML email format. The update emails provide links and general information for the given parcel.

## Requirements

Run `pip install -r requirements.txt` in your terminal to install dependencies.

## Usage

All you need is a sender email, receiver email, and an email API password. My specific instance uses the Google API to accomplish this. After setting up the .env file using `example.env` as a reference, simply run `real_estate_updates.py` to query the database.

The default query time is set to 30 minutes. However, you can adjust this value using the `minutes` variable in `real_estate_updates.py`. Moreover, `real_estate_queries.ipynb` gives examples for altering the code to query for either hours or days.