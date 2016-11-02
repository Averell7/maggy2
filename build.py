#!/usr/bin/python

#
# PdfBooklet 2.3.0 - GTK+ based utility to create booklets and other layouts 
# from PDF documents.
# Copyright (C) 2008-2012 GAF Software
# <https://sourceforge.net/projects/pdfbooklet>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import os
import re
import glob
from ftplib import FTP


version = "2.0.0.50"
print "\n\n ================ start bdist =============================\n\n"
os.system('sudo python setup.py bdist')
print "\n\n ================ end bdist - start sdist =================\n\n"
os.system('sudo python setup.py sdist')
print "\n\n ================ end sdist - start bdist_rpm =============\n\n"
os.system('sudo python setup.py bdist_rpm')
print "\n\n ================ end bdist_rpm ===========================\n\n"
rpm_file = "./dist/maggy2-" + version + "-1.noarch.rpm"
tar_file = "./dist/maggy2-" + version + ".tar.gz"
tar64_file = "./dist/maggy2-" + version + ".linux-x86_64.tar.gz"

if os.path.isfile(rpm_file) :
  print "found rpm", rpm_file
else :
    print "NOT found rpm", rpm_file
  
if os.path.isfile(tar_file) :
  print "found tar", tar_file
else :
    print "NOT found tar", tar_file
  
os.system("ls ./dist")


print "\n\n ================ Uploading tar.gz =======================\n\n"

ftp = FTP('perso-ftp.orange.fr')     # connect to host, default port
x = ftp.login('dysmas1956@wanadoo.fr', '4ua7x9x')                     # user anonymous, passwd anonymous@
print "Connect to Ftp : " + x
ftp.cwd('maggy')               # change into "debian" directory
#ftp.retrlines('LIST')           # list directory contents
#ftp.retrbinary('RETR Archeotes.sqlite', open('Archeotes.sqlite', 'wb').write)
try :
    command = 'STOR ' + tar_file[7:]
    x = ftp.storbinary(command, open(tar_file, 'rb'))    
except :    
    print "tar file error :", command

try :
    command = 'STOR ' + tar64_file[7:] 
    x = ftp.storbinary(command, open(tar64_file, 'rb'))
except :
    print "tar64 file error :", command
    
try :
    command = 'STOR ' + rpm_file[7:]
    x = ftp.storbinary(command, open(rpm_file, 'rb'))
except :
    print "rpm file error :", command


# generate Debian package
print "\n\n ================ Creating debian package =======================\n\n"
new_dir = "./pdfBooklet-" + version + "/"
os.system('sudo alien --generate --scripts ' + rpm_file)
control_file = new_dir + "debian/control"
if os.path.isfile(control_file) :
  print "control found"

f1 = open(control_file, "r")

data1 = f1.read()
data1 = data1.replace("${shlibs:Depends}", "pygtk2|python-gtk2, pypoppler|python-poppler")
f1.close()
f1 = open(control_file, "w")
f1.write(data1)
f1.close()

os.system("cd " + new_dir + "; sudo dpkg-buildpackage")

deb_file = "./pdfbooklet_" + version + "-2_all.deb"

# install package
print "\n\n ================ Installing debian package =============================\n\n"
os.system("sudo dpkg -i " + deb_file)
os.system("sudo apt-get -f -y install")

print "\n\n ================ build.py terminated =============================\n\n"





x = ftp.storbinary('STOR ' + deb_file[2:], open(deb_file, 'rb'))
print x
ftp.quit()



  





#os.system('rpmrebuild -b -R --change-spec-requires rebuild.py -p ' + new_file )


"""
# Clean up temporary files
if os.path.isdir('mo/'):
    os.system ('rm -r mo/')
if os.path.isdir('build/'):
    os.system ('rm -r build/')
"""
