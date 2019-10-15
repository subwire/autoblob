from .arm_ivt_finder import detect_arm_ivt
from .marvell_fw_finder import detect_marvell_fw
from .cpu_rec import cpu_rec_initial
from .cubscout import cubscout_detect_arch

import logging
l = logging.getLogger("autoblob.initial")


def autodetect_initial(stream):
    """
    Pre-loading autodetection code should go here.
    All funcs operate on the file stream
    This will include:
    - What architecture is it?
    - What's the base address?
    - What's the entry point?

    :return:
    """
    arch = None
    base = None
    entry = None
    try:
        for det in initial_detectors:
            if arch is not None and base is not None and entry is not None:
                break
            a, b, e = det(stream)
            l.debug("%s: Arch: %s, Base: %s, Entry: %s" % (det.__name__, repr(a), repr(b), repr(e)))
            arch = a if arch is None else arch
            base = b if base is None else base
            entry = e if entry is None else entry
        return arch, base, entry
    except:
        l.exception(" ")
        return None, None, None
    finally:
        stream.seek(0)


initial_detectors = [detect_marvell_fw,
                     detect_arm_ivt,
                     cubscout_detect_arch,
                     cpu_rec_initial]

