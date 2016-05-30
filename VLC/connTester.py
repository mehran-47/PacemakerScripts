#!/usr/bin/env python
from connection import *
import logging as lg
if __name__ == '__main__':
	client = connection('192.168.189.129', 5555)
	client.connect('192.168.189.129', 6666)
	lg.basicConfig(leve=lg.DEBUG)
	while True:
		try:
			client.send({'message':raw_input('send message > ')})
		except KeyboardInterrupt:
			lg.info('ending')
			break
	