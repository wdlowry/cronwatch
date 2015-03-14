# Steps #

  1. Edit pavement.py and change VERSION:
```
VERSION = '1.4'
```
  1. Edit docsrc/source/conf.py and change version:
```
version = '1.4'
```
  1. Edit docsrc/source/usage.rst and change the tar file name:
```
tar xzf cronwatch-1.4.tar.gz
...
cd cronwatch-1.4
```
  1. Commit all changes
```
svn commit
```
  1. Create an SVN tag
```
svn copy https://cronwatch.googlecode.com/svn/trunk/ https://cronwatch.googlecode.com/svn/tags/1.4
```
  1. Create the tarball
```
paver sdist
```
  1. Deprecate the old release download
  1. Upload and feature the new release tarball
  1. Register with pypi
```
paver register
```