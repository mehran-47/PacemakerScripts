#!/usr/bin/env python
import pexpect, logging as lg, time
from threading import Thread, Event as ThreadEvent
from multiprocessing import Event as ProcessEvent
from subprocess import Popen, PIPE
from shlex import split

class pacemakerGlue():
	def __init__(self, procShouldRun, interval=1):
		self.handle = pexpect.spawn('bash', timeout=None)
		self.procShouldRun = procShouldRun
		self.interval = interval
		self.hostname = Popen(split('hostname -s'), stdout=PIPE).communicate()[0].strip()
		lg.debug(self.hostname)

	def check_status(self):
		while self.procShouldRun.is_set():
			x = Popen(split('crm status'), stdout=PIPE)
			output = [aLine for aLine in x.communicate()[0].split('\n') if 'VLC_vidstream' in aLine]
			if not output[0:]:
				lg.debug('should terminate')
			elif output[-1].rsplit(' ')[-1].strip() == self.hostname: 
				lg.debug('should set active')			
			else:
				lg.debug('hostname:\n%r\noutput:\n%r' %(self.hostname, output[-1].rsplit(' ')[-1].strip()))
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