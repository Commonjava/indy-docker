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

FROM centos

MAINTAINER John Casey <jdcasey@commonjava.org>

RUN yum -y update
RUN yum -y install wget git tar which curl tree java-1.8.0-openjdk-devel

VOLUME /var/lib/aprox/storage /var/lib/aprox/data /var/log/aprox /etc/aprox /tmp/aprox /tmp/ssh-config

EXPOSE 8080
EXPOSE 8081
EXPOSE 8000

ADD start-aprox.py /usr/local/bin/start-aprox.py
RUN chmod +x /usr/local/bin/start-aprox.py

CMD "/usr/local/bin/start-aprox.py"
