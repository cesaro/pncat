
import xml.etree.ElementTree

class Formula :
    # types of nodes in the formula tree 
    TRUE         = 0
    FALSE        = 1
    IS_FIREABLE  = 2
    DEADLOCK     = 18
    LEQ          = 3
    NOT          = 4
    OR           = 5
    AND          = 6
    EX           = 7
    EU           = 8
    EG           = 9
    # ..............
    TOKEN_COUNT  = 10
    INT_CONST    = 11
    A            = 12
    E            = 13
    G            = 14
    F            = 15
    X            = 16
    U            = 17

    def __init__ (self, op = None, sub1 = None, sub2 = None) :
        self.op = op
        self.sub1 = sub1
        self.sub2 = sub2
        self.atom_identifiers = None
        self.atom_int = None
        self.ident = None

    def rewrite (self) :
        # EF f          = E (True U f)
        # AX f          = not EX not f
        # AG f          = not E (True U not f)
        # AF f          = not EG not f
        # A (f U g)     = not E ((not g) U (not f and not g)) and (not EG not g)
        if self.op == Formula.E :
            if self.sub1.op == Formula.X :
                self.op = Formula.EX
                self.sub1 = self.sub1.sub1
                self.sub1.rewrite ()
            elif self.sub1.op == Formula.U :
                f = self.sub1.sub1
                g = self.sub1.sub2
                f.rewrite ()
                g.rewrite ()
                self.op = Formula.EU
                self.sub1 = f
                self.sub2 = g
            elif self.sub1.op == Formula.G :
                self.op = Formula.EG
                self.sub1 = self.sub1.sub1
                self.sub1.rewrite ()
            elif self.sub1.op == Formula.F :
                # EF f = E (True U f)
                f = self.sub1.sub1
                f.rewrite ()
                self.op = Formula.EU
                self.sub1 = Formula (Formula.TRUE)
                self.sub2 = f
            else :
                raise Exception, '"%s": cannot handle this subformula' % self
        elif self.op == Formula.A :
            if self.sub1.op == Formula.X :
                # AX f = not EX not f
                f = self.sub1.sub1
                f.rewrite ()
                not_f = Formula (Formula.NOT, f)
                self.op = Formula.NOT
                self.sub1 = Formula (Formula.EX, not_f)
            elif self.sub1.op == Formula.U :
                # A (f U g) = not E ((not g) U (not f and not g)) and (not EG not g)
                f = self.sub1.sub1
                g = self.sub1.sub2
                f.rewrite ()
                g.rewrite ()
                not_f = Formula (Formula.NOT, f)
                not_g = Formula (Formula.NOT, g)
                not_f_and_not_g = Formula (Formula.AND, not_f, not_g)
                not_eu = Formula (Formula.NOT, Formula (Formula.EU, not_g, not_f_and_not_g))
                not_eg_not_g = Formula (Formula.NOT, Formula (Formula.EG, not_g))
                self.op = Formula.AND
                self.sub1 = not_eu
                self.sub2 = not_eg_not_g
            elif self.sub1.op == Formula.G :
                # AG f = not E (True U not f)
                f = self.sub1.sub1
                f.rewrite ()
                not_f = Formula (Formula.NOT, f)
                self.op = Formula.NOT
                self.sub1 = Formula (Formula.EU, Formula (Formula.TRUE), not_f)
            elif self.sub1.op == Formula.F :
                # AF f = not EG not f
                f = self.sub1.sub1
                f.rewrite ()
                not_f = Formula (Formula.NOT, f)
                self.op = Formula.NOT
                self.sub1 = Formula (Formula.EG, not_f)
            else :
                raise Exception, '"%s": cannot handle this subformula' % self
        elif self.op == Formula.G or \
                self.op == Formula.F or \
                self.op == Formula.X or \
                self.op == Formula.U :
            raise Exception, '"%s": this seems to be an LTL formula that we cannot handle' % self
        elif self.op == Formula.TOKEN_COUNT or \
                self.op == Formula.INT_CONST :
            raise Exception, '"%s": this seems to be an integer expression that we cannot handle' % self
        elif self.op == Formula.NOT or \
                self.op == Formula.EX or \
                self.op == Formula.EG :
            self.sub1.rewrite ()
        elif self.op == Formula.OR or \
                self.op == Formula.AND or \
                self.op == Formula.EU :
            self.sub1.rewrite ()
            self.sub2.rewrite ()
        elif self.op == Formula.TRUE or \
                self.op == Formula.FALSE or \
                self.op == Formula.IS_FIREABLE or \
                self.op == Formula.LEQ :
            return
        else :
            raise Exception, '"%s": Formula::rewrite, internal error' % self

    def simplify (self) :
        if self.sub1 != None : self.sub1.simplify ()
        if self.sub2 != None : self.sub2.simplify ()

        # not (not f) = f
        if self.op == Formula.NOT and \
                self.sub1.op == Formula.NOT :
            self.__copy_fields (self.sub1.sub1)

        # not True = False
        elif self.op == Formula.NOT and \
                self.sub1.op == Formula.TRUE :
            self.op = Formula.FALSE

        # not False = True
        elif self.op == Formula.NOT and \
                self.sub1.op == Formula.FALSE :
            self.op = Formula.TRUE

        # f and f = f
        elif self.op == Formula.AND and \
                self.sub1.__easy_syntax_eq (self.sub2) :
            self.__copy_fields (self.sub1)

        # f and not f = False
        elif self.op == Formula.AND and \
                self.sub2.op == Formula.NOT and \
                self.sub1.__easy_syntax_eq (self.sub2.sub1) :
            self.op = Formula.FALSE

        # not f and f = False
        elif self.op == Formula.AND and \
                self.sub1.op == Formula.NOT and \
                self.sub2.__easy_syntax_eq (self.sub1.sub1) :
            self.op = Formula.FALSE

        # f or f = True
        elif self.op == Formula.OR and \
                self.sub1.__easy_syntax_eq (self.sub2) :
            self.op = Formula.TRUE

        # True or f = True
        elif self.op == Formula.OR and \
                self.sub1.op == Formula.TRUE :
            self.op = Formula.TRUE

        # f or True = True
        elif self.op == Formula.OR and \
                self.sub2.op == Formula.TRUE :
            self.op = Formula.TRUE

        # True and f = f
        elif self.op == Formula.AND and \
                self.sub1.op == Formula.TRUE :
            self.__copy_fields (self.sub2)

        # f and True = f
        elif self.op == Formula.AND and \
                self.sub2.op == Formula.TRUE :
            self.__copy_fields (self.sub1)

        # (not f) and (not g) = not (f or g)
        elif self.op == Formula.AND and \
                self.sub1.op == Formula.NOT and \
                self.sub2.op == Formula.NOT :
            self.op = Formula.NOT
            new_f = Formula (Formula.OR, self.sub1.sub1, self.sub2.sub1)
            self.sub1 = new_f

        # (not f) or (not g) = not (f and g)
        elif self.op == Formula.OR and \
                self.sub1.op == Formula.NOT and \
                self.sub2.op == Formula.NOT :
            self.op = Formula.NOT
            new_f = Formula (Formula.AND, self.sub1.sub1, self.sub2.sub1)
            self.sub1 = new_f

        # EX False = False
        # EG False = False
        # E (f U False) = False
        # EX True = True
        # EG True = True
        # E (f U True) = True
        elif (self.op == Formula.EX or self.op == Formula.EG) and \
                self.sub1.op == Formula.FALSE :
            self.op = Formula.FALSE
        elif self.op == Formula.EU and \
                self.sub2.op == Formula.FALSE :
            self.op = Formula.FALSE
        elif (self.op == Formula.EX or self.op == Formula.EG) and \
                self.sub1.op == Formula.TRUE :
            self.op = Formula.TRUE
        elif self.op == Formula.EU and \
                self.sub2.op == Formula.TRUE :
            self.op = Formula.TRUE

        # there are more ...
        # we could even identify common subformulas (!!)
        else :
            return

    def __copy_fields (self, g) :
        self.op = g.op
        self.sub1 = g.sub1
        self.sub2 = g.sub2
        self.atom_int = g.atom_int
        self.atom_identifiers = g.atom_identifiers
        self.ident = g.ident

    def __easy_syntax_eq (self, g) :
        if self.op != g.op : return False
        if self.op == Formula.IS_FIREABLE or self.op == Formula.TOKEN_COUNT :
            return set (self.atom_identifiers) == set (g.atom_identifiers)
        elif self.op == Formula.INT_CONST :
            return self.atom_int == g.atom_int
        elif self.op == Formula.TRUE or \
                self.op == Formula.FALSE :
                return True
        elif self.op == Formula.NOT or \
                self.op == Formula.EX or \
                self.op == Formula.EG or \
                self.op == Formula.A or \
                self.op == Formula.E or \
                self.op == Formula.G or \
                self.op == Formula.F or \
                self.op == Formula.X :
            return self.sub1.__easy_syntax_eq (g.sub1)
        elif self.op == Formula.OR or \
                self.op == Formula.LEQ or \
                self.op == Formula.AND or \
                self.op == Formula.EU or \
                self.op == Formula.U :
            return self.sub1.__easy_syntax_eq (g.sub1) and \
                    self.sub2.__easy_syntax_eq (g.sub2)
        else :
            raise Exception, 'Formula::__easy_syntax_eq, internal error'

    def __str__ (self) :
        if self.op == Formula.TRUE :
            return "(true)"
        elif self.op == Formula.FALSE :
            return "(false)"
        elif self.op == Formula.DEADLOCK :
            return "(deadlock)"
        elif self.op == Formula.IS_FIREABLE :
            s = "(is-firable "
            if len (self.atom_identifiers) > 5 :
                s += ", ".join (repr (t) for t in self.atom_identifiers[:5])
                s += ", ... %d more" % (len (self.atom_identifiers) - 5)
            else :
                s += ", ".join (repr (t) for t in self.atom_identifiers)
            return s + ")"
        elif self.op == Formula.LEQ :
            return "(leq " + str (self.sub1) + " " + str (self.sub2) + ")"
        elif self.op == Formula.NOT :
            return "(not " + str (self.sub1) + ")"
        elif self.op == Formula.OR :
            return "(or " + str (self.sub1) + " " + str (self.sub2) + ")"
        elif self.op == Formula.AND :
            return "(and " + str (self.sub1) + " " + str (self.sub2) + ")"
        elif self.op == Formula.EX :
            return "(EX " + str (self.sub1) + ")"
        elif self.op == Formula.EU :
            return "(EU " + str (self.sub1) + " " + str (self.sub2) + ")"
        elif self.op == Formula.EG :
            return "(EG " + str (self.sub1) + ")"
        elif self.op == Formula.TOKEN_COUNT :
            s = "(token-count "
            if len (self.atom_identifiers) > 5 :
                s += ", ".join (repr (p) for p in self.atom_identifiers[:5])
                s += ", ... %d more" % (len (self.atom_identifiers) - 5)
            else :
                s += ", ".join (repr (p) for p in self.atom_identifiers)
            return s + ")"
        elif self.op == Formula.INT_CONST :
            return str (self.atom_int)
        elif self.op == Formula.A :
            return "(A " + str (self.sub1) + ")"
        elif self.op == Formula.E :
            return "(E " + str (self.sub1) + ")"
        elif self.op == Formula.G :
            return "(G " + str (self.sub1) + ")"
        elif self.op == Formula.F :
            return "(F " + str (self.sub1) + ")"
        elif self.op == Formula.X :
            return "(X " + str (self.sub1) + ")"
        elif self.op == Formula.U :
            return "(U " + str (self.sub1) + " " + str (self.sub2) + ")"
        else :
            raise Exception, 'Formula::__str__, internal error'

    def write (self, f, fmt='cunf') :
        if isinstance (f, basestring) : f = open (f, 'w')
        if fmt == 'cunf' : return self.__write_cunf (f)

    def __write_cunf (self, f) :
        # <f>    ::= EF <f1> | AG <f1>
        # <f1>   ::= NOT <f1> | {AND,OR} <f1> <f1> | <atom>
        # <atom> ::= is-fireable ... | deadlock

        # negate={Y,N} id formula

        negate = False
        if self.op == Formula.A and self.sub1.op == Formula.G :
            negate = True
        elif self.op == Formula.E and self.sub1.op == Formula.F :
            pass
        else :
            raise Exception, "Formula is not of the form EF or AG"

        # if negate is true, we need to introduce a double negation ;)
        # as AG f = ! EF (! f)
        f.write ('# negate=%s id=%s txt=%s\n' %
            ('Y' if negate else 'N', self.ident, str(self)[:40]))
        if negate :
            f.write ('! ')
        self.sub1.sub1.__write_cunf_rec (f)
        f.write (';\n')

    def __write_cunf_rec (self, f) :
        # expect NOT, AND, OR, DEADLOCK, IS_FIREABLE
        if self.op == Formula.NOT :
            f.write ('(! ')
            self.sub1.__write_cunf_rec (f)
            f.write (')')
        elif self.op == Formula.AND :
            f.write ('(')
            self.sub1.__write_cunf_rec (f)
            f.write (' && ')
            self.sub2.__write_cunf_rec (f)
            f.write (')')
        elif self.op == Formula.OR :
            f.write ('(')
            self.sub1.__write_cunf_rec (f)
            f.write (' || ')
            self.sub2.__write_cunf_rec (f)
            f.write (')')
        elif self.op == Formula.DEADLOCK :
            f.write ('deadlock')
        elif self.op == Formula.IS_FIREABLE :
            f.write ('(')
            for t in self.atom_identifiers[:-1] :
                f.write ('"%s" || ' % str (t))
            f.write ('"%s")' % str (self.atom_identifiers[-1]))
        else :
            raise Exception, \
                "Operator %d is not accepted in Cunf's syntax" % self.op

    @staticmethod
    def read (path, net=None, fmt='mcc15') :
        if fmt == 'mcc15' : return Formula.__read_mcc15 (path, net)
        raise Exception, "'%s': unknown input format" % fmt

    @staticmethod
    def __read_mcc15 (path, net) :
        print "pncat: loading XML in memory (ElementTree.parse)"
        xmltree = xml.etree.ElementTree.parse (path)
        root = xmltree.getroot ()
        result = []
        for child in root :
            result.append (Formula.__read_mcc15_parse_property (child, net))
        return result

    @staticmethod
    def __read_mcc15_parse_property (xmltree, net) :
        f = Formula.__read_mcc15_parse_formula (net, xmltree.find ('{http://mcc.lip6.fr/}formula')[0])
        f.ident = xmltree.find ('{http://mcc.lip6.fr/}id').text
        return f

    @staticmethod
    def __read_mcc15_parse_formula (net, xmltree) :
        f = Formula ()
        #print 'pncat: parsing xml', xmltree
        if xmltree.tag == '{http://mcc.lip6.fr/}all-paths' :
            f.op = Formula.A
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
        elif xmltree.tag == '{http://mcc.lip6.fr/}exists-path' :
            f.op = Formula.E
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
        elif xmltree.tag == '{http://mcc.lip6.fr/}globally' :
            f.op = Formula.G
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
        elif xmltree.tag == '{http://mcc.lip6.fr/}finally' :
            f.op = Formula.F
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
        elif xmltree.tag == '{http://mcc.lip6.fr/}next' :
            f.op = Formula.X
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
        elif xmltree.tag == '{http://mcc.lip6.fr/}until' :
            f.op = Formula.U
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0][0])
            f.sub2 = Formula.__read_mcc15_parse_formula (net, xmltree[1][0])
        elif xmltree.tag == '{http://mcc.lip6.fr/}negation' :
            f.op = Formula.NOT
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
        elif xmltree.tag == '{http://mcc.lip6.fr/}conjunction' :
            f.op = Formula.AND
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
            f.sub2 = Formula.__read_mcc15_parse_formula (net, xmltree[1])
        elif xmltree.tag == '{http://mcc.lip6.fr/}disjunction' :
            f.op = Formula.OR
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
            f.sub2 = Formula.__read_mcc15_parse_formula (net, xmltree[1])
        elif xmltree.tag == '{http://mcc.lip6.fr/}integer-le' :
            f.op = Formula.LEQ
            f.sub1 = Formula.__read_mcc15_parse_formula (net, xmltree[0])
            f.sub2 = Formula.__read_mcc15_parse_formula (net, xmltree[1])
        elif xmltree.tag == '{http://mcc.lip6.fr/}is-fireable' :
            f.op = Formula.IS_FIREABLE
            f.atom_identifiers = []
            if len (xmltree) > 1000 :
                print "pncat: is-fireable XML tag with %d transition ids (!!)" % len (xmltree)
            nr = 0
            for xmlsub in xmltree :
                if net is None :
                    t = xmlsub.text
                else :
                    t = net.trans_lookup_id (xmlsub.text)
                    if t == None :
                        raise Exception, \
                                "'%s': transition id not found in this net" % xmlsub.text
                f.atom_identifiers.append (t)
                nr += 1
                if nr % 10000 == 0 :
                    print "pncat: loaded %d transition ids" % nr
        elif xmltree.tag == '{http://mcc.lip6.fr/}integer-constant' :
            f.op = Formula.INT_CONST
            f.atom_int = int (xmltree.text)
        elif xmltree.tag == '{http://mcc.lip6.fr/}tokens-count' :
            f.op = Formula.TOKEN_COUNT
            f.atom_identifiers = []
            if len (xmltree) > 1000 :
                print "pncat: tokens-count XML tag with %d transition ids (!!)" % len (xmltree)
            nr = 0
            for xmlsub in xmltree :
                if net is None :
                    p = xmlsub.text
                else :
                    p = net.place_lookup_id (xmlsub.text)
                    if p == None :
                        raise Exception, \
                                "'%s': place id not found in this net" % xmlsub.text
                f.atom_identifiers.append (p)
                nr += 1
                if nr % 10000 == 0 :
                    print "pncat: loaded %d place ids" % nr
        elif xmltree.tag == '{http://mcc.lip6.fr/}deadlock' :
            f.op = Formula.DEADLOCK
        else :
            raise Exception, \
                "'%s': unable to handle XML tag, probably I cannot handle this formula" % xmltree.tag
        return f

