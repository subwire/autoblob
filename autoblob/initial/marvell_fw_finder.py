import logging
import struct
import archinfo
l = logging.getLogger("autoblob")

def detect_marvell_fw(stream):
    """

    :param stream:
    :type stream: file
    :return:
    """
    min_arm_sp = 0x20000000
    max_arm_sp = 0x20100000

    try:
        stream.seek(0)
        header = stream.read(0xc0)
        if not b"MRVL" in header:
            return None, None, None
        maybe_entry = struct.unpack('<I', header[0x10:0x14])[0]
        maybe_fw_file_offs = struct.unpack('<I', header[0x18:0x1c])[0]
        if not (0 < maybe_fw_file_offs < 0x1000):
            return None, None, None
        # First dword of the firmware is the SP
        stream.seek(maybe_fw_file_offs)
        maybe_sp = struct.unpack("<I", stream.read(4))[0]
        if not (min_arm_sp < maybe_sp <= max_arm_sp):
             return None, None, None
        l.debug("Detected Marvell FW header")
        maybe_arch = archinfo.ArchARMCortexM(endness=archinfo.Endness.LE)
        l.debug("Found possible Little-Endian ARM IVT with initial SP %#08x" % maybe_sp)
        l.debug("Reset vector at %#08x" % maybe_entry)
        maybe_base = maybe_entry & 0xffff0000  # A complete guess
        l.debug("Guessing base address at %#08x" % maybe_base)
        return maybe_arch, maybe_base, maybe_entry
    except Exception:
        l.exception("")
        return None, None, None
    finally:
        stream.seek(0)
