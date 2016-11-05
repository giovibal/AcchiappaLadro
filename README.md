# AcchiappaLadro

> This is a series of scripts to detect intrusion with a Raspberry PI 2, a PIR and a NoIR Cam

## Instalation

1. Link or copy "init.d/acchiappa-ladro" into /etc/init.d/ folder
    
        cd /home/pi/AcchiappaLadro/
        ln -s init.d/acchiappa-ladro /etc/init.d/acchiappa-ladro
    
2. Configure gdrive

    to configure gdrive you must execute it once manually, 
    approve auth token, and set it into the app interactively
    
    Execute this command
    
        cd /home/pi/AcchiappaLadro
        /home/pi/AcchiappaLadro/gdrive/gdrive -c /home/pi/AcchiappaLadro/gdrive/conf upload -p 0B5VaZPNYmmfca0dnMDdFLXppNTA -f /home/pi/AcchiappaLadro/README.md
         
    N.B. gdrive (https://github.com/prasmussen/gdrive) is not included, 
    you must download and configure by yourself