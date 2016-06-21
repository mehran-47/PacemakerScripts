#!/bin/bash

param=$1
PID_EXISTS=true
CALL_COUNT=0
#export DO_TOKEN=$OCF_RESKEY_do_token
#IP=$OCF_RESKEY_floating_ip
#ID=$(curl -s http://169.254.169.254/metadata/v1/id)
#HAS_FLOATING_IP=`curl -s http://169.254.169.254/metadata/v1/floating_ip/ipv4/active`


#######################################################################
# Initialization:

: ${OCF_FUNCTIONS_DIR=${OCF_ROOT}/lib/heartbeat}
. ${OCF_FUNCTIONS_DIR}/ocf-shellfuncs

#######################################################################



meta_data() {
  cat <<END
<?xml version="1.0"?>
<!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
<resource-agent name="vlcservice" version="0.1">
  <version>0.1</version>
  <longdesc lang="en">
vlc ocf resource agent for streaming a specified video to a specified IP</longdesc>
  <shortdesc lang="en">Stream a video using vlc</shortdesc>
<parameters>
</parameters>
  <actions>
    <action name="start"        timeout="20" />
    <action name="stop"         timeout="20" />
    <action name="monitor"      timeout="10" interval="5" depth="0" />
    <action name="meta-data"    timeout="5" />
  </actions>
</resource-agent>
END
}

isdirectory() {
  if [ -d "$1" ]
  then
    # 0 = true
    return 0 
  else
    # 1 = false
    return 1
  fi
}

vlc_start() {
	python /opt/videos/vlc_vidstream start
	python /opt/videos/vlc_vidstream monitor &
 	return $OCF_SUCCESS
}

vlc_stop() {
	python /opt/videos/vlc_vidstream stop
	#/home/magic/Documents/pacemakerScripts/VLC/VLCcommandDispatcher.py /home/magic/Documents/pacemakerScripts/VLC/vlc_remote_config.json 'pause'
  	return $OCF_SUCCESS
}

vlc_monitor() {
	if [[ $(pidof vlc_monitoring) ]]; then		
		return $OCF_SUCCESS
	else
		python /opt/videos/vlc_vidstream monitor &		
	fi

	if [[ $(pidof vlc_monitoring) ]]; then		
		return $OCF_SUCCESS
	else
		return $OCF_ERR_GENERIC
	fi
	return $OCF_NOT_RUNNING
}

__monitor(){
	CALL_COUNT=cat "/opt/videos/call_count"
	if [ $CALL_COUNT -gt 2 ]; then
		if [ -e "/proc/$(cat /tmp/vlc_service.pid)" ]; then
			echo "/proc/$(cat /tmp/vlc_service.pid)" > /opt/videos/status
			PID_EXISTS=true
		else
			PID_EXISTS=false
		fi
	else
		CALL_COUNT=$(($CALL_COUNT+1))
	fi
	echo $CALL_COUNT > /opt/videos/call_count
}

if [ "start" == "$param" ] ; then
  vlc_start
elif [ "stop" == "$param" ] ; then
  vlc_stop
elif [ "status" == "$param" ] ; then
  python /opt/videos/vlc_vidstream status
elif [ "monitor" == "$param" ] ; then
	vlc_monitor
  #PID=$(cat /tmp/vlc_service.pid);
  : '
  python /opt/videos/vlc_vidstream monitor &
  if $PID_EXISTS; then
    exit 0;
  else
    exit 7;
  fi
  '
elif [ "meta-data" == "$param" ] ; then
  meta_data
  exit 0
else
  echo "no such command $param"
  exit 1;
fi
