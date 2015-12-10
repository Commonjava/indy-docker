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
from urllib2 import urlopen
# import tarfile
import shutil
import fnmatch

def run(cmd, fail_message='Error running command', fail=True):
  cmd += " 2>&1"
  print cmd
  ret = os.system(cmd)
  if fail is True and ret != 0:
    print "%s (failed with code: %s)" % (fail_message, ret)
    sys.exit(ret)



def runIn(cmd, workdir, fail_message='Error running command', fail=True):
  cmd += " 2>&1"
  olddir = os.getcwd()
  os.chdir(workdir)
  
  print "In: %s, executing: %s" % (workdir, cmd)
  
  ret = os.system(cmd)
  if fail is True and ret != 0:
    print "%s (failed with code: %s)" % (fail_message, ret)
    sys.exit(ret)
  
  os.chdir(olddir)



def move_and_link(src, target, replaceIfExists=False):
  srcParent = os.path.dirname(src)
  if not os.path.isdir(srcParent):
    print "mkdir -p %s" % srcParent
    os.makedirs(srcParent)
  
  if not os.path.isdir(target):
    print "mkdir -p %s" % target
    os.makedirs(target)
  
  if os.path.isdir(src):
    for f in os.listdir(src):
      targetFile = os.path.join(target, f)
      srcFile = os.path.join(src, f)
      print "%s => %s" % (srcFile, targetFile)
      if os.path.exists(targetFile):
        if not replaceIfExists:
          print "Target dir exists: %s. NOT replacing." % targetFile
          continue
        else:
          print "Target dir exists: %s. Replacing." % targetFile
        
        if os.path.isdir(targetFile):
          print "rm -r %s" % targetFile
          shutil.rmtree(targetFile)
        else:
          print "rm %s" % targetFile
          os.remove(targetFile)
      
      if os.path.isdir(srcFile):
        print "cp -r %s %s" % (srcFile, targetFile)
        shutil.copytree(srcFile, targetFile)
      else:
        print "cp %s %s" % (srcFile, targetFile)
        shutil.copy(srcFile, targetFile)
    
    print "rm -r %s" % src
    shutil.rmtree(src)
  
  print "ln -s %s %s" % (target, src)
  os.symlink(target, src)




# Envar for reading development binary volume mount point
APROX_DEV_VOL = '/tmp/indy'
SSH_CONFIG_VOL = '/tmp/ssh-config'
APROX_DEV_BINARIES_PATTERN='indy*-launcher.tar.gz'


# Envars that can be set using -e from 'docker run' command.
APROX_VERSION_ENVAR='APROX_VERSION'
APROX_FLAVOR_ENVAR='APROX_FLAVOR'
APROX_URL_ENVAR = 'APROX_BINARY_URL'
APROX_ETC_URL_ENVAR = 'APROX_ETC_URL'
APROX_OPTS_ENVAR = 'APROX_OPTS'
APROX_DEVMODE_ENVAR = 'APROX_DEV'


# Defaults
DEF_APROX_FLAVOR='savant'

DEF_APROX_BINARY_URL_FORMAT = 'http://repo.maven.apache.org/maven2/org/commonjava/indy/launch/indy-launcher-{flavor}/{version}/indy-launcher-{flavor}-{version}-launcher.tar.gz'


# locations for expanded indy binary
APROX_DIR = '/opt/indy'
BOOT_PROPS = 'boot.properties'
APROX_BIN = os.path.join(APROX_DIR, 'bin')
APROX_ETC = os.path.join(APROX_DIR, 'etc/indy')
APROX_STORAGE = os.path.join(APROX_DIR, 'var/lib/indy/storage')
APROX_DATA = os.path.join(APROX_DIR, 'var/lib/indy/data')
APROX_LOGS = os.path.join(APROX_DIR, 'var/log/indy')


# locations on global fs
ETC_APROX = '/etc/indy'
VAR_APROX = '/var/lib/indy'
VAR_STORAGE = os.path.join(VAR_APROX, 'storage')
VAR_DATA = os.path.join(VAR_APROX, 'data')
LOGS = '/var/log/indy'


# if true, attempt to use indy distro tarball or directory from attached volume
devmode = os.environ.get(APROX_DEVMODE_ENVAR)

