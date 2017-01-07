import socket
import json
from generic_listener import GenericListener
from threading import Thread
from broker import Broker
from request_creator import RequestType

class Worker(Thread):
	def __init__(self, socket, address, broker):
		Thread.__init__(self)
		self.sock = socket
		self.addr = address
		self.broker = broker
		self.start()

	def run(self):
		data = json.loads(self.sock.recv(1024).decode())
		if data['type'] == RequestType.publish_data.value:
			self.broker.register(data['payload'])
			self.sock.send(b'Key will be published.')
		elif data['type'] == RequestType.request_data.value:
			data = self.broker.fetch(data['payload'])
			self.sock.send(json.dumps(data).encode())

class KeyListener(GenericListener):

	def __init__(self, port, broker):
		super().__init__(port)
		self.broker = broker

	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, address, self.broker)
		finally:
			self.serversocket.close()
