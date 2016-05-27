#!/usr/bin/env python
from pexpect import spawn, pxssh
from threading import Thread
import sys, os

class vlcRemoteColtroller():
	def __init__(self, path_to_video, ip, port, seek=0.0):
		if os.path.exists(path_to_video):
			child = spawn('bash', timeout=None)
			child.sendline('vlc -vvv '+ sys.argv[1] + ' --sout \'#rtp{sdp=rtsp://' + ip + ':' + port + '/rtest}\' --loop --ttl 1 -I rc')
			child.sendline()



if __name__ == '__main__':
	if sys.argv[1:]:
		vc = vlcRemoteColtroller(sys.argv, '192.168.31.1', '8080', 0.0)