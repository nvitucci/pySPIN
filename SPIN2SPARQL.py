import rdflib
from rdflib import RDF, RDFS, OWL

spin_owlrl = rdflib.Graph()
spin_owlrl.parse(file=open('/tmp/owlrl', 'r'), format="application/rdf+xml")

SP = rdflib.Namespace('http://spinrdf.org/sp#')
SPIN = rdflib.Namespace('http://spinrdf.org/spin#')
OWLRL = rdflib.Namespace('http://topbraid.org/spin/owlrl#')

def specEl(x, g):
    if type(x[1]) == rdflib.URIRef:
        # return x[1]
        return g.namespace_manager.normalizeUri(x[1])
    elif type(x[1]) == rdflib.BNode:
        n = [s[1] for s in g.predicate_objects(x[1])]
        if len(n):
            return '?' + n[0]
        else:
            return ':_' + x[1][-6:]
    elif type(x[1]) == rdflib.Literal:
            return '"' + x[1] + '"'

def processFilter(f, g):
    expr = [x[1] for x in spin_owlrl.predicate_objects(f) if x[0] == SP['expression']][0]

    exprType = [x[1] for x in spin_owlrl.predicate_objects(expr) if x[0] == RDF['type']][0]
    arg1 = [s[1] for x in spin_owlrl.predicate_objects(expr) for s in spin_owlrl.predicate_objects(x[1]) if x[0] == SP['arg1']][0]
    arg2 = [s[1] for x in spin_owlrl.predicate_objects(expr) for s in spin_owlrl.predicate_objects(x[1]) if x[0] == SP['arg2']][0]

    if exprType == SP['ne']:
        exprTypeSym = '!='
    else:
        exprTypeSym = '### UNKNOWN ###'

    s = 'FILTER' + ' (' + arg1.toPython() + ' ' + exprTypeSym + ' ' + arg2.toPython() + ')'

    return s

problems = []

for t in spin_owlrl:
    try:
        # if t[2] == SPIN['Template'] and t[0] == OWLRL['eq-diff3']:
        if t[2] == SPIN['Template']:
            print t[0]
    
            tmpl = [x for x in spin_owlrl.predicate_objects(t[0])]
            body = [x[1] for x in tmpl if x[0] == SPIN['body']][0]
            where = [x[1] for x in spin_owlrl.predicate_objects(body) if x[0] == SP['where']][0]
            templates = [x[1] for x in spin_owlrl.predicate_objects(body) if x[0] == SP['templates']][0]
    
            templates_list = [x for x in spin_owlrl.transitive_objects(templates, RDF['rest']) if x != RDF['nil']]
            templates_desc = [x[1] for w in templates_list for x in spin_owlrl.predicate_objects(w) if x[0] == RDF['first']]
            
            print 'CONSTRUCT {'
            
            for d in templates_desc:
                subj = None
                pred = None
                obj = None
                v = [x for x in spin_owlrl.predicate_objects(d)]
                for x in v:
                    if x[0] == SP['predicate']:
                        pred = specEl(x, spin_owlrl)
                    elif x[0] == SP['subject']:
                        subj = specEl(x, spin_owlrl)
                    elif x[0] == SP['object']:
                        obj = specEl(x, spin_owlrl)
                print '\t', subj, pred, obj
            
            print '}'
            
            where_list = [x for x in spin_owlrl.transitive_objects(where, RDF['rest']) if x != RDF['nil']]
            where_desc = [x[1] for w in where_list for x in spin_owlrl.predicate_objects(w) if x[0] == RDF['first']]
            
            print 'WHERE {'
            
            for d in where_desc:
                subj = None
                pred = None
                obj = None
                filt = None
                v = [x for x in spin_owlrl.predicate_objects(d)]
                for x in v:
                    if x[1] == SP['Filter']:
                        filt = processFilter(d, spin_owlrl)
                    else:
                        if x[0] == SP['predicate']:
                            pred = specEl(x, spin_owlrl)
                        elif x[0] == SP['subject']:
                            subj = specEl(x, spin_owlrl)
                        elif x[0] == SP['object']:
                            obj = specEl(x, spin_owlrl)
                if filt == None:
                    print '\t', subj, pred, obj, '.'
                else:
                    print '\t', filt, '.'
            
            print '}'
            print '###############'
    except:
        problems.append(t[0])

for e in problems:
    print '> DEBUG: Problems with ' + e
