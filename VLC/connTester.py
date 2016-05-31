#!/usr/bin/env python
from connection import *
import logging as lg, sys
from multiprocessing import Event 

def terminate_server_gracefully(ip, port, ev=Event()):
	time.sleep(5)
	ev.set()
	try:
		client = connection('192.168.189.129', 5555, ev)
		client.connect(ip, port)
	except socket.error:
		lg.info('caught bad file descriptor exception')
		client.close()


if __name__ == '__main__':
	if sys.argv[1:]:
		shouldRun = Event()
		shouldRun.set()
		client = connection('192.168.189.129', 5555, shouldRun)
		client.connect('192.168.189.129', 6666)
		lg.basicConfig(level=lg.DEBUG)
		msg = {'message':sys.argv[1].strip()}
		lg.info(msg)
		time.sleep(1)
		client.send(msg)
		client.close()
		if msg.get('message')=='terminate':
			terminate_server_gracefully('192.168.189.129', 6666)
		'''
		while True:
			try:
				client.send(msg)				
			except KeyboardInterrupt:
				shouldRun.clear()
				lg.info('ending')
				break
		'''