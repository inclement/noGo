from setuptools import setup, find_packages
from os import walk
from os.path import join, dirname, sep
import os
import glob

# NOTE: All package data should also be set in MANIFEST.in

packages = find_packages()

package_data = {'': ['*.json',
                     '*.sgf',
                     '*.py'], }

data_files = []

# By specifying every file manually, package_data will be able to
# include them in binary distributions. Note that we have to add
# everything as a 'pythonforandroid' rule, using '' apparently doesn't
# work.
def recursively_include(results, directory, patterns):
    for root, subfolders, files in walk(directory):
        for fn in files:
            if not any([glob.fnmatch.fnmatch(fn, pattern) for pattern in patterns]):
                continue
            filename = join(root, fn)
            directory = 'pythonforandroid'
            if directory not in results:
                results[directory] = []
            results[directory].append(join(*filename.split(sep)[1:]))

recursively_include(package_data, 'noGo', ['*.py'])
recursively_include(package_data, 'noGo/games', ['*.json', '*.sgf'])
recursively_include(package_data, 'noGo/collections', ['*.json'])

setup(name='noGo',
      version='0.5',
      description='SGF editor for Android',
      author='Alexander Taylor',
      author_email='alexanderjohntaylor@gmail.com',
      url='https://github.com/inclement/noGo', 
      license='GPL3', 
      install_requires=[],
      entry_points={
          'console_scripts': [
              'noGo = noGo.main:run',
              'nogo = noGo.main:run',
              ],
          },
      classifiers = [
          'Development Status :: 4 - Beta',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: OS Independent',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 2',
          ],
      packages=packages,
      package_data=package_data,
      )
