import os
import mmap
import psutil

from eyefi import locate_eyefi_mount

# Constants
EYEFI_BUF_SIZE = 1024 * 2  # Adjust as necessary
PATHNAME_MAX = 4096

# Debug level
eyefi_debug_level = 1


def debug_printf(level, message, *args):
    """
    Print debug messages if the specified debug level is met.

    Args:
      level (int): The minimum debug level required to print the message.
      message (str): The message format string.
      *args: Arguments for the format string.

    Returns:
      None
    """
    if eyefi_debug_level >= level:
        print(message % args)


def eyefi_printf(message, *args):
    """
    Print a formatted message.

    Args:
      message (str): The message format string.
      *args: Arguments for the format string.

    Returns:
      None
    """
    print(message % args)


def eyefi_file_name(file):
    """
    Map file enumeration to its corresponding file name.

    Args:
      file (str): The file enumeration name.

    Returns:
      str: The corresponding file name.
    """
    mapping = {
        "REQC": "reqc",
        "REQM": "reqm",
        "RSPC": "rspc",
        "RSPM": "rspm",
        "RDIR": ""
    }
    return mapping.get(file, None)


def eyefi_file_on(file, mnt):
    """
    Get the full path of the EyeFi file located on the mount point.

    Args:
      file (str): The file enumeration name.
      mnt (str): The mount point path.

    Returns:
      str: The full path of the file.
    """
    filename = eyefi_file_name(file)
    if not filename:
        return None
    full_path = os.path.join(mnt, "EyeFi", filename)
    debug_printf(4, "eyefile nr: %s on '%s' is: '%s'", file, mnt, full_path)
    return full_path


class CardSeqNum:
    """
    A class to manage the card sequence number.
    """

    def __init__(self):
        """
        Initialize the sequence number.
        """
        self.seq = 0


eyefi_seq = CardSeqNum()

# Buffer alignment for O_DIRECT writes (Linux-specific)
unaligned_buf = bytearray(EYEFI_BUF_SIZE * 2)
eyefi_buf = None


def align_buf():
    """
    Align the buffer for optimal file operations.

    Returns:
      None
    """
    global eyefi_buf
    addr = (id(unaligned_buf) + EYEFI_BUF_SIZE - 1) & ~(EYEFI_BUF_SIZE - 1)
    eyefi_buf = memoryview(unaligned_buf)[addr:]
    debug_printf(4, "buf: %p", eyefi_buf)


def init_card():
    """
    Initialize the EyeFi card by aligning the buffer,
    zeroing card files, and updating the sequence number.

    Returns:
      None
    """
    global eyefi_buf
    if eyefi_buf:
        return

    debug_printf(2, "Initializing card...")
    mnt = locate_eyefi_mount()
    if not mnt:
        return

    align_buf()
    zero_card_files()
    eyefi_seq.seq = read_seq_from("RSPC")
    if eyefi_seq.seq == 0:
        eyefi_seq.seq = 0x1234
    eyefi_seq.seq += 1
    debug_printf(2, "Done initializing card...")
    debug_printf(3, "seq was: %04x", eyefi_seq.seq)


def zero_card_files():
    """
    Zero out the EyeFi card files.

    Returns:
      None
    """
    zbuf = bytearray(EYEFI_BUF_SIZE)
    write_to("RSPM", zbuf, EYEFI_BUF_SIZE)
    read_from("REQM")
    read_from("REQC")
    read_from("RSPM")


def read_seq_from(file):
    """
    Read the sequence number from a file.

    Args:
      file (str): The file enumeration name.

    Returns:
      int: The sequence number.
    """
    read_from(file)
    return int.from_bytes(eyefi_buf[:4], "little")


def read_from(file_path):
  """
  Read data from a file and populate the buffer.

  Args:
    file_path (str): The path to the file.

  Returns:
    bytes: The data read from the file.
  """
  try:
    with open(file_path, "rb") as f:
      mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
      data = mmapped_file[:EYEFI_BUF_SIZE]
      mmapped_file.close()
      return data
  except FileNotFoundError:
    print(f"File not found: {file_path}")
    return None
  except Exception as e:
    print(f"Error reading from file {file_path}: {e}")
    return None

def write_to(file_path, data):
  """
  Write data to a file.

  Args:
    file_path (str): The path to the file.
    data (bytes): The data to write.

  Returns:
    None
  """
  try:
    with open(file_path, "wb") as f:
      f.write(data)
      f.flush()
      os.fsync(f.fileno())
  except Exception as e:
    print(f"Error writing to file {file_path}: {e}")

def majflts():
    """
    Get the number of major page faults for the current process.

    Returns:
      int: The number of major page faults.
    """
    process = psutil.Process()
    min_flt = process.num_page_faults()
    return min_flt


def mmap_file(file_path, length):
    """
    Map a file into memory for reading.

    Args:
      file_path (str): The path to the file.
      length (int): The length of the file to map.

    Returns:
      mmap.mmap: The memory-mapped file object.
    """
    with open(file_path, "r+b") as f:
        mmapped_file = mmap.mmap(f.fileno(), length, access=mmap.ACCESS_READ)
        return mmapped_file


if __name__ == "__main__":
    init_card()
