#!/usr/bin/env python
from connection import *
import logging as lg, sys, json, socket
from multiprocessing import Event 

def terminate_server_gracefully(config, ev=Event()):
	ev.set()
	client = connection(config['client']['ip'], config['client']['port'], ev)
	shouldLoop = True
	while shouldLoop:
		#timeour first for allowing VLCcontroller to terminate all scripts and processes
		time.sleep(5)
		try:
			#client = connection(config['client']['ip'], config['client']['port'], ev)
			client.connect(config['server']['ip'], config['server']['port'])
		except socket.error:
			lg.info('caught bad file descriptor exception')
			shouldLoop=False
	client.close()


if __name__ == '__main__':
	if sys.argv[2:]:
		shouldRun = Event()
		shouldRun.set()
		with open(sys.argv[1], 'r') as cf: config = json.loads(cf.read())['vlc_client']
		client = connection(config['client']['ip'], config['client']['port'], shouldRun)
		client.connect(config['server']['ip'], config['server']['port'])
		lg.basicConfig(level=lg.INFO)
		msg = {'message':sys.argv[2].strip()}
		lg.info(msg)
		time.sleep(1)
		client.send(msg)
		client.close()
		if msg.get('message')=='terminate':
			terminate_server_gracefully(config)
		'''
		while True:
			try:
				client.send(msg)
			except KeyboardInterrupt:
				shouldRun.clear()
				lg.info('ending')
				break
		'''