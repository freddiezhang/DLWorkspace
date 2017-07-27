from .event_sender import EventSender
import sys
import requests

tenant_token = "7a725db988304a09bdf4e794cda40b17-cc48d478-d728-461e-97da-8f7cbb171054-7230"
e = EventSender()
e.send(tenant_token)
sys.exit("Does This Work")