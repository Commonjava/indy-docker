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


import os
import sys
from optparse import OptionParser
from aprox import *

def run(cmd, fail=True):
  print cmd
  ret = os.system(cmd)
  if fail and ret != 0:
    print "%s (failed with code: %s)" % (cmd, ret)
    sys.exit(ret)

def parse():
  usage = """%prog [options]"""
  parser = OptionParser(usage=usage)
  parser.disable_interspersed_args()
  
  parser.add_option('-i', '--image', help="The image to use when deploying (default: %s)" % VOLS_IMAGE)
  parser.add_option('-n', '--name', help="The container name under which to deploy AProx volume container (default: %s)" % VOLS_NAME)
  
  opts, args = parser.parse_args()
  
  return (opts)

def do(opts):
  name = VOLS_NAME
  if opts.name is not None:
    name = opts.name
  
  image = VOLS_IMAGE
  if opts.image is not None:
    image = opts.image
  
  run("docker run -d --name='%s' %s" % (name, image))

if __name__ == '__main__':
    opts = parse()
    do(opts)
