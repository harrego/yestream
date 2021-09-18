import requests
from bs4 import BeautifulSoup
import twitter
import re

def twitter_setup(consumer_key, consumer_secret, access_token_key, access_token_secret):
	try:
		twitter_api = twitter.Api(
			consumer_key=consumer_key,
			consumer_secret=consumer_secret,
			access_token_key=access_token_key,
			access_token_secret=access_token_secret)
		if twitter_api.VerifyCredentials():
			return twitter_api
		else:
			return None
	except Exception as error:
		return None

def site_metadata(url):
	headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" }
	r = requests.get(url, headers=headers)
	
	soup = BeautifulSoup(r.text, features="html.parser")
	head_title = soup.find("title")
	meta_title = soup.find("meta", property="og:title")
	meta_description = soup.find("meta", property="og:description")
	
	title = meta_title["content"] if meta_title else None
	if title == None:
		title = head_title.string if head_title else None
	description = meta_description["content"] if meta_description else None
	
	return (title, description)
	
def tweet_metadata(twitter_api, tweet_id):
	status = twitter_api.GetStatus(tweet_id)
	return status
	
def tweet_ids_from_str(string):
	ids = []
	for url_match in re.finditer(r'(https?:\/\/)?(www.)?twitter.com\/\w+\/status\/[0-9]+', string):
		# re.search is for anywhere in the string
		(url_start, url_end) = url_match.span()
		match_str = url_match.string[url_start:url_end]
		id_match = re.search(r'[0-9]+$', match_str)
		if id_match == None:
			return None
		(start, end) = id_match.span()
		tweet_id = id_match.string[start:end]
		ids.append(int(tweet_id))
	return ids
	
