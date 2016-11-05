import pir
import cam
import configparser
from multiprocessing import Pool


config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('config.ini')

pir_id = config['device']['pir_id']
mqtt_host = config['mqtt']['mqtt_host']
mqtt_topic = config['mqtt']['mqtt_topic']
local_tmp_dir = config['gdrive']['local_tmp_dir']
gdriveCMD = config['gdrive']['cmd']

print("initializing pir ... ")
presence = pir.Pir(pir_id=pir_id
                   , mqtt_host=mqtt_host
                   , mqtt_topic=mqtt_topic)

print("initializing cam ... ")
camera = cam.Cam(pir_id=pir_id
                 , mqtt_host=mqtt_host
                 , mqtt_topic=mqtt_topic
                 , local_tmp_dir=local_tmp_dir
                 , gdrive_cmd=gdriveCMD)


def start_pir():
    print("initializing pir ... ")
    presence.start()


def start_cam():
    print("initializing pir ... ")
    camera.start()

pool = Pool(processes=2)
pool.apply_async(start_pir)
pool.apply_async(start_cam)

