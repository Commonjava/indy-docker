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
import re
from optparse import (OptionParser,BadOptionError,AmbiguousOptionError)

VERSION='@aproxVersion@'
FLAVOR='savant'
PORT=8081
URL_TEMPLATE="http://repo.maven.apache.org/maven2/org/commonjava/aprox/launch/aprox-launcher-{flavor}/{version}/aprox-launcher-{flavor}-{version}-launcher.tar.gz"
NAME='aprox'
IMAGE='buildchimp/aprox'

APROX_BINARY_RE = re.compile('aprox-launcher-.+-launcher.tar.gz')

SSHDIR=os.path.join(os.environ.get('HOME'), '.ssh')

def run(cmd, fail=True):
  print cmd
  ret = os.system(cmd)
  if fail and ret != 0:
    print "%s (failed with code: %s)" % (cmd, ret)
    sys.exit(ret)

def chcon(dir):
  run("chcon -Rt svirt_sandbox_file_t %s" % dir)

def parse():
  usage = """%prog [options]
%prog [options] - [aprox options]"""
  parser = OptionParser(usage=usage)
  parser.disable_interspersed_args()
  
  parser.add_option('-d', '--devdir', help='Directory to mount for devmode deployment (default: disabled, to use released version from URL)')
  parser.add_option('-D', '--debug-port', help="Port on which AProx JPDA connector should listen (default: disabled)")
  parser.add_option('-E', '--etc-url', help='URL from which to git-clone the etc/aprox directory (default: disabled)')
  parser.add_option('-F', '--flavor', help='The flavor of AProx binary to deploy (default: savant)')
  parser.add_option('-i', '--image', help='The image to use when deploying (default: builchimp/aprox)')
  parser.add_option('-n', '--name', help='The container name under which to deploy AProx (default: aprox)')
  parser.add_option('-p', '--port', help='Port on which AProx should listen (default: 8080)')
  parser.add_option('-q', '--quiet', action='store_false', help="Don't start with TTY")
  parser.add_option('-S', '--sshdir', help='Directory to mount for use as .ssh directory by AProx (default: disabled)')
  parser.add_option('-U', '--url', help="URL from which to download AProx (default is calculated, using 'savant' flavor)")
  parser.add_option('-V', '--version', help='The version of AProx to deploy (default: @aproxVersion@)')
  
  parser.add_option('--config', help="Volume mount for 'etc/aprox' configuration directory")
  parser.add_option('--data', help="Volume mount for state data files")
  parser.add_option('--logs', help="Volume mount for logs")
  parser.add_option('--storage', help="Volume mount for artifact storage")
  
  opts, args = parser.parse_args()
  
  return (opts,args)

def do(opts, args):
  cmd_opts = []
  
  cmd_opts.append("--name=%s" % (opts.name or NAME))
  
  if opts.quiet is False:
    cmd_opts.append("-d")
  else:
    cmd_opts.append("-t")
  
  url=opts.url or URL_TEMPLATE.format(flavor=(opts.flavor or FLAVOR), version=(opts.version or VERSION))
  cmd_opts.append("-e APROX_BINARY_URL=%s" % url)
  cmd_opts.append("-p %s:8081" % (opts.port or PORT))
  
  if opts.debug_port:
    cmd_opts.append("-p %s:8000" % opts.debug_port)
  
  if opts.config:
    cmd_opts.append("-v %s:/etc/aprox" % opts.config)
  
  if opts.data:
    cmd_opts.append("-v %s:/var/lib/aprox/data" % opts.data)
  
  if opts.logs:
    cmd_opts.append("-v %s:/var/log/aprox" % opts.logs)
  
  if opts.storage:
    cmd_opts.append("-v %s:/var/lib/aprox/storage" % opts.storage)
  
  if opts.sshdir:
    chcon(opts.sshdir)
    cmd_opts.append("-v %s:/tmp/ssh" % opts.sshdir)
  
  if opts.devdir:
    found=False
    for file in os.listdir(opts.devdir):
      if APROX_BINARY_RE.match(file):
        found=True
        break
    
    if not found:
      print "No deployable tarball found in: %s for dev-mode execution. Aborting." % opts.devdir
      sys.exit(1)
    
    chcon(opts.devdir)
    cmd_opts.append("-e APROX_DEV=true")
    cmd_opts.append("-v %s:/tmp/aprox" % opts.devdir)
  
  if opts.etc_url:
    cmd_opts.append("-e APROX_ETC_URL=%s" % opts.etc_url)
  
  if len(args) > 0:
    cmd_opts.append("-e APROX_OPTS='%s'" % " ".join(args))
  
  cmd_opts.append(opts.image or IMAGE)

  run("docker run %s" % " ".join(cmd_opts))

if __name__ == '__main__':
    opts, args = parse()
    do(opts, args)
