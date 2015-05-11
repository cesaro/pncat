
def test1 () :
    n = Net (True)
    n.read (sys.stdin, 'grml')
    n.write (sys.stdout, 'grml')

def test2 () :
    n = Net (True)
    n.read (sys.stdin, 'pt1')
    n.stubbornify ()
    #n.write (sys.stdout, 'pt1')

def test3 () :

    # two transitions in conflict
    n = Net (True)
    p0 = n.place_add ('p0', 1)
    p1 = n.place_add ('p1')
    p2 = n.place_add ('p2')

    t1 = n.trans_add ('t1')
    t2 = n.trans_add ('t2')

    t1.pre_add (p0)
    t1.post_add (p1)

    t2.pre_add (p0)
    t2.post_add (p2)

    print "Before stubbornifying !!"
    n.write (sys.stdout, 'pt1')
    n.write (sys.stdout, 'dot')
    n.stubbornify ()
    print "After stubbornifying !!"
    n.write (sys.stdout, 'dot')
    n.cont2plain ()
    n.write (sys.stdout, 'pt1')

    f = open ('./out.ll_net', 'w')
    n.write (f, 'pep')

def test4 () :

    # three transitions in conflict
    n = Net (True)
    p0 = n.place_add ('p0', 1)
    p1 = n.place_add ('p1')
    p2 = n.place_add ('p2')
    p3 = n.place_add ('p3')

    t1 = n.trans_add ('t1')
    t2 = n.trans_add ('t2')
    t3 = n.trans_add ('t3')

    t1.pre_add (p0)
    t1.post_add (p1)

    t2.pre_add (p0)
    t2.post_add (p2)

    t3.pre_add (p0)
    t3.post_add (p3)

    print "Before stubbornifying !!"
    n.write (sys.stdout, 'dot')
    n.stubbornify ()
    print "After stubbornifying !!"
    n.write (sys.stdout, 'dot')

    f = open ('./out.ll_net', 'w')
    n.write (f, 'pep')

def test5 () :

    # two transitions in conflict, and return
    n = Net (True)
    p0 = n.place_add ('p0', 1)
    p1 = n.place_add ('p1')

    t1 = n.trans_add ('t1')
    t2 = n.trans_add ('t2')
    t3 = n.trans_add ('t3')

    t1.pre_add (p0)
    t1.post_add (p1)

    t2.pre_add (p0)
    t2.post_add (p1)

    t3.pre_add (p1)
    t3.post_add (p0)

    n.write (sys.stdout, 'dot')
    n.stubbornify ()
    n.write (sys.stdout, 'dot')

    f = open ('./out.ll_net', 'w')
    n.write (f, 'pep')

def test6 () :

    n = Net (True)
    n.read (sys.stdin, 'pt1')
    n.stubbornify ()
    n.cont2plain ()
    n.write (sys.stdout, 'pep')

# vi:ts=4:sw=4:et:
