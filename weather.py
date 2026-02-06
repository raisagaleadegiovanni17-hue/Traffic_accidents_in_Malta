from datetime import datetime, timedelta
from meteostat import Stations, Daily, Hourly

stations = None

def get_stations():
	"""
	Retrieve weather stations located in Malta.

	Returns:
	Stations: A Stations object containing the weather stations in Malta.
	"""
	global stations
	if stations is None:
		stations = Stations().region('MT').fetch()
	return stations

def get_daily_weather_data(start_date: datetime, end_date: datetime = None):
	"""
	Fetch daily aggregated weather data from Malta for a given date range.

	Parameters:
	start_date (datetime): The start date in datetime format.
	end_date (datetime): The end date in datetime format.

	Returns:
	DataFrame: A pandas DataFrame containing the weather data aggregated across weather stations.
	"""

	data = Daily(get_stations(), start_date, end_date or start_date)
	# Call data.normalize() if we need gaps in the time series to be filled.
	data.aggregate('1D', True) # Calculate averages/sums across weather stations.
	return data.fetch()

def get_hourly_weather_data(start_time: datetime, end_time: datetime):
	"""
	Fetch hourly aggregated weather data from Malta for a given date and time range.

	Parameters:
	start_date (datetime): The start date in datetime format.
	end_date (datetime): The end date in datetime format.

	Returns:
	DataFrame: A pandas DataFrame containing the weather data aggregated across weather stations.
	"""

	data = Hourly(get_stations(), start_time, end_time)
	data.aggregate('1h', True) # Calculate averages/sums across weather stations.
	return data.fetch()

def rain_on_date(date: datetime) -> bool:
	"""
	Check if it rained on a specific date in Malta.

	Parameters:
	date (datetime): The date to check.

	Returns:
	bool: True if it rained on the specified date, False otherwise.
	"""
	weather_data = get_daily_weather_data(date)
	if not weather_data.empty:
		return weather_data['prcp'].values[0] > 0
	return False

def rain_before(date: datetime, time, hours) -> bool:
	"""
	Check if it rained within a specified number of hours before a given date and time.

	Parameters:
	date (datetime): The date to check.
	time (int): The hour of the day (0-23).
	hours (int): The number of hours to look back.

	Returns:
	bool: True if it rained within the specified hours before the given date and time, False otherwise.
	"""
	end_time = datetime(date.year, date.month, date.day, time)
	weather_data = get_hourly_weather_data(end_time - timedelta(hours=hours), end_time)
	if not weather_data.empty:
		return weather_data['prcp'].sum() > 0
	return False
