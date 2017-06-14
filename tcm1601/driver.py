# Copyright (C) 2016, see AUTHORS.md
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

from protocol import PfeifferTCM1601Protocol
from message import ReadMessage, WriteMessage, AbstractConverter, BooleanConverter, FloatConverter, IntegerConverter, \
    StringConverter, ShortConverter, ExponentialConverter
from slave.driver import Driver, Command, _load, _typelist
from slave.types import Mapping, Stream, Float

PARAMETER_STANDBY = 2
PARAMETER_PUMP_STAT = 10
PARAMETER_MOTOR_TURBOPUMP = 23

PARAMETER_ACTUAL_ROTATION_SPEED = 309
PARAMETER_SET_ROTATION_SPEED = 308
PARAMETER_ERROR_CODE = 303
PARAMETER_MOTOR_CURRENT = 310
PARAMETER_MOTOR_OPERATION_HOURS = 311

class PfeifferTCM1601xDriver(Driver):
    def __init__(self, transport, protocol=None, address=None):
        if protocol is None:
            protocol = PfeifferTCM1601Protocol(None)

        self.transport = transport
        self.protocol = protocol

        if address is None:
            address = "0"

        self.address = address

        super(PfeifferTCM1601xDriver, self).__init__(transport, protocol)

    def query_message(self, msg):
        msg.get_raw().set_address(self.address)
        msg.get_raw().apply_converter(msg.get_pre_converter())
        response = self.protocol.write(self.transport, msg)
        response.apply_converter(msg.get_post_converter())
        return response

    def get_transport(self):
        return self.transport

    def get_protocol(self):
        return self.protocol

    def standby(self, on_off):
        msg = WriteMessage(BooleanConverter(), BooleanConverter())
        msg.set_parameter(PARAMETER_STANDBY)
        msg.set_data(on_off)
        return self.query_message(msg)

    def is_standby(self):
        msg = ReadMessage(BooleanConverter())
        msg.set_parameter(PARAMETER_STANDBY)
        return self.query_message(msg)

    def pumpstat(self, on_off):
        msg = WriteMessage(BooleanConverter(), BooleanConverter())
        msg.set_parameter(PARAMETER_PUMP_STAT)
        msg.set_data(on_off)
        return self.query_message(msg)

    def is_pumpstat(self):
        msg = ReadMessage(BooleanConverter())
        msg.set_parameter(PARAMETER_PUMP_STAT)
        return self.query_message(msg)

    def motor_pump(self, on_off):
        msg = WriteMessage(BooleanConverter(), BooleanConverter())
        msg.set_parameter(PARAMETER_MOTOR_TURBOPUMP)
        msg.set_data(on_off)
        return self.query_message(msg)

    def is_motor_pump(self):
        msg = ReadMessage(BooleanConverter())
        msg.set_parameter(PARAMETER_MOTOR_TURBOPUMP)
        return self.query_message(msg)

    def get_actual_rotation_speed(self):
        msg = ReadMessage(IntegerConverter())
        msg.set_parameter(PARAMETER_ACTUAL_ROTATION_SPEED)
        return self.query_message(msg)

    def get_set_rotation_speed(self):
        msg = ReadMessage(IntegerConverter())
        msg.set_parameter(PARAMETER_SET_ROTATION_SPEED)
        return self.query_message(msg)

    def get_error(self):
        msg = ReadMessage(StringConverter())
        msg.set_parameter(PARAMETER_ERROR_CODE)
        return self.query_message(msg)

    def get_motor_current(self):
        msg = ReadMessage(FloatConverter())
        msg.set_parameter(PARAMETER_MOTOR_CURRENT)
        return self.query_message(msg)

    def get_motor_operation_hours(self):
        msg = ReadMessage(IntegerConverter())
        msg.set_parameter(PARAMETER_MOTOR_OPERATION_HOURS)
        return self.query_message(msg)