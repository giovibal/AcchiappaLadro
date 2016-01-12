This is a series of scripts to detect intrusion with a PIR and a NoIR Cam

put this in /etc/rc.local 

/usr/bin/python3 /home/pi/AcchiappaLadro/VideoOnPir2.py > /var/log/VideoOnPir2.log 2>&1 &

