import socket
import json
from generic_listener import GenericListener
from request_creator import RequestType
from mix import MixNode
from threading import Thread
from petlib.ec import EcPt
from binascii import unhexlify
from epspvt_utils import getGlobalSphinxParams
from logger import *
from socket_utils import recv_timeout
from request_creator import RequestCreator
from network_sender import NetworkSender

class Worker(Thread):
	def __init__(self, socket, mixnode, mix_port=8081):
		Thread.__init__(self)
		self.sock = socket
		self.mixnode = mixnode
		self.mix_port = mix_port
		self.network_sender = NetworkSender()
		self.start()

	def run(self):
		def reconstruct_header(h_0, h_1, h_2):
			h_0 = unhexlify(h_0)
			params = getGlobalSphinxParams()
			group = params.group.G
			ecPt = EcPt.from_binary(h_0, group)
			return (ecPt, unhexlify(h_1), unhexlify(h_2))

		raw_data = recv_timeout(self.sock, timeout=1)
		data = json.loads(raw_data)
		if data['type'] == RequestType.push_to_mix.value:
			data = data['payload']
			header = reconstruct_header(data['header_0'], data['header_1'], data['header_2'])
			delta = unhexlify(data['delta'])
			log_debug(header)
			print(header)
			log_debug(delta)
			result = self.mixnode.process(header, delta)
			if result[1] is None:
				json_data, dest = RequestCreator().post_msg_to_mix(
					{'ip': result[0], 'port': self.mix_port},
					{'header': header, 'delta': delta}
				)
				self.network_sender.send_data(json_data, dest)


class MixNodeListener(GenericListener):
	def __init__(self, port, mixnode):
		super().__init__(port)
		self.mixnode = mixnode
	
	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, self.mixnode, self.port)
		finally:
			self.serversocket.close()