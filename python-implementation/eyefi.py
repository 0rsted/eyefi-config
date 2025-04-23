import os
import platform
import ctypes
from ctypes import wintypes

# Constants
EYEFI_BUF_SIZE = 1024 * 2
PATHNAME_MAX = 4096
LINEBUFSZ = 1024
EYEFI_VOLUME_ID = "AA52-6922"

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

def atoo(o):
  """
  Convert an octal character to its integer value.

  Args:
    o (str): A single character representing an octal digit.

  Returns:
    int: The integer value of the octal character, or -1 if invalid.
  """
  if '0' <= o <= '7':
    return int(o, 8)
  return -1

def octal_esc_to_chr(input_str):
  """
  Convert an octal escape sequence to a character.

  Args:
    input_str (str): The input string containing the octal escape sequence.

  Returns:
    int: The character value, or -1 if invalid.
  """
  if input_str[0] != '\\' or len(input_str) < 4:
    return -1
  ret = 0
  for i in range(1, 4):
    tmp = atoo(input_str[i])
    if tmp < 0:
      return tmp
    ret = (ret << 3) + tmp
  return ret

def replace_escapes(string):
  """
  Replace octal escape sequences in a string with their corresponding characters.

  Args:
    string (str): The input string containing octal escape sequences.

  Returns:
    str: The string with escape sequences replaced.
  """
  output = []
  i = 0
  while i < len(string):
    esc = octal_esc_to_chr(string[i:])
    if esc >= 0:
      output.append(chr(esc))
      i += 4  # Skip the escape sequence
    else:
      output.append(string[i])
      i += 1
  return ''.join(output)

def fd_flush(fd):
  """
  Flush the file descriptor to ensure data is written to disk.

  Args:
    fd (int): The file descriptor.

  Returns:
    int: Always returns 0.
  """
  os.fsync(fd)
  return 0

def basename(path):
  """
  Extract the base name of a file path.

  Args:
    path (str): The file path.

  Returns:
    str: The base name of the path.
  """
  return os.path.basename(path)

def dev_has_eyefi_vol_id(dev):
  """
  Check if the device has the EyeFi volume ID.

  Args:
    dev (str): The device path.

  Returns:
    bool: True if the device has the EyeFi volume ID, False otherwise.
  """
  if platform.system() == "Windows":
    volume_name_buffer = ctypes.create_unicode_buffer(PATHNAME_MAX)
    serial_number = wintypes.DWORD()
    max_component_length = wintypes.DWORD()
    file_system_flags = wintypes.DWORD()

    result = ctypes.windll.kernel32.GetVolumeInformationW(
      dev,
      volume_name_buffer,
      ctypes.sizeof(volume_name_buffer),
      ctypes.byref(serial_number),
      ctypes.byref(max_component_length),
      ctypes.byref(file_system_flags),
      None,
      0
    )
    return result and basename(volume_name_buffer.value) == EYEFI_VOLUME_ID

  return False

def zero_file(file, mnt):
  """
  Create a file on the mount point and fill it with zeros.

  Args:
    file (str): The file name.
    mnt (str): The mount point path.

  Returns:
    int: 0 on success, or the error code on failure.
  """
  fname = os.path.join(mnt, "EyeFi", file)
  debug_printf(1, "Creating control file: '%s'", fname)
  try:
    with open(fname, "wb") as f:
      f.write(b'\x00' * EYEFI_BUF_SIZE)
      fd_flush(f.fileno())
  except OSError as e:
    debug_printf(1, "Error creating control file: %s", e)
    return e.errno
  return 0

def locate_eyefi_mount():
  """
  Locate the EyeFi card mount point.

  Returns:
    str: The path to the mount point, or None if not found.
  """
  if platform.system() == "Windows":
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
      drive_path = f"{drive}:\\"
      if os.path.exists(drive_path) and dev_has_eyefi_vol_id(drive_path):
        return drive_path
  return None