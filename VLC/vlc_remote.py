#!/usr/bin/env python
from pexpect import spawn
from threading import Thread
import sys, os, logging as lg, time

class vlcRemoteColtroller():
	def __init__(self):		
		self.handle = spawn('bash', timeout=None)
		self.check_new_commands = True
		self.commandstack = []
		#self.commands_map = {'play': self.__play, 'stop': self.__stop, 'resume': self.__resume}
		self.interval = 2
		self.commands_executer = Thread(target=self.command_executer, args=(self.interval,))
		self.commands_receiver = Thread(target=self.command_receiver)
		lg.basicConfig(level=lg.INFO)
		self.commands_receiver.start()
		#self.command_executer.start()

	def instantiate(self, path_to_video, ip, port, play=False):
		if os.path.exists(path_to_video):
			lg.debug('command to play video:')
			self.handle.sendline('vlc -vvv '+ sys.argv[1] + ' --sout \'#rtp{sdp=rtsp://' + ip + ':' + port + '/rtest}\' --loop --ttl 1 -I rc')
			if not play: self.handle.sendline('stop')
			lg.info('vlc -vvv '+ sys.argv[1] + ' --sout \'#rtp{sdp=rtsp://' + ip + ':' + port + '/rtest}\' --loop --ttl 1 -I rc')
			try:
				for line in self.handle: lg.debug(line)
			except KeyboardInterrupt:
				lg.info('Stopping vlc')			
		else:
			lg.error('Invalid path to video: %s' %(path_to_video))
	
	def command_executer(self, interval=5):
		while self.check_new_commands:
			if self.commandstack[:]:
				for one_set_of_commands in self.commandstack:
					if one_set_of_commands[0] in self.commands_map:
						self.commands_map[one_set_of_commands[0]](one_set_of_commands)
					else:
						lg.error('Invalid commands passed\n %r' %(one_set_of_commands))
			time.sleep(interval)
		lg.info('Stopping live command input')

	def command_receiver(self):
		self.commandstack.append([elem for elem in raw_input('> ').split(',') if elem])

if __name__ == '__main__':
	if sys.argv[1:]:
		vc = vlcRemoteColtroller()
		vc.instantiate(sys.argv[1], '192.168.189.200', '8080', True)
		Thread(target=printStack, args=(vc.commandstack, )).start()
