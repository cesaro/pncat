#!/usr/bin/env python

if __name__ == '__main__' :

    import pncat
    import sys
    m = pncat.Main ()
    m.main ()
    sys.exit (0)

    try :
        import sys
        import pncat
        m = pncat.Main ()
        m.main ()
        #pncat.test.test19 ()
    except KeyboardInterrupt :
        print 'pncat: interrupted'
        sys.exit (1)
    except Exception as e :
        print 'pncat: error: %s' % str (e)
        sys.exit (1)
    sys.exit (0)

# vi:ts=4:sw=4:et:
