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
		for chunk in r.iter_content(chunk_size=128):
			fd.write(chunk)
			
	return (id, file_name)
