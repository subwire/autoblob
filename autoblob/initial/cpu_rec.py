#from cpu_rec import TrainingData, FileAnalysis
import logging
import sys

l = logging.getLogger("autoblob.cpu_rec")

paths = ["../../lib/cpu_rec/cpu_rec.py"]

def find_cpu_rec():
    for filename in paths:
        try:
            path, name = os.path.split(os.path.abspath(filename))
            name, ext = os.path.splitext(name)
            f, filename, data = imp.find_module(name, [path])
            mod = imp.load_module(name, f, filename, data)
            print 'After: %s in sys.modules ==' % name, name in sys.modules
            return mod
        except:
            pass
    else:
        l.warning("cpu_rec not found!")
        return None

def cpu_rec_initial(stream):
    cpu_rec = find_cpu_rec()
    if not cpu_rec:
        return (None, None, None)
    l.debug("cpu_rec analysis starting...")
    # TODO: Don't do that
    l.debug("Loading file...")
    data = stream.read()
    stream.seek(0)

    l.debug("Loading training data...")
    t = cpu_rec.TrainingData()
    t.read_corpus()
    p = cpu_rec.FileAnalysis(t)
    l.debug('Beginning full-file analysis...')
    d = cpu_rec.TrainingData.unpack_file(data)
    res, r2, r3 = p.deduce(d)
    l.debug('%-15s%-10s' % ('full(%#x)' % len(d), res))
    l.debug("                   %s", r2[:4])
    l.debug("                   %s", r3[:4])
    l.debug("Looking for a text section, if possible...")
    # Text section, if possible
    try:
        d_txt = cpu_rec.TrainingData.extract_section(d, section='text')
        if len(d) != len(d_txt):
            res, r2, r3 = p.deduce(d_txt)
            l.debug('%-15s%-10s' % ('text(%#x)' % len(d_txt), res))
        else:
            l.debug('%-15s%-10s' % ('', ''))
    except:
        l.exception("Text extraction analysis failed.  Probably elfesteem is messed up.")
    l.debug("Performing sliding window analysis...")
    _, cpu, sz, cnt, _ = p.sliding_window(d)
    l.debug('%-20s%-10s' % ('chunk(%#x;%s)'%(2*sz*cnt,cnt), cpu))
    if res and cpu and res == cpu:
        return (res.lower(), None, None)
    if cpu:
        return (cpu.lower(), None, None)
    if res:
        return (res.lower(), None, None)
    return (None, None, None)

if __name__ == '__main__':
    l.setLevel(logging.DEBUG)
    with open(sys.argv[1], 'rb') as f:
        print cpu_rec_initial(f)[0]
        
