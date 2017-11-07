from decimal import Decimal


class RawMessage(object):
    ACTION_READ = "00"
    ACTION_WRITE = "10"

    QUERY_READ = "=?"
    TERMINATOR = chr(13)  # Carriage return

    def __init__(self):
        self._address = ""
        self._action = ""
        self._parameternumber = ""
        self._length = ""
        self._data = ""
        self._checksum = ""
        pass

    def from_raw_message(self, raw_message):
        if len(raw_message) < 14:
            raise RuntimeError("Given raw message is too short (< 14 chars)")

        self._address = raw_message[0:3]
        self._action = raw_message[3:5]
        self._parameternumber = raw_message[5:9]
        self._length = raw_message[9:11]
        self._checksum = raw_message[-4:-1]
        self._data = raw_message[11:-4]

        if not raw_message[-1:] == self.TERMINATOR:
            raise RuntimeError("Given raw message does not terminate with carriage return")

        if not self._action in [self.ACTION_READ, self.ACTION_WRITE]:
            raise RuntimeError("Given raw message contains the wrong action type")

        if self._action == self.ACTION_READ and not self._data == self.QUERY_READ:
            raise RuntimeError("Given raw message is read only, but data doesn't match up")

        if not int(self._length) == len(self._data):
            raise RuntimeError("Given raw message contains the wrong data length")

    def get_address(self):
        return self._address

    def get_action(self):
        return self._action

    def get_parameternumber(self):
        return self._parameternumber

    def get_datalength(self):
        return self._length

    def get_data(self):
        return self._data

    def get_checksum(self):
        return self._checksum

    def get_raw(self):
        return "".join([self._address, self._action, self._parameternumber, self._length, self._data, self._checksum,
                        self.TERMINATOR])

    def set_address(self, address):
        new_addr = str(address).zfill(3)
        if len(new_addr) > 3:
            raise RuntimeError("Given address is too long")

        self._address = new_addr

    def set_action(self, action):
        new_action = str(action).zfill(2)
        if not new_action in [self.ACTION_READ, self.ACTION_WRITE]:
            raise RuntimeError("Given action is unknown")

        self._action = new_action

    def set_parameternumber(self, number):
        new_param = str(number).zfill(3)
        if len(new_param) > 3:
            raise RuntimeError("Given number is too large")

        if int(new_param) < 0:
            raise RuntimeError("Given number must be positive")

    def set_data(self, data):
        length = len(data)
        if length > 99:
            raise RuntimeError("Given data contains too much information")

        self._data = str(data)
        self._length = str(len(self._data)).zfill(2)

    def set_checksum(self, checksum):
        new_checksum = str(checksum).zfill(3)

        if len(new_checksum) > 3:
            raise RuntimeError("Given checksum is too large")

        self._checksum = new_checksum

    def compute_checksum(self):
        data = "".join([self._address, self._action, self._parameternumber, self._length, self._data])

        for char in data:
            checksum = checksum + ord(char)

        return checksum % 256

    def is_valid_checksum(self):
        return self.compute_checksum() == self._checksum

    def use_checksum(self):
        self.set_checksum(self.compute_checksum())

    def apply_pre_converter(self, converter):
        self._data = converter.convert_to_raw(self._data)

    def apply_post_converter(self, converter):
        self._data = converter.convert_raw(self._data)


class AbstractMessage(object):
    def __init__(self, preconverter=None, postconverter=None):
        self._msg = RawMessage()
        if preconverter is None:
            self._preconverter = AbstractConverter()
        if postconverter is None:
            self._postconverter = AbstractConverter()

    def get_pre_converter(self):
        return self._preconverter

    def get_post_converter(self):
        return self._postconverter

    def set_pre_converter(self, converter):
        if not isinstance(converter, AbstractConverter):
            raise RuntimeError("Given converter not an instance of AbstractConverter")
        self._preconverter = converter

    def set_post_converter(self, converter):
        if not isinstance(converter, AbstractConverter):
            raise RuntimeError("Given converter not an instance of AbstractConverter")
        self._postconverter = converter

    def get_raw(self):
        return self._msg

    def set_parameter(self, param):
        self._msg.set_parameternumber(param)

    def get_data(self):
        self._msg.get_data()


class ReadMessage(AbstractMessage):
    def __init__(self, postconverter=None):
        super(ReadMessage, self).__init__(None, postconverter)
        self._init()

    def _init(self):
        self._msg.set_action(RawMessage.ACTION_READ)
        self._msg.set_data(RawMessage.QUERY_READ)


class WriteMessage(AbstractMessage):
    def __init__(self, preconverter=None, postconverter=None):
        super(WriteMessage, self).__init__(preconverter, postconverter)
        self._init()

    def _init(self):
        self._msg.set_action(RawMessage.ACTION_WRITE)

    def set_data(self, data):
        self._msg.set_data(data)


class AbstractConverter(object):
    def __init__(self):
        pass

    def convert_raw(self, data):
        return data

    def convert_to_raw(self, data):
        return data


class IntegerConverter(AbstractConverter):
    def convert_raw(self, data):
        if not len(data) == 6:
            raise RuntimeError("Given data has not the length of 6")

        return int(data)

    def convert_to_raw(self, data):
        return str(int(data)).zfill(6)


class BooleanConverter(AbstractConverter):
    def convert_raw(self, data):
        if not len(data) == 6:
            raise RuntimeError("Given data has not the length of 6")

        if data == "111111":
            return True
        elif data == "000000":
            return False
        else:
            raise RuntimeError("Unknown data for BooleanConverter '" + data + "'")

    def convert_to_raw(self, data):
        if data is True:
            return "111111"
        elif data is False:
            return "000000"
        else:
            raise RuntimeError("Unknown data (" + str(data) + ") given to BooleanConverter")


class FloatConverter(AbstractConverter):
    def convert_raw(self, data):
        if not len(data) == 6:
            raise RuntimeError("Given data has not the length of 6")

        number = int(data)
        return number / 100.0

    def convert_to_raw(self, data):
        return str(int(number * 100.0)).zfill(6)


class ExponentialConverter(AbstractConverter):
    def convert_raw(self, data):
        if not len(data) == 6:
            raise RuntimeError("Given data has not the length of 6")

        return float(data)

    def format_e(n):
        a = '%E' % n
        return (a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]).replace("+", "")

    def convert_to_raw(self, data):
        return self.format_e(str(data)).zfill(6)


class StringConverter(AbstractConverter):
    def convert_raw(self, data):
        if not len(data) == 6:
            raise RuntimeError("Given data has not the length of 6")

        return str(data)

    def convert_to_raw(self, data):
        return str(data).zfill(6)


class ShortConverter(AbstractConverter):
    def convert_raw(self, data):
        if not len(data) == 3:
            raise RuntimeError("Given data has not the length of 3")

        return int(data)

    def convert_to_raw(self, data):
        return str(int(data)).zfill(3)
