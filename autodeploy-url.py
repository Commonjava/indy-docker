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


from lxml import objectify
from lxml import etree
import lxml
import httplib2
import os
import sys
import hashlib
import re
import shutil
from optparse import (OptionParser,BadOptionError,AmbiguousOptionError)

NAME='aprox'
IMAGE='buildchimp/aprox'
VERSIONFILE=os.path.join(os.environ.get('HOME'), '.autodeploy.last')

class Metadata(object):
  def __init__(self, doc, verbose):
    self.xml = doc
    self.verbose = verbose
  
  def getLatestSnapshot(self):
    timestamp = None
    build = None
    if self.xml.versioning["snapshot"] is not None and len(self.xml.versioning.snapshot) > 0 and self.xml.versioning.snapshot.getchildren() and len(self.xml.versioning.snapshot.getchildren()):
      if self.verbose is True:
        print(lxml.objectify.dump(self.xml.versioning.snapshot))
      
      timestamp = "{:.6f}".format(float(self.xml.versioning.snapshot.timestamp))
      build = self.xml.versioning.snapshot.buildNumber
      if self.verbose is True:
        print "Found timestamp: %s, build-number: %s" % (timestamp, build)
    
    version = None
    if timestamp is not None and len(self.xml.versioning.snapshotVersions) and self.xml.versioning.snapshotVersions.getchildren():
      suffix = "%s-%s" % (timestamp, build)
      if self.verbose is True:
        print "Searching for version ending with: %s" % suffix
      
      for v in self.xml.versioning.snapshotVersions['snapshotVersion']:
        if v.getchildren():
          ver = str(v.value)
          if ver.endswith(suffix):
            version = ver
            break
    
    if self.verbose is True:
      print "Returning latest snapshot: %s" % version
    return version
  
  def getLatestRelease(self):
    version = None
    if self.xml.versioning.getchildren() and len(self.xml.versioning.getchildren()):
      # TODO: If this is a FloatElement or similar, the string rendering will be WRONG.
      # See snapshot timestamp above.
      version = str(self.xml.versioning.release)
    
    if self.verbose is True:
      print "Returning latest release: %s" % version
      
    return version

def run(cmd, fail=True):
  print cmd
  ret = os.system(cmd)
  if fail and ret != 0:
    print "%s (failed with code: %s)" % (cmd, ret)
    sys.exit(ret)

def parse():
  usage = """%prog [options] <init-script> [init-options]"""
  parser = OptionParser(usage=usage)
  parser.disable_interspersed_args()
  
  parser.add_option('-i', '--image', help='The image to use when deploying (default: builchimp/aprox)')
  parser.add_option('-n', '--name', help='The container name under which to deploy AProx volume container (default: aprox)')
  parser.add_option('-r', '--release', action='store_true', help='Treat the metadata as version metadata, not snapshot metadata')
  parser.add_option('-s', '--service', help='The systemd service to manage when redeploying (default: aprox-server)')
  parser.add_option('-S', '--unsafe-ssl', action='store_true', help='Disable verification of SSL certificate (DANGEROUS)')
  parser.add_option('-u', '--url', help='URL to maven-metadata.xml to watch for updates')
  parser.add_option('-v', '--verbose', action='store_true', help='Turn on verbose feedback')
  parser.add_option('-V', '--versionfile', help='File to track the last deployed version of AProx')
  
  opts, args = parser.parse_args()
  
  if opts.verbose is True:
    print "Args: '%s'" % " ".join(args)
  init_cmd_template = " ".join(args)
  if not '{url}' in init_cmd_template:
    init_cmd_template += " --url='{url}'"
  
  return (opts, init_cmd_template)

def getMetadataVersion(opts):
  disable_ssl_validation = opts.unsafe_ssl or False
  http_client = httplib2.Http(disable_ssl_certificate_validation=disable_ssl_validation)
  headers = {
    'Accept': 'application/xml',
    'Content-Type': 'application/xml',
  }
  
  if opts.verbose is True:
    print "Parsing metadata at: %s" % opts.url
  response,content = http_client.request(opts.url, headers=headers)
  
  if response.status == 404:
    if opts.verbose is True:
      print "%s not found" % url
    sys.exit(0)
  elif response.status != 200:
    print "GET %s failed: %s" % (path, response.status)
    sys.exit(1)
  
  if opts.verbose is True:
    print "Parsing xml:\n%s" % content
  
  doc = objectify.fromstring(content)
  meta = Metadata(doc, verbose=opts.verbose)
  
  if opts.release is True:
    return meta.getLatestRelease()
  else:
    return meta.getLatestSnapshot()

def deploy(opts, init_cmd):
  print "Deploying: '%s'" % init_cmd
  
  name = opts.name or NAME
  image = opts.image or IMAGE
  
  if opts.service and os.path.exists("/bin/systemctl"):
    if opts.verbose is True:
      print "Stopping service: %s" % opts.service
    run("systemctl stop %s" % opts.service)
  
  if opts.verbose is True:
    print "Shutting down existing docker container"
  run("docker stop %s" % name, fail=False)
  run("docker rm %s" % name, fail=False)
  run("docker pull %s" % image, fail=False)
  
  if opts.verbose is True:
    print "Running init command: %s" % init_cmd
  run(init_cmd)
  
  if opts.service and os.path.exists("/bin/systemctl"):
    print "Startingservice: %s" % opts.service
    run("systemctl start %s" % opts.service)

def do(opts, init_cmd_template):
  version = getMetadataVersion(opts)
  if opts.verbose is True:
    print "Version from metadata is: %s" % version
  
  if version is None:
    if opts.verbose is True:
      print "No versions available in metadata: %s" % opts.url
    sys.exit(0)
  
  versionfile = opts.versionfile or VERSIONFILE
  if opts.verbose is True:
    print "Checking last-deployed version recorded in: %s" % versionfile

  deployed_version = None
  if os.path.exists(versionfile) and os.path.isfile(versionfile):
    with open(versionfile, "r") as vf:
      deployed_version=vf.read().replace('\n', '')
  
  if opts.verbose is True:
    print "Last deployed version is: %s" % deployed_version
  
  if deployed_version is not None and version == deployed_version:
    if opts.verbose is True:
      print "No new versions available in metadata: %s (deployed version: %s, metadata version: %s)" % (opts.url, deployed_version, version)
    sys.exit(0)
  else:
    base_url = os.path.dirname(opts.url)
    if opts.release is True:
      artifact_id = os.path.basename(base_url)
      url = "{base}/{version}/{artifact_id}-{version}-launcher.tar.gz".format(base=base_url, version=version, artifact_id=artifact_id)
    else:
      artifact_id = os.path.basename(os.path.dirname(base_url))
      url = "{base}/{artifact_id}-{version}-launcher.tar.gz".format(base=base_url, version=version, artifact_id=artifact_id)
    
    if opts.verbose is True:
      print "Deployment URL: %s" % url

    if url is not None:
      deploy(opts, init_cmd_template.format(url=url))
      with open(versionfile, "w+") as vf:
        vf.write(version)

if __name__ == '__main__':
    (opts, init_cmd_template) = parse()
    do(opts, init_cmd_template)
