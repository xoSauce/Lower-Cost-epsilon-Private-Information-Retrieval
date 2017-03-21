import requests
from sphinxmix.SphinxParams import SphinxParams

class Debug():
	dbg = False

class ProtocolNumber():
	PROTOCOL_BYTE_NUMBER = 15

class SecurityParameters():
	NUMBER_OF_REQUESTS = 6 # p in the paper
	REQUESTS_IN_THE_POOL = 3

def getGlobalSphinxParams():
	return SphinxParams(header_len = 500, body_len=2048)

def getPublicIp():

	if Debug.dbg:
		return '0.0.0.0'

	_RESPONSE_RETURNED = 200
	link = "http://api.ipify.org?format=json"
	resp = requests.get(link)
	if resp.status_code != _RESPONSE_RETURNED:
		raise Exception("Cannot reach " + link + "to retrieve public ip address")
	return resp.json()["ip"]
