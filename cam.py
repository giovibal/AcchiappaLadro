import cam
import configparser


config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('config.ini')

pir_id = config['device']['pir_id']
mqtt_host = config['mqtt']['mqtt_host']
mqtt_topic = config['mqtt']['mqtt_topic']
local_tmp_dir = config['gdrive']['local_tmp_dir']
gdriveCMD = config['gdrive']['cmd']


print("initializing cam ... ")
camera = cam.Cam(pir_id=pir_id
                 , mqtt_host=mqtt_host
                 , mqtt_topic=mqtt_topic
                 , local_tmp_dir=local_tmp_dir
                 , gdrive_cmd=gdriveCMD)


waitSeconds = 10
print("starting cam, wait %s sec to acquire internet connection ... " % waitSeconds)
camera.start(delay=waitSeconds)
