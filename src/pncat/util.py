
def error_missing_package (exception) :
    print 'ERROR!'
    print 'It seems that your python installation is missing some package.'
    print 'This tool requires, among others, the following packages:'
    print '* resource, networkx, argparse, random, z3, ptnet, pes'
    print 'The runtime reported the following error:\n\n', str (exception), '\n'
    print 'You might want to use "easy_install --user PACKAGE"'
    print ''
    import sys
    sys.exit (1)

try :
    import os
except ImportError, e:
    error_missing_package (e)

def output_dict (f, d, prefix='pncat: ') :
    n = max ([len (k) for k in d])
    l = list (d)
    l.sort ()
    for k in l :
        output_pair (f, k, d[k], n, prefix)

def output_pair (f, k, v, n, prefix='', fmt='%s') :
    f.write (prefix + ('%-*s : ' + fmt + '\n') % (n, k, v))

def avg_iter (it) :
    s = 0
    i = 0
    for x in it :
        s += x
        i += 1
    return float (s) / i

def long_list (ls, maxlen=5) :
    ls = list (ls)
    le = len (ls)
    if maxlen < 0 : maxlen = le
    s = "["
    s += ", ".join (repr (x) for x in ls[:maxlen])
    if le > maxlen :
        s += ", ... %d more]" % (le - maxlen)
    else :
        s += "]"
    return s

# vi:ts=4:sw=4:et:
