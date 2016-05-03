If you do not want to change anything in the code:
	1. Create directories for path: /opt/videos
	2. Copy 'playvid', 'vlc_vidstream' and 'vlc_service_config.json' in /opt/videos
	3. Copy the video you want to play as a service in /opt/videos 
	4. Change the values in the 'vlc_service_config.json' file accordingly. Video file name, IP address, etc.
	5. Copy 'vlc_service.sh' as 'vlc' to '/usr/lib/ocf/resource.d/heartbeat' or similar appropriate directory before adding vlc as a service.