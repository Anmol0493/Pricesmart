from helper_class import *

class CWEBSHARE():

	def __init__(self):
		self.API_KEY = '10txdgbnplegpsdmphzbe1ehvxqm7ma7vrqvlxfm'
		self.helper = Helper()
		self.proxy_list_file = ''


	def authenticate(self):
		response = requests.get("https://proxy.webshare.io/api/", headers={"Authorization": f"Token {self.API_KEY}"})
		if response.status_code == 200:
			return True
		else:
			return False

	def get_user_profile_info(self):
		response = requests.get("https://proxy.webshare.io/api/profile/", headers={"Authorization": f"Token {self.API_KEY}"})
		if response.status_code == 200:
			print(json.dumps(response.json(),indent=4))
			return response.json()
		else:
			return False

	def get_subscription_info(self):
		response = requests.get("https://proxy.webshare.io/api/subscription/", headers={"Authorization": f"Token {self.API_KEY}"})
		if response.status_code == 200:
			print(json.dumps(response.json(),indent=4))
			return response.json()
		else:
			return False

	def get_proxy_configuration_info(self):
		response = requests.get("https://proxy.webshare.io/api/proxy/config/", headers={"Authorization": f"Token {self.API_KEY}"})
		if response.status_code == 200:
			print(json.dumps(response.json(),indent=4))
			return response.json()
		else:
			return False

	def get_proxy_list(self,proxy_filename):
		self.proxy_list_file = proxy_filename

		page_num = 1
		total_count = 0
		proxies_data = {}
		proxies_data['date'] = str(self.helper.get_time_stamp()).split()[0]
		proxies_list = []
		while 1:
			url = f"https://proxy.webshare.io/api/proxy/list/?page={page_num}"
			
			# print ("Current URL: ", url," : Page Number: ", page_num)

			response = requests.get(url, headers={"Authorization": f"Token {self.API_KEY}"})
			if response.status_code == 200:
				response = response.json()
				total_count = response['count']
				proxies_list.extend(response['results'])

				# print(total_count," : ",len(response['results'])," : ",len(proxies_list))

				if len(proxies_list) >= total_count:
					break
				else:
					page_num += 1
			else:
				return False
		
		proxies_data['proxies'] = proxies_list
		self.helper.write_json_file(proxies_data,self.proxy_list_file)
		return self.proxy_list_file

	def get_proxy_stats(self):
		response = requests.get("https://proxy.webshare.io/api/proxy/stats/", headers={"Authorization": f"Token {self.API_KEY}"})
		if response.status_code == 200:
			print(json.dumps(response.json(),indent=4))
			return response.json()
		else:
			return False


if __name__ == "__main__":
	handle = CWEBSHARE()
	#handle.authenticate()
	#handle.get_user_profile_info()
	handle.get_subscription_info()
	#handle.get_proxy_configuration_info()
	handle.get_proxy_list('data.json')
	handle.get_proxy_stats()