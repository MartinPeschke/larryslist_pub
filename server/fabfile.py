from fabric.api import run
from fabric.context_managers import cd
from fabric.contrib import files
from fabric.operations import put

SYSTEM_PACKAGES = ["sudo", "vim", "less"
                    , "build-essential"
                    , "libjpeg62-dev"
                    , "libxml2-dev"
                    , "libxslt1-dev"
                    , "unzip"
                    , "libpng12-dev"
                    , "libfreetype6-dev"
                    , "libpcre3-dev"
                    , "libpcre3-dev"
                    , "libssl-dev"
                    , "apache2-utils"
                    , "lib32bz2-dev"
                    , "curl"
                    , "libreadline6"
                    , "libreadline6-dev"
                    , "libmhash2"
                    , "libmhash-dev"
                    , "libmcrypt4"
                    , "libtomcrypt-dev"
                    , "libssl-dev"
                    , "git"]

VERSIONS = {
    "PYTHON":"2.7.5"
    , "NGINX":"1.4.1"
}

def set_resolv():
    run("""
echo "# nameserver config
nameserver 8.8.8.8
nameserver 213.133.100.100
nameserver 213.133.98.98
nameserver 213.133.99.99" > /etc/resolv.conf
    """)


def set_host(name):
    run("cp /etc/hosts /etc/hosts.bak")
    run("""
sed -e 's/Debian-.*-64-minimal/{host}/g' /etc/hosts.bak > /etc/hosts
echo Welcome to {host}> /etc/motd
echo {host} > /etc/hostname
    """.format(host=name))


def update():
    run("mkdir /server/{src,www} -p")
    run("apt-get update")
    run("apt-get install -y {}".format(" ".join(SYSTEM_PACKAGES)))

def adduser():
    name = "developer"
    run("adduser {}".format(name))
    run("sudo su - {}".format(name))
    run("mkdir .ssh")
    run("ssh-keygen -t rsa -b 4096")
    run("cp .ssh/id_rsa.pub .ssh/authorized_keys")

def set_wwwuser():
    run("mkdir /home/www-data")
    run("chown www-data: /home/www-data")
    run("usermod -d /home/www-data -s /bin/bash www-data")
    run("sudo su - {}".format("www-data"))
    run("mkdir .ssh")
    run("ssh-keygen -t rsa -b 4096")
    run("cp .ssh/id_rsa.pub .ssh/authorized_keys")



###fucked, somehow dont work
def firewall():
    put("./iptables.rules", "/etc/iptables.rules")
    put("./iptables", "/etc/network/if-up.d/iptables")
    run("iptables-restore < /etc/iptables.rules")

def add_python():
    with cd("/server/src"):
        run("wget http://www.python.org/ftp/python/2.7.5/Python-{}.tar.bz2".format(VERSIONS['PYTHON']))
        run("tar xfvj Python-{}.tar.bz2".format(VERSIONS['PYTHON']))
    with cd("/server/src/Python-{}".format(VERSIONS['PYTHON'])):
        run("./configure && make && make install")
        run("wget http://peak.telecommunity.com/dist/ez_setup.py")
        run("python ez_setup.py")
        run("easy_install virtualenv Cython ctypes")

def add_nginx():
    with cd("/server/src"):
        run("wget http://nginx.org/download/nginx-{}.tar.gz".format(VERSIONS['NGINX']))
        run("tar xfv nginx-{}.tar.gz".format(VERSIONS['NGINX']))
    with cd("/server/src/nginx-{}".format(VERSIONS['NGINX'])):
        run("./configure \
            --group=www-data\
            --user=www-data\
            --with-http_ssl_module\
            --prefix=/server/nginx/{}\
            --conf-path=/server/nginx/etc/nginx.conf\
            --error-log-path=/server/nginx/logs/error.log\
            --pid-path=/server/nginx/run/nginx.pid\
            --lock-path=/server/nginx/run/nginx.lock\
            --with-http_gzip_static_module && make && make install".format(VERSIONS['NGINX']))
    files.upload_template("nginx.initd.tmpl", "/etc/init.d/nginx", {'NGINX_VERSION': VERSIONS['NGINX']})
    run("chmod +x /etc/init.d/nginx")
    run("update-rc.d nginx defaults")


def setup(host):
    set_resolv()
    set_host(host)