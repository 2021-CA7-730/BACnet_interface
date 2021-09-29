# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 13:45:11 2021

@author: jonas
"""
import bacpypes as bac
from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import run
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
_debug = 0
_log = ModuleLogger(globals())
args = ConfigArgumentParser(description=__doc__).parse_args()


import sys
import re
import socket
import struct
import time
#DELL_IP = "169.254.72.213"
#gets data from local host
DELL_IP = "172.26.13.96"
HVAC_IP = "172.26.12.106"
DELL_PORT = 25000
HVAC_PORT = 25000
HVAC_PORT_TRANSMIT = 4796
NUM_SENSORS = 2

sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((DELL_IP, DELL_PORT))
sock.settimeout(0.00001)

# contains valid sensors and initial values
SENSOR_DATA_DICT = {k:0 for k in range(1, 256)}

ACTUATOR_DATA_DICT = {k:0 for k in range(1, 256)}

def get_latest_messege(ReceiveIP, ReceivePORT):
    data = []
    while True:
        try:
            data.append(sock.recvfrom(1024)) # buffer size is 1024 bytes
        except socket.timeout : 
                for messeges in reversed(data):
                    if messeges[1] == (ReceiveIP, ReceivePORT):
                        return messeges[0]
                
                return -1
            

def get_sensor_values(data):
    # splits the data stream up in fives and updates the values of the idx
    sensor_dict = {}
    sensor_IDS = [data[i] for i in range(0, len(data), 5)]
    sensor_values = [data[i+1:i+5] for i in range(0, len(data), 5)]
    
    for idx, ID in enumerate(sensor_IDS) : 
        sensor_dict[ID] = struct.unpack('f', sensor_values[idx])[0]
    return sensor_dict
    


def read_actuator(ID):
    global ACTUATOR_DATA_DICT
    return ACTUATOR_DATA_DICT[ID]

def write_actuator(ID, value):
    global ACTUATOR_DATA_DICT
    ACTUATOR_DATA_DICT[ID] = value
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = bytes()
    for k, v in ACTUATOR_DATA_DICT.items():
        message += struct.pack("B", k)
        message += struct.pack("f", v)
    sock.sendto(message, (HVAC_IP, HVAC_PORT))
    
    return
    
def read_sensor(ID):
    global SENSOR_DATA_DICT
    data = get_latest_messege(HVAC_IP, HVAC_PORT_TRANSMIT)
    if data != -1:
        SENSOR_DATA_DICT = get_sensor_values(data)
    
    return SENSOR_DATA_DICT[ID]


    

class SensorValueObject(bac.object.AnalogValueObject):
    properties = []
    

class SensorValueProperty(bac.object.Property):
  #creates a subclass of the sensorobject
  def __init__(self, identifier, sensorID):
    bac.object.Property.__init__(self, identifier, bac.primitivedata.Real, default=0.0, optional=True, mutable=False)
    self.sensorID = sensorID

  def ReadProperty(self, obj, arrayIndex=None):
  # reads data from sensor into the right ID
   return read_sensor(self.sensorID)
   
  def WriteProperty(self, obj, value, arrayIndex=None, priority=None, direct=False):
    raise  bac.errors.ExecutionError(errorClass='property', errorCode='writeAccessDenied')


class ActuatorObject(bac.object.AnalogOutputObject):
    properties = []

class ActuatorValueProperty(bac.object.WritableProperty):
    def __init__(self, identifier, actuatorID):
        bac.object.WritableProperty.__init__(self, identifier, bac.primitivedata.Real)
        self.actuatorID = actuatorID
    
    def ReadProperty(self, obj, arrayIndex = None): 
        return read_actuator(self.actuatorID)
        
    def WriteProperty(self, obj, value, arrayIndex=None, priority=None, direct=False):
        return write_actuator(self.actuatorID, value)
        
        
        


def main():

    # code goes here...
    this_device = LocalDeviceObject(
        objectName=args.ini.objectname,
        objectIdentifier=int(args.ini.objectidentifier),
        maxApduLengthAccepted=int(args.ini.maxapdulengthaccepted),
        segmentationSupported=args.ini.segmentationsupported,
        vendorIdentifier=int(args.ini.vendoridentifier),
        vendorName="B612",
    )

    if _debug: _log.debug("initialization")
    if _debug: _log.debug("    - args: %r", args)

    try:
        # code goes here...

        _log.debug("initialization")
        # code goes here...
        
        actuators = [
            {'name': 'HR:DC01:Damper_outside_intake', 'id': 1, 'units': 'noUnits'},
            {'name': 'HR:DC02:Damper_cross', 'id': 2, 'units': 'noUnits'},
            {'name': 'HR:DC03:Damper_lab_intake', 'id': 3, 'units': 'noUnits'},
            
            {'name': 'HR:FC01:Fan_intake', 'id': 11, 'units': 'noUnits'},
            {'name': 'HR:FC02:Fan_exhaust', 'id': 12, 'units': 'noUnits'},
            
            {'name': 'HR:JC01-1:Electric_heater', 'id': 21, 'units': 'noUnits'},
            {'name': 'HR:JC01-2:Electric_heater', 'id': 22, 'units': 'noUnits'}, 
            {'name': 'HR:JC01-3:Electric_heater', 'id': 23, 'units': 'noUnits'}, 
            {'name': 'HR:JC01-4:Electric_heater', 'id': 24, 'units': 'noUnits'}, 
            {'name': 'HR:JC01-5:Electric_heater', 'id': 25, 'units': 'noUnits'}, 
            {'name': 'HR:JC01-6:Electric_heater', 'id': 26, 'units': 'noUnits'}, 
            {'name': 'HR:JC01-7:Electric_heater', 'id': 27, 'units': 'noUnits'}, 
            {'name': 'HR:JC01-8:Electric_heater', 'id': 28, 'units': 'noUnits'}, 
            {'name': 'HR:JC01-9:Electric_heater', 'id': 29, 'units': 'noUnits'}, 
            
            {'name': 'HR:VC01:Solonoid_valve_tank', 'id': 31, 'units': 'noUnits'}, 
            {'name': 'HR:VC02:3-way_valve_tank', 'id': 32, 'units': 'noUnits'}, 
            {'name': 'HR:VC03:3-way_valve_tank_heater', 'id': 33, 'units': 'noUnits'}, 
            {'name': 'HR:VC04:3-way_valve_condesor', 'id': 34, 'units': 'noUnits'}, 
            
            {'name': 'HR:SC01:Pump_into_tank', 'id': 41, 'units': 'noUnits'}, 
            {'name': 'HR:SC02:Pump_into_condensor', 'id': 42, 'units': 'noUnits'}
            
            
            
            
            
            ]
        
        
        sensors = [
        
            {'name': 'HR:TT01:Temperature_outside_intake', 'id': 1, 'units': 'degreesCelsius'},
            {'name': 'HR:TT02:Temperature_after_crossflow_damper', 'id': 2, 'units': 'degreesCelsius'},
            {'name': 'HR:TT03:Temperature_outside', 'id': 3, 'units': 'degreesCelsius'},
            {'name': 'HR:TT04:Temperature_after_heating_coil', 'id': 4, 'units': 'degreesCelsius'},
            {'name': 'HR:TT05:Temperature_lab_exhaust', 'id': 5, 'units': 'degreesCelsius'},
            {'name': 'HR:TT06:Temperature_lab_intake', 'id': 6, 'units': 'degreesCelsius'},
            {'name': 'HR:TT07:Temperature_accumulator', 'id': 7, 'units': 'degreesCelsius'},
            {'name': 'HR:TT08:Temperature_condensor', 'id': 8, 'units': 'degreesCelsius'},
            {'name': 'HR:TT09:Temperature_condesor_manifold', 'id': 9, 'units': 'degreesCelsius'},
            {'name': 'HR:TT10:Temperature_heatingcoil_inflow', 'id': 10, 'units': 'degreesCelsius'},
            {'name': 'HR:TT11:Temperature_heatingcoil_outflow', 'id': 11, 'units': 'degreesCelsius'},
            {'name': 'HR:TT12:Temperature_watertank_heating_out', 'id': 12, 'units': 'degreesCelsius'},
            {'name': 'HR:TT13:Temperature_watertank_top', 'id': 13, 'units': 'degreesCelsius'},
            {'name': 'HR:TT14:Temperature_watertank_middle', 'id': 14, 'units': 'degreesCelsius'},
            {'name': 'HR:TT15:Temperature_watertank_bottom', 'id': 15, 'units': 'degreesCelsius'},     
            
            {'name': 'HR:DC01:Damper_outside_intake_opening', 'id': 21, 'units': 'noUnits'},  
            {'name': 'HR:DC02:Damper_cross_opening', 'id': 22, 'units': 'noUnits'},  
            {'name': 'HR:DC03:Damper_lab_intake_opening', 'id': 23, 'units': 'noUnits'},  
         
            {'name': 'HR:VC01:Solonoid_valve_tank_opening', 'id': 31, 'units': 'noUnits'}, 
            {'name': 'HR:VC02:3-way_valve_tank_opening', 'id': 32, 'units': 'noUnits'}, 
            {'name': 'HR:VC03:3-way_valve_tank_heater_opening', 'id': 33, 'units': 'noUnits'}, 
            {'name': 'HR:VC04:3-way_valve_condesor_opening', 'id': 34, 'units': 'noUnits'}

        ]
        
        this_application = BIPSimpleApplication(this_device, args.ini.address)
        if _debug: _log.debug("    - this_application: %r", this_application)
        
        services_supported = this_application.get_services_supported()
        if _debug: _log.debug("    - services_supported: %r", services_supported)
        
        
        # initialize all sensors
        for sensor in sensors:
            sensor_object = SensorValueObject(
                objectIdentifier=('analogValue', sensor['id']),
                objectName=sensor['name'],
                units=sensor['units']
                )
            sensor_object.add_property(SensorValueProperty('presentValue', sensor['id']))
            this_application.add_object(sensor_object)
            
            
        # initialize all actuators
        for actuator in actuators:
            actuator_object = ActuatorObject(
                objectIdentifier = ('analogOutput', actuator['id']), 
                objectName=actuator['name'],
                units = ['units']
                )
            actuator_object.add_property(ActuatorValueProperty('presentValue', actuator['id']))
            this_application.add_object(actuator_object)
        
        run()
        _log.debug("running")
        

    except Exception as e:
        _log.exception("an error has occurred: %s", e)
    finally:
        _log.debug("finally")

if __name__ == "__main__":
    main()