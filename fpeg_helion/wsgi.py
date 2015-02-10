
import bottle
from bottle import route, post, get, request, response, template

import logging
import requests
from PIL import Image
from uuid import uuid1

from StringIO import StringIO
from io import BytesIO
from binascii import b2a_base64
import json
import os

logging.basicConfig()
log = logging.getLogger("fpeg")
log.setLevel(logging.DEBUG)

STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')

# image cache
CACHE = {}

@route('/static/:filename')
def serve_static(filename):
  log.debug("serving static assets")
  return bottle.static_file(filename, root=STATIC_ROOT)

@route('/')
def home():
  bottle.TEMPLATE_PATH.insert(0, './views')
  return bottle.template('home', sent=False, body=None)



@post('/compress')
def compress():
  data = request.files.get("upload")
  if data and data.file:
    raw = data.file.read()
    filename = data.filename
    log.debug("upload: {} ({} bytes).".format(filename, len(raw)))
  else:
    log.error("upload failed")
    
  # set header to unique ID used to request compressed img
  uniqueID = uuid1().int
  response.set_header("X-uploadid", uniqueID)
  
  # send request to face detection api
  sendHPIDOLrequest(filename, raw, uniqueID)


def sendHPIDOLrequest(filename, raw, uniqueID):
  apikey="9e91cb08-3b8c-4c0e-a0fa-256c75fe2f07"
  url="https://api.idolondemand.com/1/api/sync/detectfaces/v1"
  headers={"Content-Type" : "multipart/related"}
  
  io = StringIO(raw)
  img = Image.open(io)
  
  files = {"file": (filename, BytesIO(raw), "image/jpeg", headers)}
  args = {"apikey": apikey}
  
  _response=requests.post(url,files=files,data=args)
  log.debug("response content: {}".format(_response.content))

  faces=json.loads(_response.content)
  face_regions=[]
  face_coords=[]
  
  for face in faces['face']:
    face_tuple=(face["left"],face["top"],face["left"]+face["width"],face["top"]+face["height"])
    face_coords.append(face_tuple)
    region=img.crop(face_tuple)
    face_regions.append(region)
  
  out = StringIO()
  img.save(out, 'JPEG', quality=10)
  out = StringIO(out.getvalue())
  compressed = Image.open(out)
  
  for i in range(len(face_regions)):
    compressed.paste(face_regions[i],face_coords[i])
  
  log.debug("caching fpeg image: {}".format(uniqueID))
  CACHE[str(uniqueID)] = compressed


@get('/get/<ID>')
def getter(ID):
  send = StringIO()
  img = CACHE[ID]
  img.save(send, 'JPEG', quality=75)
  send = b2a_base64(send.getvalue())
  
  response.set_header("content-type", "image/jpeg")
  return send


    

application = bottle.app()
application.catchall = False

bottle.run(application, host='0.0.0.0', port=os.getenv('PORT', 8080))
