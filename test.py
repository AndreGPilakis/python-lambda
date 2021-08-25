import requests
import json

### Inputs from CFN
vpcName = 'Joes-test-app-prod'
accountNumber = '797117344656'
blocksize = 22





#Combined name for requesting
tag = vpcName + "-" + accountNumber 
#Infoblock space to pull from
space = 'Test'
#Infoblox API token (secret)
infoBloxToken = '161e2056f694d7ea0489da1428a22e6c0d04643afbf8b4f47fdf1c887ad4c47a'
headers = {'content-type': 'application/json','AUTHORIZATION': f'TOKEN {infoBloxToken}'}

print(f'Checking with Infobox for {tag}...')

# Check to see if an block has already been assigned
params = { '_tfilter' : f'appName={tag}'}
response = requests.get('https://csp.infoblox.com/api/ddi/v1/ipam/subnet', headers=headers, params=params)


if len(json.loads(response.text)['results']) != 0:
	print(f'a CIDR block has already been assigned for tag {tag}')
	assigned = json.loads(response.text)['results'][0]['address']
else:
	print(f'CIDR block for {tag} not found, requesting a new one:')


	#pull the IP Space
	params =  {'_filter': f'name=="{space}"'}
	response = requests.get('https://csp.infoblox.com/api/ddi/v1/ipam/ip_space', headers=headers, params=params)
	ipSpace = json.loads(response.text)['results'][0]['id']

	print(f' - Got IP Space: {ipSpace}')



	#pull address block
	params = {'_filter': f'space=="{ipSpace}"'}
	response = requests.get('https://csp.infoblox.com/api/ddi/v1/ipam/address_block', headers=headers, params=params)
	addressBlock = json.loads(response.text)['results'][0]['id']

	print(f' - Got address block: {addressBlock}')
	
	
	#Find next avaliable CIDR
	params = {'cidr': blocksize}
	response = requests.get(f'https://csp.infoblox.com/api/ddi/v1/{addressBlock}/nextavailablesubnet', headers=headers, params=params)
	freeBlock = json.loads(response.text)['results'][0]['address']

	print(f' - Got free block: {freeBlock}')

	
	#Request allocation
	data = {'address': freeBlock,'comment': f'{tag} (Auto Assigned)','cidr': blocksize,'tags' : {'appName' : tag},'space' : ipSpace}
	response = requests.post('https://csp.infoblox.com/api/ddi/v1/ipam/subnet', headers=headers, json=data)
	assigned = json.loads(response.text)['result']['address']
	
	print(' - CIDR successfully allocated')

print()
print('CIDR:')
print(assigned)