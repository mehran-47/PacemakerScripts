*show current configuration
crm configure show 

*configure http service
crm configure primitive HTTP_Service ocf:heartbeat:apache params configfile=/etc/apache2/apache2.conf op monitor interval="30s" op start timeout="40s" op stop timeout="60s"

*show corosync members
corosync-cmapctl | grep members 

*start/stop resource
crm resource start <resource name>
crm resource stop <resource name>

*show configuration
crm configure show

*one shot monitoring
crm status

*Time synchronization
	1. in /etc/ntp.conf: add
		server	tick.encs.concordia.ca  #132.205.96.93
		server	tock.encs.concordia.ca	#132.205.96.94
	2. ptpd server:  
		ptpd -c -G -b eth0 -h -D  #master, verbose mode, synchronized with ntp
		ptpd -c -G -b eth0		  #non verbose mode
	3. ptpd slaves:
		ptpd -c -g -b eth0 -h -D  #slave, verbose mode	