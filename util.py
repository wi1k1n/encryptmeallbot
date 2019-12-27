def inann(dict, key):
	""" Takes dictionary and key and checks if key in dictionary and it is not None """
	return key in dict and not dict[key] is None

def ninann(dict, key):
	""" Takes dictionary and key and checks if key not in dictionary or it is None """
	return not key in dict or dict[key] is None