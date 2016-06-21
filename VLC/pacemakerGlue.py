#!/usr/bin/env python
import pexpect, logging as lg, time, os
from threading import Thread, Event as ThreadEvent
from multiprocessing import Event as ProcessEvent
from subprocess import Popen, PIPE, call
from shlex import split

class pacemakerGlue():
	def __init__(self, procShouldRun, interval=3):
		self.handle = pexpect.spawn('bash', timeout=None)
		self.procShouldRun = procShouldRun
		self.interval = interval
		self.hostname = Popen(split('hostname -s'), stdout=PIPE).communicate()[0].strip()
		lg.debug(self.hostname)

	def check_status(self):
		if not os.path.isfile('/tmp/vlc.state'): 
			with open('/tmp/vlc.state','w') as f: f.write('standby')
		while self.procShouldRun.is_set():
			x = Popen(split('crm status'), stdout=PIPE)
			output = [aLine for aLine in x.communicate()[0].split('\n') if 'VLC_vidstream' in aLine]
			if not output[0:]:
				lg.debug('pacemakerGlue: terminating')
			elif output[-1].rsplit(' ')[-1].strip() == self.hostname: 
				with open('/tmp/vlc.state','r') as f: state = f.read().strip()
				if state!='active':	
					lg.debug('pacemakerGlue: setting active')			
			else:
				with open('/tmp/vlc.state','r') as f: state = f.read().strip()
				if state!='standby':
					lg.debug('pacemakerGlue: stating standby')
			time.sleep(self.interval)

if __name__ == '__main__':
	lg.basicConfig(level=lg.DEBUG)
	pge = ProcessEvent()
	pge.set()
	pg = pacemakerGlue(pge)
	try:
		pg.check_status()
	except KeyboardInterrupt:
		lg.info('clearing pacemaker status checking')
		pge.clear()