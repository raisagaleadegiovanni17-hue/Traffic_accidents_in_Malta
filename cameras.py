"""
Module for checking streets with speed cameras in Malta.

This module loads speed camera data from a CSV file and provides functionality to check if a specific street has a speed camera.

The base speed camera data comes from SCDB: https://www.scdb.info/en/countrycameralist/M/

The data point on the year of installation was obtained from data compiled by Times of Malta (see table with title "Where are Malta's speed cameras installed?"):

https://timesofmalta.com/article/factcheck-speed-cameras-save-lives.1034910

"""

import pandas as pd, string

# A kind of normalisation table for Maltese characters.
MT_TABLE = str.maketrans('ĊĠĦŻċġħż', 'CGHZcghz')

# Table for removing punctuation from street and locality names.
PUNCT_TABLE = str.maketrans('', '', string.punctuation)

def _load_speed_camera_data() -> pd.DataFrame:
	"""
	Load speed camera data from the CSV file.

	Returns:
	pd.DataFrame: A DataFrame containing speed camera data.
	"""
	data = pd.read_csv('supplementary-data/speed-cameras.csv', keep_default_na=False) # Read empty columns as '', not NaN.
	cols = ['street_en', 'street_mt', 'street_common', 'locality']
	data[cols] = data[cols].map(lambda x: x.translate(MT_TABLE).translate(PUNCT_TABLE).upper()) # Normalise street and locality names for comparison.
	return data

data = _load_speed_camera_data()

def speed_cameras(street: str) -> pd.DataFrame:
	"""
	Look up speed cameras on a specific street.

	The lookup is insensitive to Maltese characters, capitalisation and punctuation.

	Parameters:
	street (str): The street name to check.

	Returns:
	bool: True if the street has a speed camera, False otherwise.
	"""
	street = street.translate(MT_TABLE).translate(PUNCT_TABLE).upper() # Normalise street name for comparison.
	street = street.replace(' STREET', '').replace('TRIQ ', '').strip() # Remove common prefixes/suffixes.
	street = street.replace('BY-PASS', 'BYPASS') # Handle common variation.
	return data[data['street_en'].str.contains(street) | data['street_mt'].str.contains(street) | data['street_common'].str.contains(street)]

def had_speed_camera(street: str, year: int) -> bool:
	"""
	Check if a specific street has a speed camera.

	The lookup is insensitive to Maltese characters, capitalisation and punctuation.

	Parameters:
	street (str): The street name to check.
	year (int): The year to check against.

	Returns:
	bool: True if the street has a speed camera, False otherwise.
	"""
	d = speed_cameras(street)
	return not d[d['installation_year'] <= year].empty
