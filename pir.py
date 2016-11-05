import pir
import configparser


config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('config.ini')

pir_id = config['device']['pir_id']
mqtt_host = config['mqtt']['mqtt_host']
mqtt_topic = config['mqtt']['mqtt_topic']

print("initializing pir ... ")
presence = pir.Pir(pir_id=pir_id
                   , mqtt_host=mqtt_host
                   , mqtt_topic=mqtt_topic)

print("initializing pir ... ")
presence.start()
