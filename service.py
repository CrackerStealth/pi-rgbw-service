import datetime
import json
import socket
import syslog

from twisted.internet import reactor
from twisted.internet import ssl
from twisted.internet.protocol import Protocol
from twisted.web import server
from twisted.web.resource import Resource
from twisted.web.static import File

from rgbwlight import *
from errors import *

# This resource handler is used to provide JSON output for the sensor.json
# resource request. A GET request parameter 'sensor' can get added with
# the name of the sensor being queries. Otherwise, returns all sensors.
class ApiHandler(Resource):
    isLeaf = True
    obj_list = None
    
    def __init__ (self, light_obj):
        Resource.__init__(self)
        self.obj_list = light_obj
    
    def render_GET(self, request):
        # We are returning JSON text to the client
        request.setHeader('Content-Type', 'application/json')
        
        # Build the list of lights
        light_list = []
        
        # If the root context of the API path is called, we want to return a list
        if request.path == '/api/' or request.path == '/api':
            # Loop through all the lights to add to the response.
            for o in self.obj_list:
                light_list.append(o.getName())
        
            return json.dumps({'hostname': socket.gethostname(), 'date': str(datetime.datetime.now()), 'lights': light_list})
        # Otherwise we are looking for a specific light
        else:
            # Prase the request for entity id
            entityId = request.path[5:].lower()
            entityId = entityId.split('/')[0]
            
            # Loop through all the lights to find a specific one.
            for o in self.obj_list:
                if o.getName().lower() == entityId:
                    return json.dumps(o.getObject())
        
        # If we get this far, no objects found to return
        request.setResponseCode(404)
        return json.dumps({ 'error_code': 404, 'error_message': 'The following object could not be found: ' + request.path[5:].lower() })

    def render_PUT(self, request):
        # We are returning JSON text to the client
        request.setHeader('Content-Type', 'application/json')
        
        request.setResponseCode(405)        
        return json.dumps({ 'error_code': 405, 'error_message': 'The PUT action is not availble for the requested resource.'})

    def render_POST(self, request):
        # We are returning JSON text to the client
        request.setHeader('Content-Type', 'application/json')
        
        # If the root context of the API path is called, we want to return bad request because we are expecting an entity id
        if request.path == '/api/':
            request.setResponseCode(400)
            return json.dumps({ 'error_code': 400, 'error_message': 'Bad request received from the client. We need an entity id to POST an update.'})
        
        # Parse the body of the content
        try:
            postBody = json.loads(request.content.read())
        except:
            request.setResponseCode(400)
            return json.dumps({ 'error_code': 400, 'error_message': 'Bad request received from the client. Body could not be parsed as JSON object.'})
        
        # Find our entoty to update the status of
        entityObj = None
        entityId = request.path[5:].lower()
        entityId = entityId.split('/')[0]
        for o in self.obj_list:
            if o.getName().lower() == entityId:
                entityObj = o
        
        # If we did not find an entity, report not found
        if entityObj == None:
            request.setResponseCode(404)
            return json.dumps({ 'error_code': 404, 'error_message': 'The following object could not be found: ' + request.path[5:].lower() })
        
        try:
            # Check if we are changing the on/off state
            if 'onoff_state' in postBody:
                if type(postBody['onoff_state']) == type(True):
                    if postBody['onoff_state']:
                        entityObj.turnOn()
                    else:
                        entityObj.turnOff()
                else:
                    request.setResponseCode(400)
                    return json.dumps({ 'error_code': 400, 'error_message': 'Bad request received from the client. ''onoff_state'' is expected to be a boolean.'})
            
            # Check if we are changing the RGB color
            if 'red_state' in postBody or 'green_state' in postBody or 'blue_state' in postBody:
                if 'red_state' in postBody and 'green_state' in postBody and 'blue_state' in postBody:
                    if type(postBody['red_state']) == type(255) and type(postBody['green_state']) == type(255) and type(postBody['blue_state']) == type(255):
                        entityObj.setRGB(postBody['red_state'], postBody['green_state'], postBody['blue_state'])
                    else:
                        request.setResponseCode(400)
                        return json.dumps({ 'error_code': 400, 'error_message': 'Bad request received from the client. ''red_state'', ''green_state'', and ''blue_state'' are all expected to be an integer.'})
                else:
                    request.setResponseCode(400)
                    return json.dumps({ 'error_code': 400, 'error_message': 'Bad request received from the client. ''red_state'', ''green_state'', and ''blue_state'' are all expected to be included together.'})
            # Check if we are changing the Warm White brightness
            if 'warm_white_state' in postBody:
                if type(postBody['warm_white_state']) == type(255):
                    entityObj.setWW(postBody['warm_white_state'])
                else:
                    request.setResponseCode(400)
                    return json.dumps({ 'error_code': 400, 'error_message': 'Bad request received from the client. ''warm_white_state'' is expected to be an integer.'})
            
            # Check if we are changing the Cool White brightness
            if 'cool_white_state' in postBody:
                if type(postBody['cool_white_state']) == type(255):
                    entityObj.setCW(postBody['cool_white_state'])
                else:
                    request.setResponseCode(400)
                    return json.dumps({ 'error_code': 400, 'error_message': 'Bad request received from the client. ''cool_white_state'' is expected to be an integer.'})
        except Exception as msg:
            request.setResponseCode(500)
            return json.dumps({ 'error_code': 500, 'error_message': str(msg)})
        
        # If we get this far, the operation completed successfully
        request.setResponseCode(200)
        return json.dumps({ 'code': 200, 'message': 'Entity modified.'})
        
    def render_DELETE(self, request):
        # We are returning JSON text to the client
        request.setHeader('Content-Type', 'application/json')
        
        request.setResponseCode(405)
        return json.dumps({ 'error_code': 405, 'error_message': 'The DELETE action is not availble for the requested resource.'})


if __name__ == '__main__':
    # List of sensor objects
    light_obj = []
    
    # Enable logging for the application
    syslog.openlog('pi_rgbw_service')
    
    # Read from the config file
    config_file = open('config.json')
    config = json.load(config_file)
    config_file.close()
    
    # Read the standard config items
    listen_port = config['listen_port']
    ssl_key = config['ssl_key']
    ssl_cert = config['ssl_cert']
    
    # Read the sensor types from the JSON file
    for (n,c) in config['lights'].items():
        light = RgbwLight(n, c)
        light_obj.append(light)
    
    # Create the SITE to be hosted by our service
    root = File('www')
    root.putChild('api', ApiHandler(light_obj))
    site = server.Site(root)
    
    # Start the HTTPS server for the service
    sslContext = ssl.DefaultOpenSSLContextFactory(ssl_key, ssl_cert)
    reactor.listenSSL(listen_port, site, sslContext)

    reactor.run()
