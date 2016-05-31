#!/usr/bin/env python
from connection import *
import logging as lg
from multiprocessing import Event 
if __name__ == '__main__':
	shouldRun = Event()
	shouldRun.set()
	client = connection('192.168.189.129', 5555, shouldRun)
	client.connect('192.168.189.129', 6666)
	lg.basicConfig(leve=lg.DEBUG)
	while True:
		try:
			client.send({'message':raw_input('send message > ')})
		except KeyboardInterrupt:
			shouldRun.clear()
			lg.info('ending')
			break
	