# indy release to use
version=os.environ.get(APROX_VERSION_ENVAR)

# currently one of: rest-min, easyprox, savant
flavor=os.environ.get(APROX_FLAVOR_ENVAR) or DEF_APROX_FLAVOR

# URL for indy distro tarball to download and expand
indyBinaryUrl = os.environ.get(APROX_URL_ENVAR) or DEF_APROX_BINARY_URL_FORMAT.format(version=version, flavor=flavor)

# Git location supplying /opt/indy/etc/indy
indyEtcUrl = os.environ.get(APROX_ETC_URL_ENVAR)

# command-line options for indy
opts = os.environ.get(APROX_OPTS_ENVAR) or ''

print "Read environment:\n  devmode: %s\n  indy version: %s\n  indy flavor: %s\n  indy binary URL: %s\n  indy etc Git URL: %s\n  indy cli opts: %s" % (devmode, version, flavor, indyBinaryUrl, indyEtcUrl, opts)

if os.path.isdir(SSH_CONFIG_VOL) and len(os.listdir(SSH_CONFIG_VOL)) > 0:
  print "Importing SSH configurations from volume: %s" % SSH_CONFIG_VOL
  run("cp -vrf %s /root/.ssh" % SSH_CONFIG_VOL)
  run("chmod -v 700 /root/.ssh", fail=False)
  run("chmod -v 600 /root/.ssh/*", fail=False)


if os.path.isdir(APROX_DIR) is False:
  parentDir = os.path.dirname(APROX_DIR)
  if os.path.isdir(parentDir) is False:
    os.makedirs(parentDir)
  
  if devmode is not None:
    unpacked=False
    for file in os.listdir(APROX_DEV_VOL):
      if fnmatch.fnmatch(file, APROX_DEV_BINARIES_PATTERN):
        devTarball = os.path.join(APROX_DEV_VOL, file)
        print "Unpacking development binary of Indy: %s" % devTarball
        run('tar -zxvf %s -C /opt' % devTarball)
        unpacked=True
        break
    if unpacked is False:
      if not os.path.exists(os.path.join(APROX_DEV_VOL, 'bin/indy.sh')):
        print "Development volume %s exists but doesn't appear to contain expanded Indy (can't find 'bin/indy.sh'). Ignoring." % APROX_DEV_VOL
      else:
        print "Using expanded Indy deployment, in development volume: %s" % APROX_DEV_VOL
        shutil.copytree(APROX_DEV_VOL, APROX_DIR)
  else:
      print 'Downloading: %s' % indyBinaryUrl
      
      download = urlopen(indyBinaryUrl)
      with open('/tmp/indy.tar.gz', 'wb') as f:
        f.write(download.read())
      run('ls -alh /tmp/')
      run('tar -zxvf /tmp/indy.tar.gz -C /opt')
    #  with tarfile.open('/tmp/indy.tar.gz') as tar:
    #    tar.extractall(parentDir)
    
  if indyEtcUrl is not None:
    print "Cloning: %s" % indyEtcUrl
    shutil.rmtree(APROX_ETC)
    run("git clone --verbose --progress %s %s 2>&1" % (indyEtcUrl, APROX_ETC), "Failed to checkout indy/etc from: %s" % indyEtcUrl)
  
  move_and_link(APROX_ETC, ETC_APROX, replaceIfExists=True)
  move_and_link(APROX_STORAGE, VAR_STORAGE)
  move_and_link(APROX_DATA, VAR_DATA)
  move_and_link(APROX_LOGS, LOGS)
  
  etcBootOpts = os.path.join(APROX_ETC, BOOT_PROPS)
  if os.path.exists(etcBootOpts):
    binBootOpts = os.path.join(APROX_BIN, BOOT_PROPS)
    if os.path.exists(binBootOpts):
      os.remove(binBootOpts)
    os.symlink(binBootOpts, etcBootOpts)
else:
  if os.path.isdir(os.path.join(APROX_ETC, ".git")) is True:
    print "Updating indy etc/ git repository..."
    runIn("git pull", APROX_ETC, "Failed to pull updates to etc git repository.")


run("%s %s" % (os.path.join(APROX_DIR, 'bin', 'indy.sh'), opts), fail=False)
