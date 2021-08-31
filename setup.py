#!/usr/bin/python

#
# maggy 2.3.2 - GTK+ based utility to create booklets and other layouts 
# from PDF documents.
# Copyright (C) 2008-2012 GAF Software
# <https://sourceforge.net/projects/maggy>
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

"""
try :
    from setuptools import setup
    print "installation with setuptools"
except :
"""

from distutils.core import setup




data_files=[('/usr/share/maggy/data', glob.glob('maggy/data/*.*')),
            ('/usr/share/maggy/config/demo2', glob.glob('maggy/config/demo2/*.*')),
            ('/usr/share/maggy/documentation', glob.glob('maggy/documentation/*.*')),          
            ('/usr/share/applications', ['maggy/data/maggy.desktop']),
            ('/usr/share/locale/fr/LC_MESSAGES', glob.glob('maggy/locale/fr/LC_MESSAGES/*.*')),
            ('/usr/share/pixmaps', ['maggy/data/maggy$.png']),
            ('/usr/share/maggy/icons/hicolor/scalable', ['maggy/data/maggy$.svg'])]


"""
# Freshly generate .mo from .po, add to data_files:
if os.path.isdir('mo/'):
    os.system ('rm -r mo/')
for name in os.listdir('po'):
    m = re.match(r'(.+)\.po$', name)
    if m != None:
        lang = m.group(1)
        out_dir = 'mo/%s/LC_MESSAGES' % lang
        out_name = os.path.join(out_dir, 'pdfshuffler.mo')
        install_dir = 'share/locale/%s/LC_MESSAGES/' % lang
        os.makedirs(out_dir)
        os.system('msgfmt -o %s po/%s' % (out_name, name))
        data_files.append((install_dir, [out_name]))
"""
setup(name='maggy',
      version='2.3.0.12',
      author='GAF Software',
      author_email='Averell7 at sourceforge dot net',
      description='A gui generator for Sqlite and MySQL',
      url = 'https://sourceforge.net/projects/maggy',
      license='GNU GPL-3',
      scripts=['bin/maggy'],
      packages=['maggy'],
      data_files=data_files,
      #requires=['python-poppler'],          # for distutils
      #install_requires=['python-poppler']   # for setuptools
     )
"""
# Clean up temporary files
if os.path.isdir('mo/'):
    os.system ('rm -r mo/')
if os.path.isdir('build/'):
    os.system ('rm -r build/')
"""
