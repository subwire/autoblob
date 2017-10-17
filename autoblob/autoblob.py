import backports.lzma as lzma
from cle.backends import Backend, register_backend, Blob
from cle.errors import CLEError
import os
import struct
import archinfo
import logging
import sys
from initial import autodetect_initial
l = logging.getLogger("autoblob")

__all__ = ('AutoBlob',)


class AutoBlob(Blob):
    """
    A backend that uses heuristics, hacks, magic, and unicorn horn concentrate to figure out what's in your blobs
    It will take a guess as to the base address, entry point, and architecture.
    The rest, however, is up to you!
    You can still give it a hint via the custom_arch, custom_offset, and custom_entry_point params.
    """

    def __init__(self, binary, custom_offset=None, segments=None, **kwargs):
        """
        :param custom_arch:   (required) an :class:`archinfo.Arch` for the binary blob.
        :param custom_offset: Skip this many bytes from the beginning of the file.
        :param segments:      List of tuples describing how to map data into memory. Tuples
                              are of ``(file_offset, mem_addr, size)``.

        You can't specify both ``custom_offset`` and ``segments``.
        """
        Backend.__init__(self, binary, **kwargs)
        arch, base, entry = autodetect_initial(self.binary_stream)

        if self.arch is None:
            if arch is None:
                raise CLEError("AutoBlob couldn't determine your arch.  Try specifying one.!")
            self.set_arch(arch)

        self.linked_base = kwargs.get('custom_base_addr', base)
        if self.linked_base is None:
            l.warning("AutoBlob could not detect the base address.  Assuming 0")
            self.linked_base = 0
        self.mapped_base = self.linked_base
        l.error(hex(self.mapped_base))
        self._entry = self._custom_entry_point if self._custom_entry_point is not None else entry
        if self._entry is None:
            l.warning("Autoblob could not detect the entry point, assuming 0")
            self._entry = 0

        self._min_addr = 2**64
        self._max_addr = 0 #TODO: This doesn't look right
        self.os = 'unknown' # TODO: Let this be specified somehow

        # TODO: Actually use this
        """
        if custom_offset is not None:
            if segments is not None:
                l.error("You can't specify both custom_offset and segments. Taking only the segments data")
            else:
                self.binary_stream.seek(0, 2)
                segments = [(custom_offset, 0, self.binary_stream.tell() - custom_offset)]
        else:
            if segments is not None:
                pass
            else:
                self.binary_stream.seek(0, 2)
                segments = [(0, self.linked_base, self.binary_stream.tell())]
        """
        self.binary_stream.seek(0, 2)
        segments = [(0, self.linked_base, self.binary_stream.tell())]
        for file_offset, mem_addr, size in segments:
            self._load(file_offset, mem_addr, size)

    @staticmethod
    def is_compatible(stream):
        arch, base, entry = autodetect_initial(stream)
        if arch and base and entry:
            l.info("AutoBlob thinks the arch is %s, the base address is %#08x, and the entry point is %#08x, and will"
                   " now try to load the binary.  If this is wrong, you can manually use the Blob loader backend to"
                   " specify custom parameters" % (arch, base, entry))
            return True
        return False

    def autodetect_secondary(self):
        """
        Dig up as much info about the just-loaded binary as possible.
        If we didn't find the IVT before, can we find it now?
        If we didn't pin down the exact arch revision, can we do that?
        Also, some fingerprinting on the entry function itself may yield more info.

        :return:
        """
        pass



if __name__ == '__main__':
    logging.basicConfig()
    l.setLevel(logging.DEBUG)
    with open(sys.argv[1], 'rb') as stream:
        AutoBlob.is_compatible(stream)
else:
    register_backend("autoblob", AutoBlob)
