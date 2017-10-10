# -*- coding: utf-8 -*-

import serial
import json


class Arduino:

    def __init__(self, address):
        """
        Address - COM4/8
        """
        self.ser = serial.Serial(address, 9600)

    def read(self, sensor_key):
        response = self.read_measurement(sensor_key)
        data = self.convert_response(response)
        return(data)

    def read_measurement(self, sensor_key):
        self.ser.write(sensor_key)

        bytes_response = self.ser.readline()
        string_response = str(bytes_response, 'utf-8')
        response = string_response.replace('\r\n', '')

        return response

    def convert_response(self, response):
        d_in = json.loads(response)
        d_out = {}
        for key, value in d_in.items():
            d_out[key] = float(value)
        return d_out
