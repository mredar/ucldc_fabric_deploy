import os
from fabric.api import settings, env, run
from fabric.api import get, cd


'''To provision our basic solr box:
    First get pkgsrc installed so we don't have to be root to install
    install git?
    install monit
    no pkg for solr -- wget and unpack
    setup monitrc
'''

def solr_0():
    env.hosts = ['50.19.127.252']
    env.user = 'ec2-user'
    env.user = 'ec2-user'
    env.key_filename = os.path.join(os.environ.get('HOME', os.path.expanduser('~')), '.ssh/UCLDC_keypair_0.pem')

def nutch_dev():
    env.hosts = ['54.243.192.165']
    env.user = 'ec2-user'
    env.key_filename = os.path.join(os.environ.get('HOME', os.path.expanduser('~')), '.ssh/pdf-test-key-mer.pem')

def host_type():
    run('uname -s')

def monit_summary():
    run('monit -c ~/.monitrc summary')

def whoami():
    run('whoami')

def id():
    run('id')

def update_host():
    result = run('which yum', warn_only=True)
    if result.succeeded:
        run('sudo yum -y update')

def get_git():
    '''Check if git is installed. If not, use yum to install.
    Git is on the suse linux boxes, so this should just run on 
    ec2 boxes.
    '''
    result = run('which git', warn_only=True)
    if result.failed:
        run('sudo yum -y install git')

def get_cvs():
    '''Check if cvs installe. Install with yum if not installled. Again suse
    boxes should already have it.
    '''
    result = run('which cvs', warn_only=True)
    if result.failed:
        run('sudo yum -y install cvs')

def get_gcc():
    result = run('which gcc', warn_only=True)
    if result.failed:
        run('sudo yum -y install gcc')

def install_appstrap():
    '''Install the appstrap and package src to make other installs easy'''
    result = run('which bmake', warn_only=True)
    if result.failed:
        run('git clone https://github.com/mredar/appstrap.git')
        run('cat $HOME/appstrap/bashrc_add >> $HOME/.bashrc')
        run("ssh -o StrictHostKeyChecking=no anoncvs@anoncvs.netbsd.org") #add anoncvs host key to .ssh/known_hosts
        run('$HOME/appstrap/pmake') #Installs pkgsrc
        run('ssh-keygen -R anoncvs.netbsd.org') #remove key from .ssh/known_hosts
	run('. $HOME/appstrap/setenv.sh')

def appstrap_pgp():
    #TODO: CHECK THE SUMS AGAINST PACKAGE DOWNLOAD IN SOLR
    #THIS WAS TAKING TOO LONG TO FIGURE OUT
    '''Install pgp to verify downloaded packages'''
    #idea license on pycrypto places no restrictions on code use
    #see: https://github.com/dlitz/pycrypto/tree/master/LEGAL/copy
    run("echo \"ACCEPTABLE_LICENSES+= idea-license\" >> $HOME/pkg/etc/mk.conf")
    run("$HOME/appstrap/pmake security/pgp5")

def install_solr():
    '''Need to have the solr src stored somewhere. For now will point to a 
    known apache mirror at sonic.net (since I'm a customer)
    '''
    run('mkdir -p $HOME/local/src')
    with cd('$HOME/local/src'):
        run('wget http://mirrors.sonic.net/apache/lucene/solr/4.3.0/solr-4.3.0.tgz')
        run('wget http://www.us.apache.org/dist/lucene/solr/4.3.0/KEYS')
        run('wget http://www.us.apache.org/dist/lucene/solr/4.3.0/solr-4.3.0.tgz.asc')
        #run('pgp -ka KEYS')
        #run('pgp solr-4.3.0.tgz.asc')
        run('tar -xvf solr-4.3.0.tgz')

def install_tomcat():
    #TO CURE: "No usable termcap library found on the system"
    result = run('which yum', warn_only=True)
    if result.succeeded: #AWS
        run('sudo yum -y install python-paramiko')
        run('sudo yum -y install ncurses-devel')

    run("echo \"ACCEPTABLE_LICENSES+= sun-jre6-license\" >> $HOME/pkg/etc/mk.conf")
    run("$HOME/appstrap/pmake www/apache-tomcat7")


def deploy():
    update_host()
    get_gcc()
    get_cvs()
    get_git()
    install_appstrap()
    #appstrap_pgp()
    #install_tomcat()
    install_solr()
