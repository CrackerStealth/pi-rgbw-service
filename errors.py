# Custom class used to define a configuration error with Pi RGB Services
class ConfigError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)