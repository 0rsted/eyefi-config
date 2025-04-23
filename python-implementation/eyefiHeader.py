# Constants
EYEFI_BUF_SIZE = 16384
ESSID_LEN = 32
MAC_BYTES = 6
WPA_KEY_BYTES = 32
WEP_KEY_BYTES = 13

# Debug level
eyefi_debug_level = 0


def debug_printf(level, *args):
    """
    Print debug messages if the specified debug level is less than or equal to the global `eyefi_debug_level`.

    Args:
      level (int): The debug level for the message.
      *args: The message content to print.
    """
    if level <= eyefi_debug_level:
        print(*args)


def swap_bytes(src):
    """
    Swap the byte order of a 32-bit integer.

    Args:
      src (int): The 32-bit integer to swap.

    Returns:
      int: The byte-swapped integer.
    """
    dest = 0
    dest |= (src & 0xff000000) >> 24
    dest |= (src & 0x00ff0000) >> 8
    dest |= (src & 0x0000ff00) << 8
    dest |= (src & 0x000000ff) << 24
    return dest


def le_to_host32(n):
    """
    Convert a 32-bit little-endian integer to host byte order.

    Args:
      n (int): The 32-bit integer.

    Returns:
      int: The integer in host byte order.
    """
    return n


def be_to_host32(n):
    """
    Convert a 32-bit big-endian integer to host byte order.

    Args:
      n (int): The 32-bit integer.

    Returns:
      int: The integer in host byte order.
    """
    return swap_bytes(n)


def host_to_be32(n):
    """
    Convert a 32-bit integer in host byte order to big-endian.

    Args:
      n (int): The 32-bit integer.

    Returns:
      int: The integer in big-endian byte order.
    """
    return swap_bytes(n)


class PascalString:
    """
    Represents a Pascal-style string with a length byte followed by content.
    """

    def __init__(self, length, value):
        """
        Initialize a PascalString.

        Args:
          length (int): The length of the string.
          value (str): The string content.
        """
        self.length = length
        self.value = value


class CardSeqNum:
    """
    Represents a card sequence number.
    """

    def __init__(self, seq):
        """
        Initialize a CardSeqNum.

        Args:
          seq (int): The sequence number.
        """
        self.seq = seq


class VarByteResponse:
    """
    Represents a response with variable bytes.
    """

    def __init__(self, response_len, bytes_):
        """
        Initialize a VarByteResponse.

        Args:
          response_len (int): The length of the response.
          bytes_ (bytes): The response bytes.
        """
        self.response_len = response_len
        self.bytes = bytes_


class CardInfoReq:
    """
    Represents a card information request.
    """

    def __init__(self, o, subcommand):
        """
        Initialize a CardInfoReq.

        Args:
          o (int): The operation code.
          subcommand (int): The subcommand code.
        """
        self.o = o
        self.subcommand = subcommand


class CardConfigCmd:
    """
    Represents a card configuration command.
    """

    def __init__(self, O, subcommand, arg=None):
        """
        Initialize a CardConfigCmd.

        Args:
          O (int): The operation code.
          subcommand (int): The subcommand code.
          arg (VarByteResponse, optional): The argument for the command.
        """
        self.O = O
        self.subcommand = subcommand
        self.arg = arg


class CardInfoRspKey:
    """
    Represents a card information response key.
    """

    def __init__(self, key):
        """
        Initialize a CardInfoRspKey.

        Args:
          key (PascalString): The response key.
        """
        self.key = key


class CardFirmwareInfo:
    """
    Represents card firmware information.
    """

    def __init__(self, info):
        """
        Initialize a CardFirmwareInfo.

        Args:
          info (PascalString): The firmware information.
        """
        self.info = info


class MacAddress:
    """
    Represents a MAC address.
    """

    def __init__(self, length, mac):
        """
        Initialize a MacAddress.

        Args:
          length (int): The length of the MAC address.
          mac (bytes): The MAC address bytes.
        """
        self.length = length
        self.mac = mac


class CardInfoApiUrl:
    """
    Represents a card API URL.
    """

    def __init__(self, key):
        """
        Initialize a CardInfoApiUrl.

        Args:
          key (PascalString): The API URL key.
        """
        self.key = key


class CardInfoLogLen:
    """
    Represents the length of a log in card information.
    """

    def __init__(self, log_len, val):
        """
        Initialize a CardInfoLogLen.

        Args:
          log_len (int): The length of the log.
          val (int): The log value.
        """
        self.log_len = log_len
        self.val = val

# Enumerations


class CardInfoSubcommand:
    """
    Enum for card information subcommands.
    """
    MAC_ADDRESS = 1
    FIRMWARE_INFO = 2
    CARD_KEY = 3
    API_URL = 4
    UNKNOWN_5 = 5
    UNKNOWN_6 = 6
    LOG_LEN = 7
    WLAN_DISABLE = 10
    UPLOAD_PENDING = 11
    HOTSPOT_ENABLE = 12
    CONNECTED_TO = 13
    UPLOAD_STATUS = 14
    UNKNOWN_15 = 15
    TRANSFER_MODE = 17
    ENDLESS = 27
    DIRECT_MODE_SSID = 0x22
    DIRECT_MODE_PASS = 0x23
    DIRECT_WAIT_FOR_CONNECTION = 0x24
    DIRECT_WAIT_AFTER_TRANSFER = 0x25
    UPLOAD_KEY = 0xfd
    UNKNOWN_ff = 0xff


class TransferMode:
    """
    Enum for transfer modes.
    """
    AUTO_TRANSFER = 0
    SELECTIVE_TRANSFER = 1
    SELECTIVE_SHARE = 2


class NetType:
    """
    Enum for network types.
    """
    NET_UNSECURED = 0
    NET_WEP = 1
    NET_WPA = 2
    NET_WPA2 = 3


class NetPasswordType:
    """
    Enum for network password types.
    """
    NET_PASSWORD_ASCII = 0
    NET_PASSWORD_RAW = 1
