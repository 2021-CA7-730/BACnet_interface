# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 13:22:28 2021

@author: jonas
"""
from preheat_open import set_api_key
import preheat_open as pha 

set_api_key("hoMakXsr1kI0rymjM3Z7djD71KMKa0zzR3EOqGdZfQTE3F9vYV")

location_id = 2245
start = "2021-09-18 00:00:00"
stop = "2021-09-23 12:00:00"
res = "minute"
b = pha.Building(location_id)
room = b.query_units("indoorClimate")[1]

room.load_data(start, stop, res)
print(room.data)