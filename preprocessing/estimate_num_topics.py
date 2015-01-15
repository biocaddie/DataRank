import sys;
import re;
import collections
from DBUtil import *
from numpy import mean
import pylab as P

if __name__ == '__main__':
    try:
        param={'src':'/home/arya/bigdata/pmc/mesh.db', 'pipeline':'mesh'}
        param['dst']=param['src']
        with dbConnector(param) as db_conn:
            mesh=db_conn.getAll()
            
            n= map(lambda x: len(eval(x[0])), mesh)
            P.Figure()
            nm, bins, patches = P.hist(n, 50,  histtype='stepfilled')
            P.title('Number of MeSH headings per Paper on PMC (mean={})'.format(mean(n)))
            print mean(n)
            P.savefig("num_mesh.png")
            P.show()
            
            
    except (IOError,ValueError) as e:
        print str(e)
        sys.exit(1)
    print 'Done!'
        