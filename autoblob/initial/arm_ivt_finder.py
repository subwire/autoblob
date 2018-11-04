import logging
import struct
import archinfo
l = logging.getLogger("autoblob")

def detect_arm_ivt(stream):
    """

    :param stream:
    :type stream: file
    :return:
    """
    min_arm_sp = 0x20000000
    max_arm_sp = 0x20100000

    # TODO: We're just looking at the front for now
    try:
        maybe_sp = stream.read(4)
        maybe_le_sp = struct.unpack('<I', maybe_sp)[0]
        maybe_be_sp = struct.unpack(">I", maybe_sp)[0]
        if min_arm_sp < maybe_le_sp < max_arm_sp:
            maybe_arch = archinfo.ArchARMCortexM(endness=archinfo.Endness.LE)
            l.debug("Found possible Little-Endian ARM IVT with initial SP %#08x" % maybe_le_sp)
            maybe_entry = struct.unpack('<I', stream.read(4))[0]
            l.debug("Reset vector at %#08x" % maybe_entry)
            maybe_base = maybe_entry & 0xffff0000  # A complete guess
            l.debug("Guessing base address at %#08x" % maybe_base)
            return maybe_arch, maybe_base, maybe_entry
        elif min_arm_sp < maybe_be_sp < max_arm_sp:
            maybe_arch = archinfo.ArchARM(endness=archinfo.Endness.BE)
            l.debug("Found possible Big-Endian ARM IVT with initial SP %#08x" % maybe_be_sp)
            maybe_entry = struct.unpack('>I', stream.read(4))[0]
            l.debug("Reset vector at %#08x" % maybe_entry)
            maybe_base = maybe_entry & 0xffff0000  # A complete guess
            l.debug("Guessing base address at %#08x" % maybe_base)
            return maybe_arch, maybe_base, maybe_entry
        else:
            # Nope
            return (None, None, None)
    except:
        l.exception("Something died")
        return (None, None, None)
    finally:
        stream.seek(0)
