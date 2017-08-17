from .event_sender import EventSender
import sys
import requests

tenant_token = "801fc846cce2482cb80e2781803dd9b9-92c9560f-1f47-4696-9390-b687ad77cc4f-7392"
e = EventSender()
e.send(tenant_token)
sys.exit("Does This Work")