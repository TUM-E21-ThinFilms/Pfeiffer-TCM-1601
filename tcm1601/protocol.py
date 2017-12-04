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

import slave

import e21_util
from e21_util.lock import InterProcessTransportLock
from e21_util.error import CommunicationError

from slave.protocol import Protocol
from slave.transport import Timeout

from message import AbstractMessage, RawMessage


class PfeifferTCM1601Protocol(Protocol):
    def __init__(self, logger):
        self.encoding = "ascii"
        self.logger = logger

    def set_logger(self, logger):
        self.logger = logger

    def create_message(self, message):
        msg = message.get_raw()
        # msg.apply_converter(message.get_pre_converter())
        msg.use_checksum()

        return msg.get_raw()

    def clear(self, transport):
        with InterProcessTransportLock(transport):
            self.logger.debug("Clearing message buffer...")
            try:
                while True:
                    transport.read_bytes(32)
            except slave.transport.Timeout:
                return

    def get_response(self, transport):
        try:
            raw = transport.read_until(RawMessage.TERMINATOR)
            return "".join([chr(x) for x in raw]) + RawMessage.TERMINATOR
        except slave.transport.Timeout:
            raise CommunicationError("Received a timeout while reading response")

    def parse_response(self, response, message):
        resp = RawMessage()
        resp.from_raw_message(response)
        # resp.apply_converter(message.get_post_converter())
        return resp

    def write(self, transport, message):
        if not isinstance(message, AbstractMessage):
            raise RuntimeError("Given message is not an instance of AbstractMessage")

        with InterProcessTransportLock(transport):
            msg = self.create_message(message)
            self.logger.debug('Sending: %s', repr(msg))
            with transport:
                transport.write(msg)
                response = self.get_response(transport)
            self.logger.debug('Response: %s', repr(response))
            return self.parse_response(response, message)

    def query(self, transport, message):
        return self.write(transport, message)
