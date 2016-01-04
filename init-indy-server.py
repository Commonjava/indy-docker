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
from indy import *

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
%prog [options] - [indy options]"""
  parser = OptionParser(usage=usage)
  parser.disable_interspersed_args()
  
  parser.add_option('-d', '--devdir', help='Directory to mount for devmode deployment (default: disabled, to use released version from URL)')
  parser.add_option('--dns', help="Pass in a DNS server to the running container", action="append")
  parser.add_option('-D', '--debug-port', help="Port on which Indy JPDA connector should listen (default: disabled)")
  parser.add_option('-e', '--env', help="Set an environment variable in the running container", action="append")
  parser.add_option('-E', '--etc-url', help='URL from which to git-clone the etc/indy directory (default: disabled)')
  parser.add_option('-F', '--flavor', help="The flavor of Indy binary to deploy (default: %s)" % FLAVOR)
  parser.add_option('-i', '--image', help="The image to use when deploying (default: %s)" % SERVER_IMAGE)
  parser.add_option('-n', '--name', help="The container name under which to deploy Indy (default: %s)" % SERVER_NAME)
  parser.add_option('-p', '--port', help="Port on which Indy should listen (default: %s)" % PORT)
  parser.add_option('-P', '--proxy-port', help="Port on which Indy's httprox add-on should listen (default: disabled)")
  parser.add_option('-q', '--quiet', action='store_false', help="Don't start with TTY")
  parser.add_option('-S', '--sshdir', help='Directory to mount for use as .ssh directory by Indy (default: disabled)')
  parser.add_option('-U', '--url', help="URL from which to download Indy (default is calculated, using '%s' flavor)" % FLAVOR)
  parser.add_option('-v', '--vols', help="Docker container name from which to mount volumes (default: %s)" % VOLS_NAME)
  parser.add_option('-V', '--version', help="The version of Indy to deploy (default: %s)" % VERSION)
  
  opts, args = parser.parse_args()
  
  return (opts,args)

def do(opts, args):
  cmd_opts = []
  
  cmd_opts.append("--name=%s" % (opts.name or SERVER_NAME))
  cmd_opts.append("--volumes-from=%s" % (opts.vols or VOLS_NAME))
  
  if opts.quiet is False:
    cmd_opts.append("-d")
  else:
    cmd_opts.append("-t")
  
  url=opts.url or URL_TEMPLATE.format(flavor=(opts.flavor or FLAVOR), version=(opts.version or VERSION))
  cmd_opts.append("-e INDY_BINARY_URL=%s" % url)
  
  if opts.env:
    for envar in opts.env:
      cmd_opts.append( "-e %s" % envar)

  if opts.dns:
    for dnsserver in opts.dns:
      cmd_opts.append( "--dns=%s" % dnsserver)
  
  cmd_opts.append("-p %s:%s" % (opts.port or PORT, PORT))
  
  if opts.proxy_port:
    cmd_opts.append("-p %s:%s" % (opts.proxy_port, PROXY_PORT))
  
  if opts.debug_port:
    cmd_opts.append("-p %s:%s" % (opts.debug_port, DEBUG_PORT))
  
  if opts.sshdir:
    chcon(opts.sshdir)
    cmd_opts.append("-v %s:/tmp/ssh-config" % opts.sshdir)
  
  if opts.devdir:
    found=False
    for file in os.listdir(opts.devdir):
      if INDY_BINARY_RE.match(file):
        found=True
        break
    
    if not found:
      print "No deployable tarball found in: %s for dev-mode execution. Aborting." % opts.devdir
      sys.exit(1)
    
    chcon(opts.devdir)
    cmd_opts.append("-e INDY_DEV=true")
    cmd_opts.append("-v %s:/tmp/indy" % opts.devdir)
  
  if opts.etc_url:
    cmd_opts.append("-e INDY_ETC_URL=%s" % opts.etc_url)
  
  if len(args) > 0:
    cmd_opts.append("-e INDY_OPTS='%s'" % " ".join(args))
  
  cmd_opts.append(opts.image or SERVER_IMAGE)

  run("docker run %s" % " ".join(cmd_opts))

if __name__ == '__main__':
    opts, args = parse()
    do(opts, args)
