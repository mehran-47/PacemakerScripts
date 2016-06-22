##TODO: write a more elaborate version
#For stateful vlc resource:
	1. configure config.json
	2. Add the following lines in /etc/init.d/pacemaker
		2.1 at the top:
			VLC_REC_DIR=<directory where the scrips reside>
		2.2 in start():
				$VLC_REC_DIR/VLCcontroller.py $VLC_REC_DIR/config.json &
				echo 'run' > /tmp/pcmk.glue
				$VLC_REC_DIR/pacemakerGlue.py $VLC_REC_DIR/config.json &
		2.3 in stop:
				rm -f /tmp/pcmk.glue