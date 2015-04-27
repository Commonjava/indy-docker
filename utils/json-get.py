#!/usr/bin/python
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


import json
import sys

def dump(data):
    if type(data) is dict:
        print json.dumps(data, indent=2)
    else:
        print data

if len(sys.argv) < 2:
    print "No file specified. Usage: %s <file> [path]" % sys.argv[0]
    sys.exit(1)

file = sys.argv[1]
path = None

if len(sys.argv) > 2:
    path = sys.argv[2]

with open(file, 'r') as json_file:
    data = json.load(json_file)

if path is None:
    dump(data)
else:
    parts = path.split('|')
    here=data
    for part in parts:
      if len(part) < 1:
        continue
      here = here[part]

    dump(here)

