#!/usr/bin/env python
#
# Copyright 2013 - Xavier Berger - http://rpi-experiences.blogspot.fr/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
#
# rpimonitordm (RPi-Monitor Data Miner) is a plugin for RPi-Monitor-LCD
# designed to extract and make available current data from RPi-Monitor.
# To decrease server load, rpimonitordm will only query the server is
# cached data are too old.
#
import time, httplib, json, pprint, datetime

class Singleton(object):
  class __Singleton:

    def __init__(self):
      self.lastUpdate = 0
      connection = httplib.HTTPConnection("localhost", 8888)
      connection.request("GET","/static.json")
      response = connection.getresponse()
      if ( response.status == 200 ):
        self.static = json.loads(response.read())
      connection.close()
   
    def getData(self):
      if (time.time() - self.lastUpdate ) >  10:
        connection = httplib.HTTPConnection("localhost", 8888)
        connection.request("GET","/dynamic.json")
        response = connection.getresponse()
        if ( response.status == 200 ):
          self.data = json.loads(response.read())
        connection.close()
        self.lastUpdate=time.time()
        self.data.update(self.static)
      return self.data

    def uptime(self):
      data = getData()
      return str(datetime.timedelta(0,float(data['uptime']))).split('.')[0]

    def disk(self, diskname):
      data = getData()
      return "%.2f%%" % (data["%s_used" % diskname]/data["%s_total" % diskname]*100)

    def memory(self):
      data = getData()
      return "%.2f%%" % ((data["memory_total"] - data["memory_free"])/data["memory_total"]*100)

  instance = None

  def __new__(c):
    if not Singleton.instance:
      Singleton.instance = Singleton.__Singleton()
    return Singleton.instance

def getData():
  singleton = Singleton()
  return singleton.getData()
  
def uptime():
  singleton = Singleton()
  return singleton.uptime()
  
def disk(diskname):
  singleton = Singleton()
  return singleton.disk(diskname)

def memory():
  singleton = Singleton()
  return singleton.memory()


if __name__ == '__main__':
  data = getData()
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(data)
  uptime()
  print disk("sdcard_boot")
  print disk("sdcard_root")
  while True:
    data = getData()
    print data['uptime']
    time.sleep(3.5);

 
