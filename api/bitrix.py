import requests
import time
from django.conf import settings

BITRIX_URL = settings.BITRIX_URL

class Bitrix:
	def __init__(self) -> None:
		self.url = 'https://{url}'.format(url=BITRIX_URL)
		self.res_type = "json"
	
	def call(self, method: str, params: dict = None):
		endpoint = "{url}/{method}.{res_type}".format(url=self.url, method=method, res_type=self.res_type)

		time.sleep(0.8)
		if params:
			response = requests.post(endpoint, json=params)
		else:
			response = requests.post(endpoint)

		if response.status_code == 200:
			return response.json()
		raise NotImplementedError(response.text)