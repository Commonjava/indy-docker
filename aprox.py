import os
import re

VERSION='0.19.2'
FLAVOR='savant'
PORT=8081
URL_TEMPLATE="http://repo.maven.apache.org/maven2/org/commonjava/aprox/launch/aprox-launcher-{flavor}/{version}/aprox-launcher-{flavor}-{version}-launcher.tar.gz"

SERVER_NAME='aprox'
SERVER_IMAGE='buildchimp/aprox'

VOLS_NAME='aprox-volumes'
VOLS_IMAGE='buildchimp/aprox-volumes'

APROX_BINARY_RE = re.compile('aprox-launcher-.+-launcher.tar.gz')

SSHDIR=os.path.join(os.environ.get('HOME'), '.ssh')

