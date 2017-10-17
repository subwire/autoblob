from .arm_ivt_finder import detect_arm_ivt


@staticmethod
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
            l.debug("%s: Arch: %s, Base: %s, Entry: %s" % (det.func_name, repr(a), repr(b), repr(e)))
            arch = a if arch is None else arch
            base = b if base is None else base
            entry = e if entry is None else entry
        return arch, base, entry
    except:
        l.exception(" ")
        return None, None, None
    finally:
        stream.seek(0)


initial_detectors = [arm_ivt_finder]

