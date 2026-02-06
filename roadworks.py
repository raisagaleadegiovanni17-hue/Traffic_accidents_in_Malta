"""
Module for checking roadworks data in Malta.

This module loads roadworks data from a JSON file and provides functionality to check if there were roadworks
on a specific street at a given time.

The roadworks data comes from the Government of Malta's Geohub "Full Road Closure" dataset, downloaded using:

curl 'https://utility.arcgis.com/usrsvcs/servers/102a9e17511b43f2be2b73baaeac61b9/rest/services/main_road_works_NoEdits/FeatureServer/0/query?f=json&cacheHint=true&maxRecordCountFactor=4&resultOffset=0&resultRecordCount=8000&where=1%3D1&orderByFields=OBJECTID%20ASC&outFields=*&outSR=102100&returnGeometry=false&spatialRel=esriSpatialRelIntersects' \
  -H 'origin: https://geogovmt.maps.arcgis.com' \
  -H 'referer: https://geogovmt.maps.arcgis.com/apps/dashboards/a72d1afaa58d4f5cb8e5d9a04817df54' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' 

This URL was obtained by inspecting the network requests made by the Geohub dashboard at:

https://geogovmt.maps.arcgis.com/apps/dashboards/a72d1afaa58d4f5cb8e5d9a04817df54

"""

import json, re, pandas

from datetime import datetime

STREET_FIX = re.compile(r'\b(triq|street|vjal|avenue|road)\b', re.IGNORECASE)

# A kind of normalisation table for Maltese characters.
MT_TABLE = str.maketrans('ĊĠĦŻ', 'CGHZ')

closures = []

def parse_roadworks_data(attr: dict) -> dict:
	"""
	Parse a roadworks data entry from the JSON file.

	Parameters:
	entry (object): A single roadworks entry from the JSON data.

	Returns:
	dict: A dictionary containing parsed roadworks information.
	"""
	return {
		'locality_name': attr['rw_LocalityName'].upper().translate(MT_TABLE),

		# Normalise street names by removing spaces after articles like "TRIQ IS- SULTAN" and ensuring uppercase.
		'street_name': re.sub(r'([LRSTXZ])- ', r'\1-', attr['rw_StreetFullname'], flags=re.IGNORECASE).upper().translate(MT_TABLE),
		'from_date': datetime.fromisoformat(attr['rw_DateFrom']),
		'to_date': datetime.fromisoformat(attr['rw_DateTo']),
		'id': attr['rw_id']
	}

def had_roadworks(locality: str, street: str, time_stamp: datetime) -> bool:
	"""
	Check if there were roadworks in a specific street at a given time.
	
	The check is insensitive to Maltese characters and capitalisation.

	Matching is inclusive, for example "Mosta" and "Triq l-Gharusa" as arguments would match a record with "il-Mosta" and "Triq l-Għarusa tal-Mosta".

	Parameters:
	locality (str): The locality in which the corresponding street must be located.
	street (str): The street to check for roadworks.
	time_stamp (datetime): The date and time to check.

	Returns:
	bool: True if there were roadworks in the specified street at the given time, False otherwise.
	"""

	# Normalise locality and street names for comparison.
	street, locality = street.upper().translate(MT_TABLE), locality.upper().translate(MT_TABLE)

	# Remove prefix/suffix from street names for broader matching e.g. "Triq Dawret il-Gudja" matches "Dawret il-Gudja".
	street = STREET_FIX.sub('', street).strip()

	# Handle case where time_stamp is a string, for convenience.
	if isinstance(time_stamp, str):
		time_stamp = datetime.fromisoformat(time_stamp)

	# Ensure a potentially naive time_stamp is timezone-aware in Europe/Malta timezone
	# (the timezone of dates from news and police reports).
	if time_stamp.tzinfo is None:
		time_stamp = pandas.to_datetime(time_stamp).tz_localize('Europe/Malta')

	for closure in closures:
		if (locality in closure['locality_name'] and
			street in closure['street_name'] and
			closure['from_date'] <= time_stamp <= closure['to_date']):
			return True

	return False

with open('supplementary-data/full-road-closures.json') as json_data:
	for entry in json.load(json_data)['features']:
		closures.append(parse_roadworks_data(entry['attributes']))
