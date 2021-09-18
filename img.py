import requests
import os
import uuid
import db
from urllib.parse import urlparse

def save(url):
	id = str(uuid.uuid4()).replace("-", "")
	file_name = os.path.basename(urlparse(url).path)
	save_dir = "static/" + id + "/"
	save_path = save_dir + file_name
	os.makedirs(save_dir)
	
	r = requests.get(url, stream=True)
	with open(save_path, "wb") as fd:
		file_size = 0
		for chunk in r.iter_content(chunk_size=128):
			file_size += len(chunk)
			fd.write(chunk)
			
	return (id, file_name, file_size)
	
# https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string

# bytes_len: Byte length to convert to human readable string.
# dp: Number of decimal places to display, 2 by default.
def human_file_size(bytes_len, dp=1):
	THRESH = 1000
	if abs(bytes_len) < THRESH:
		return str(bytes_len) + " B"
	
	UNITS = ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
	u = -1
	r = 10 ** dp
	
	while True:
		bytes_len /= THRESH
		u += 1
		if not (round(abs(bytes_len) * r) / r >= THRESH and u < len(UNITS) - 1):
			break
	
	bytes_len_dp = round(bytes_len * r) / r
	return str(bytes_len_dp) + " " + UNITS[u]
	