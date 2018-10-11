import logging
import sys
import re
from archinfo import arch_from_id, all_arches

from collections import defaultdict
l = logging.getLogger("autoblob.cubscout")


def cubscout_detect_arch(stream, cookiesize=1):
    """
    CubScout: A direct port of BoyScout to AutoBlob.

    This does dead-simple prolog matching.
    """
    # TODO: A lot of things need the whole binary's string.  Let's make this efficient
    # Retrieve the binary string of main binary
    data = stream.read()
    stream.seek(0)
    votes = defaultdict(int)
    for arch in all_arches:
        regexes = set()
        for ins_regex in set(arch.function_prologs).union(arch.function_epilogs):
            r = re.compile(ins_regex)
            regexes.add(r)

        for regex in regexes:
            # Match them!
            for mo in regex.finditer(data):
                position = mo.start() 
                if position % arch.instruction_alignment == 0:
                    votes[(arch.name, arch.memory_endness)] += 1

        l.debug("%s %s hits %d times", arch.name, arch.memory_endness,
                votes[(arch.name, arch.memory_endness)])

    arch_name, endianness, hits = sorted([(k[0], k[1], v) for k, v in votes.iteritems()], key=lambda x: x[2], reverse=True)[0]
    if hits < cookiesize * 2:
        # this cannot possibly be code
        l.debug("CubScout thinks this is Data")
        return (None, None, None)

    l.debug("The architecture should be %s with %s", arch_name, endianness)
    arch = arch_from_id(arch_name, endianness)
    return (arch, None, None)

if __name__ == '__main__':
    logging.basicConfig()
    l.setLevel(logging.DEBUG)
    with open(sys.argv[1], 'rb') as stream:
        print(cubscout_detect_arch(stream))

