import sys, os

rootdir = os.getcwd()
while 'Projects' in rootdir:
    rootdir = os.path.dirname(rootdir)
sys.path.append(os.path.join(rootdir, 'Projects', 'credentials'))
dirname = os.path.join(rootdir, 'Projects', 'cragcrunch')
from sqlcfg import host, user, passwd

projectroot = '/Projects/cragcrunch/'
fulldir = os.path.join(rootdir, 'Projects/cragcrunch')
redfeatfile = os.path.join(fulldir, 'data', 'learnedfeatures.pkl')

# database parameters
class Cfg():
    def __init__(self, projectroot, host, user, passwd, dbname, charset='utf8', use_unicode=0, clobber=False):
        self.projectroot = projectroot
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.charset = charset
        self.use_unicode = use_unicode
        self.clobber = clobber


DBCFG = Cfg(projectroot, host, user, passwd, dbname='climbdb_prepped')

#vars in caps will be read by app.config
ROOTDIR=fulldir
APPNAME='CragCrunch'