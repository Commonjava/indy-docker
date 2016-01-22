#!/bin/bash
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

python -c 'import httplib2' > /dev/null || echo "You must have python-httplib2 installed"

DIR=$(dirname $(dirname $(realpath $0)))
echo "Initializing Indy directories in $DIR"

pushd $DIR
mkdir ssh data etc logs storage
ssh-keygen -C "$(basename $DIR)@$(hostname)" -N '' -f ssh/id_rsa
popd

echo "$DIR now contains the following subdirectories:"
ls -1 $DIR

echo "Now, do the following:"
echo "1. Copy and change $DIR/ENV.prototype:"
echo ""
echo "  cp $DIR/ENV.prototype $DIR/ENV"
echo ""
echo "2. Adjust it to your desired deployment options"
echo "3. Execute the folowing:"
echo ""
echo "  cp $DIR/indy-docker/systemd/indy-server-novols.service /etc/systemd/system/indy-server-<name>.service"
echo "  vi /etc/systemd/system/indy-server-<name>.service  #change 'indy' to your indy container's name from ENV"
echo "  systemctl enable indy-server-<name>"
echo ""
echo "4. Deploy Indy by calling:"
echo ""
echo "  $DIR/scripts/init-indy --version=<initial-indy-version>"
echo ""
