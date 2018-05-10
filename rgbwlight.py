import json
import syslog

import RPi.GPIO as gpio

from errors import *

# This class is used for controlling an RGB light instance on the Raspberry Pi
class RgbwLight ():
    name = None
    enable_onoff = False
    enable_rgb = False
    enable_ww = False
    enable_cw = False
    
    gpio_onoff = 0
    gpio_red = 0
    gpio_green = 0
    gpio_blue = 0
    gpio_ww = 0
    gpio_cw = 0
    
    current_onoff_state = False
    current_red_state = 0
    current_green_state = 0
    current_blue_state = 0
    current_warm_white_state = 0
    current_cool_white_state = 0
    
    saved_red_state = None
    saved_green_state = None
    saved_blue_state = None
    saved_warm_white_state = None
    saved_cool_white_state = None
    
    # Create an instance of an RGBW light initialization parameters
    def __init__ (self, name, enable_onoff, enable_rgb, enable_ww, enable_cw, gpio_onoff, gpio_red, gpio_green, gpio_blue, gpio_ww, gpio_cw):
        gpio.setmode(gpio.BCM)
        
        self.name = name
        
        self.enable_onoff = enable_onoff
        self.enable_rgb = enable_rgb
        self.enable_ww = enable_ww
        self.enable_cw = enable_cw
        
        self.gpio_onoff = gpio_onoff
        self.gpio_red = gpio_red
        self.gpio_green = gpio_green
        self.gpio_blue = gpio_blue
        self.gpio_ww = gpio_ww
        self.gpio_cw = gpio_cw
        
        self.validate()
        self.gpioSetup()
    
    # Create an instance of an RGBW light from an object
    def __init__ (self, name, object):
        gpio.setmode(gpio.BCM)
        
        self.name = name
        
        self.enable_onoff = object['enable_onoff']
        self.enable_rgb = object['enable_rgb']
        self.enable_ww = object['enable_ww']
        self.enable_cw = object['enable_cw']
        
        self.gpio_onoff = object['gpio_onoff']
        self.gpio_red = object['gpio_red']
        self.gpio_green = object['gpio_green']
        self.gpio_blue = object['gpio_blue']
        self.gpio_ww = object['gpio_ww']
        self.gpio_cw = object['gpio_cw']
        
        self.validate()
        self.gpioSetup()

    # This instance of an RGBW light no longer exists
    def __del__(self):
        gpio.cleanup()

    # Return the name of this object
    def getName(self):
        return self.name

    # Turn the light on
    def turnOn(self):
        if self.enable_onoff:
            self.current_onoff_state = True
        
        if self.enable_cw:
            self.current_red_state = 0
            self.current_green_state = 0
            self.current_blue_state = 0
            self.current_warm_white_state = 0
            self.current_cool_white_state = 255
        elif self.enable_ww:
            self.current_red_state = 0
            self.current_green_state = 0
            self.current_blue_state = 0
            self.current_warm_white_state = 255
            self.current_cool_white_state = 0
        elif self.enable_rgb:
            self.current_red_state = 255
            self.current_green_state = 255
            self.current_blue_state = 255
            self.current_warm_white_state = 0
            self.current_cool_white_state = 0
        else:
            self.current_red_state = 0
            self.current_green_state = 0
            self.current_blue_state = 0
            self.current_warm_white_state = 0
            self.current_cool_white_state = 0
        
        self.restoreState()
        self.syncState()
    
    # Turn the light off
    def turnOff(self):
        self.saveState()
        
        self.current_onoff_state = False
        self.current_red_state = 0
        self.current_green_state = 0
        self.current_blue_state = 0
        self.current_warm_white_state = 0
        self.current_cool_white_state = 0
        
        self.syncState()
    
    # Save the current color state
    def saveState(self):
        self.saved_red_state = self.current_red_state
        self.saved_green_state = self.current_green_state
        self.saved_blue_state = self.current_blue_state
        self.saved_warm_white_state = self.current_warm_white_state
        self.saved_cool_white_state = self.current_cool_white_state
    
    # Save the current color state
    def restoreState(self):
        if self.saved_red_state != None:
          self.current_red_state = self.saved_red_state
        if self.saved_green_state != None:
          self.current_green_state = self.saved_green_state
        if self.saved_blue_state != None:
          self.current_blue_state = self.saved_blue_state
        if self.saved_warm_white_state != None:
          self.current_warm_white_state = self.saved_warm_white_state
        if self.saved_cool_white_state != None:
          self.current_cool_white_state = self.saved_cool_white_state
    
    # Set the RGB Color
    def setRGB(self, red, green, blue):
        if not self.enable_rgb:
            raise ConfigError('Cannot set state of RGB light when RGB is disabled.')
        if not (0 <= red <= 255):
            raise ConfigError('The red brightness must be between 0 and 255.')
        if not (0 <= green <= 255):
            raise ConfigError('The green brightness must be between 0 and 255.')
        if not (0 <= blue <= 255):
            raise ConfigError('The blue brightness must be between 0 and 255.')
        
        self.current_onoff_state = True
        self.current_red_state = red
        self.current_green_state = green
        self.current_blue_state = blue
        self.current_warm_white_state = 0
        self.current_cool_white_state = 0
        
        self.syncState()
    
    # Set the warm white brightness
    def setWW(self, brightness):
        if not self.enable_ww:
            raise ConfigError('Cannot set state of warm white light when warm white is disabled.')
        if not (0 <= brightness <= 255):
            raise ConfigError('The warm white brightness must be between 0 and 255.')
            
        self.current_onoff_state = True
        self.current_red_state = 0
        self.current_green_state = 0
        self.current_blue_state = 0
        self.current_warm_white_state = brightness
        self.current_cool_white_state = 0
        
        self.syncState()
    
    # Set the cool white brightness
    def setCW(self, brightness):
        if not self.enable_cw:
            raise ConfigError('Cannot set state of cool white light when cool white is disabled.')
        if not (0 <= brightness <= 255):
            raise ConfigError('The cool white brightness must be between 0 and 255.')
            
        self.current_onoff_state = True
        self.current_red_state = 0
        self.current_green_state = 0
        self.current_blue_state = 0
        self.current_warm_white_state = 0
        self.current_cool_white_state = brightness
        
        self.syncState()
    
    # Validate State
    def validate(self):
        if self.enable_onoff != False and self.enable_onoff != True:
            raise ConfigError('On/Off is not configured correctly.')
        if self.enable_rgb != False and self.enable_rgb != True:
            raise ConfigError('RGB is not configured correctly.')
        if self.enable_ww != False and self.enable_ww != True:
            raise ConfigError('Warm White is not configured correctly.')
        if self.enable_cw != False and self.enable_cw != True:
            raise ConfigError('Cool White is not configured correctly.')
        if not (2 <= self.gpio_onoff <= 27):
            raise ConfigError('GPIO pin for On/Off is not configured correctly.')
        if not (2 <= self.gpio_red  <= 27):
            raise ConfigError('GPIO pin for the color red is not configured correctly.')
        if not (2 <= self.gpio_green  <= 27):
            raise ConfigError('GPIO pin for the color green is not configured correctly.')
        if not (2 <= self.gpio_blue  <= 27):
            raise ConfigError('GPIO pin for the color blue is not configured correctly.')
        if not (2 <= self.gpio_ww  <= 27):
            raise ConfigError('GPIO pin for warm white is not configured correctly.')
        if not (2 <= self.gpio_cw  <= 27):
            raise ConfigError('GPIO pin for cool white is not configured correctly.')
            
    # Setup the GPIO pins for use
    def gpioSetup(self):
        if self.enable_onoff:
            gpio.setup(self.gpio_onoff, gpio.OUT)
        
        if self.enable_rgb:
            gpio.setup(self.gpio_red, gpio.OUT)
            gpio.setup(self.gpio_green, gpio.OUT)
            gpio.setup(self.gpio_blue, gpio.OUT)
        
        if self.enable_ww:
            gpio.setup(self.gpio_ww, gpio.OUT)
        
        if self.enable_cw:
            gpio.setup(self.gpio_cw, gpio.OUT)

    # Make changes to the state of the RGBW light on the GPIO
    def syncState (self):
        if self.enable_onoff:
            if self.current_onoff_state:   
                gpio.output(self.gpio_onoff, gpio.HIGH)
            else:   
                gpio.output(self.gpio_onoff, gpio.LOW)
        
        if self.enable_rgb:
            pwmRed = gpio.PWM(self.gpio_red, 50)
            pwmRed.ChangeDutyCycle((self.current_red_state / 255 * 100))
            
            pwmGreen = gpio.PWM(self.gpio_green, 50)
            pwmGreen.ChangeDutyCycle((self.current_green_state / 255 * 100))
            
            pwmBlue = gpio.PWM(self.gpio_blue, 50)
            pwmBlue.ChangeDutyCycle((self.current_blue_state / 255 * 100))
        
        if self.enable_ww:
            pwmWarmWhite = gpio.PWM(self.gpio_ww, 50)
            pwmWarmWhite.ChangeDutyCycle((self.current_warm_white_state / 255 * 100))
        
        if self.enable_cw:
            pwmCoolWhite = gpio.PWM(self.gpio_cw, 50)
            pwmCoolWhite.ChangeDutyCycle((self.current_cool_white_state / 255 * 100))
    
    # Return a raw object version of the RGBW light. Useful to convert into JSON object later.
    def getObject(self):
        element = {'name': self.name, 'enable_onoff': self.enable_onoff, 'enable_rgb': self.enable_rgb, 'enable_ww': self.enable_ww, 'enable_cw': self.enable_cw, 'onoff_state': self.current_onoff_state, 'red_state' : self.current_red_state, 'green_state' : self.current_green_state, 'blue_state' : self.current_blue_state, 'warm_white_state' : self.current_warm_white_state, 'cool_white_state' : self.current_cool_white_state }
        
        return element
        
    # Return the JSON formatted version of the RGBW light.
    def getJSON(self):
        return json.dumps(self.getObject())
    