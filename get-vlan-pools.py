#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

import json
import requests

# static APIC credentials for debugging purpose
APIC_IP_Addr = "10.60.9.225"
APIC_login = "admin"
APIC_mdp = "cisco123"

# Or user input for APIC credentials
#APIC_IP_Addr =  raw_input("IP address of APIC ? ")
#APIC_login =  raw_input("APIC login ? ")
#APIC_mdp =  raw_input(APIC_login + " password ? ")

# create credentials structure
credentials = {'aaaUser': {'attributes': {'name': APIC_login, 'pwd': APIC_mdp}}}

# login to APIC
base_url = 'http://' + APIC_IP_Addr + '/api/'
login_url = base_url + 'aaaLogin.json'
login_session = requests.post(login_url, data=json.dumps(credentials))

if login_session.status_code == 200:
	print ("\nOk, you're logged in APIC " + APIC_IP_Addr + " with account <" + APIC_login + ">")

	# get token from login response structure
	auth = json.loads(login_session.text)
	auth_token = auth['imdata'][0]['aaaLogin']['attributes']['token']
	#print ("token = " + auth_token)

	# create cookie array from token
	cookies = {}
	cookies['APIC-Cookie'] = auth_token
	#print cookies

	# get the liste of vlan pools from the APIC API
	url = base_url + 'class/fvnsEncapBlk.json?'
	response = requests.get(url, cookies=cookies, verify=False)
	#print "reponse URL demandee:"
	#print response.json()

	# get the number of pools configured
	response_size = len(response.json()['imdata'])

	vlan_pool_list = []

	print "\nList of VLAN and VXLAN pools :\n"
	for i in range(0,response_size):
		# get the string that contains the vlan/vxlan pools data in the returned json
		# and split the string based on '-' char separator to create a list
		line_split = response.json()["imdata"][i]["fvnsEncapBlk"]["attributes"]["dn"].split('-')
		print ("pool string #" + str(i) + ': ' + str(line_split))

		if str(line_split[0]) == "uni/infra/vlanns":
			# get the name of the pool and remove extra chars
			pool_name = line_split[1][1:-1]
			pool_type = line_split[2][:-5]
			print ("   " + pool_name + " is a " + pool_type + " vlan pool")

			# get the vlan range and remove extra chars
			vlan_range = [int(line_split[4][:-1]),int(line_split[7][:-1])]
			#print vlan_range

			# populate the vlan pool list
			vlan_pool_list.append((vlan_range,pool_name))
		else:
			pool_name = line_split[1]
			print ("   " + pool_name + " is a vxlan pool")

	# sort vlan pool list
	vlan_pool_list.sort()

	print "\n Sorted VLAN range list used on " + APIC_IP_Addr + " :\n"
	for i in range(0,len(vlan_pool_list)):
		print ("   " + str(vlan_pool_list[i][0][0]) + " -> " + str(vlan_pool_list[i][0][1]) + " : " + str(vlan_pool_list[i][1]))

else:
	print ("Login error : return code HTTP = " + str(login_session.status_code))

