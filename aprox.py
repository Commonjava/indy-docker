#
# Copyright (C) 2015 John Casey (jdcasey@commonjava.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import re

VERSION='0.19.2'
FLAVOR='savant'
PORT=8080
PROXY_PORT=8081
DEBUG_PORT=8000
URL_TEMPLATE="http://repo.maven.apache.org/maven2/org/commonjava/aprox/launch/aprox-launcher-{flavor}/{version}/aprox-launcher-{flavor}-{version}-launcher.tar.gz"

SERVER_NAME='aprox'
SERVER_IMAGE='buildchimp/aprox'

VOLS_NAME='aprox-volumes'
VOLS_IMAGE='buildchimp/aprox-volumes'

APROX_BINARY_RE = re.compile('aprox-launcher-.+-launcher.tar.gz')

SSHDIR=os.path.join(os.environ.get('HOME'), '.ssh')

