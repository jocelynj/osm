#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os,stat,io,hashlib,re

class hash_file():
  """ Compute md5 hash from a given file """
  sDescript = '?'
  def __init__(self,fpath):
    """ Read file data to md5 buffer """
    self.md5 = hashlib.md5()
    self.sDescript = fpath
    f = io.open(fpath); self.md5.update( f.read() );f.close()

  def __str__(self):
    """ Return md5.hexdigest from type hash_file """
    return self.hexdigest()

  def hexdigest(self):
    return self.md5.hexdigest()
    
  def cmp_tuple(self,hdigest):
    """ Return tuple(string(OK|FAIL), description, hexdigest) """
    fHash = self.md5.hexdigest()
    if fHash == hdigest: sHash = "OK"
    else: sHash = "FAIL"
    return (sHash,self.sDescript,fHash)

  def cmp(self,hdigest):
    """ Return Boolean compared md5.hexdigest() with given hexdigest """
    return self.md5.hexdigest() == hdigest
#end class hash_file

def remove(fpath,trace=True):
  """ Remove one or all files matching given filename wildcard.
      Return False if Wildcard in path
      Return False if No such directory given in fpath
      Return True if all matched filename could be removed
  """
  path = os.path.dirname(fpath)
  if '?' in path or '*' in path: return False
  fail = 0
  name = os.path.basename(fpath)

  # Make re.expression
  regex = name
  # Escape first dot
  i = name.find('.')
  if i >= 0: regex = name[0:i]+'\\'+name[i:len(name)]
  # Make first * = .+
  i = regex.find('*')
  if i >= 0: regex = regex[0:i]+'.+'+regex[i+1:len(regex)]
  # Make first ? = .
  i = regex.find('?')
  if i >= 0: regex = regex[0:i]+'.'+regex[i+1:len(regex)]
  rObj = re.compile(regex,re.UNICODE)

  #print("\tname=%s, path=%s" % (name,path))
  try:
    fnames = os.listdir(path)
    for fname in fnames:
      #print("\tre.match(%s, '%s')" % (rObj.pattern,fname))
      if rObj.match(fname):
        fpath = os.path.join(path, fname)
        try:
          mode = os.lstat(fpath).st_mode
        except os.error:
          mode = 0

        if not stat.S_ISDIR(mode):
          try:
            os.remove(fpath)
            if trace: print("Removed %s" % (fpath))
          except os.error, err:
            if trace: print("[FAIL] Failed to remove %s!\n%s" % (fpath,err))
            fail += 1
    #end for
    return fail == 0
  except os.error, err:
    if trace: print("[FAIL] No such directory: %s!" % path)
    return False
    
#end def remove

def appendString(fpath, s=u'appendString::Teststring'):
  """ For testing, add string 's' to a file """
  f = io.open(fpath, 'a'); f.write(s); f.close()
#end def shakeUp

###########################################################################
import unittest

class TestCase(unittest.TestCase):
  iTests = 0

  def __init__(self,methodName,rootPath='tests'):
    import os

    unittest.TestCase.__init__(self,methodName)
    self.rootPath = os.path.join(rootPath, "helperLib")

    TestCase.iTests += 1
    
    if TestCase.iTests == 1:
      # Run this suite ONCE per class TestCase
      print("%s.__init__" % (__name__))
      if not os.path.exists( self.rootPath ):
        os.makedirs( self.rootPath )
      else:
        # remove old files
        remove( os.path.join(self.rootPath, "*") )
  #end def __init__

  def __del__(self):
    TestCase.iTests -= 1
    if TestCase.iTests == 0:
      print("%s.__del__" % (__name__))
      remove( os.path.join(self.rootPath, "*") )
      os.rmdir( self.rootPath )

  def _hash_file(self):
    print("%s._hash_file using dir %s" % (__name__,self.rootPath))
    fpath = os.path.join(self.rootPath, 'hash_file')
    fname = os.path.basename(fpath)

    # Create a sample file
    appendString(fpath)

    #print hash_file(fpath)
    hdigest = '58b73ff1d46be14bd3da5989decc38b4'

    self.assertTrue( str(hash_file(fpath)) == hdigest)
    self.assertTrue( hash_file(fpath).hexdigest() == hdigest)
    self.assertTrue( hash_file(fpath).cmp(hdigest) )
    self.assertTrue( hash_file(fpath).cmp_tuple(hdigest)[0] == 'OK')
    self.assertTrue( hash_file(fpath).cmp_tuple('dummy')[0] == 'FAIL')
    
    # ShakeUp sample file
    appendString(fpath)
    self.assertFalse( hash_file(fpath) == hdigest)
  #end def _hash_file
  
  def _remove(self):
    def createX(fname):
      """ Create a sample file from 'fname' - Return Filepath """
      fpath = fpath = os.path.join(self.rootPath, fname)
      appendString( fpath )
      return fpath
    #end def create
    def create(fname):
      """ Create a sample file from 'fname'
          Replace given Wildcard (*|?) with 'X'
          Return Filepath with Wildcard
      """
      fname2 = fname
      i = fname.find('*')
      if i >= 0: fname = fname[0:i]+'X'+fname[i+1:len(fname)]
      i = fname.find('?')
      if i >= 0: fname = fname[0:i]+'X'+fname[i+1:len(fname)]

      fpath = fpath = os.path.join(self.rootPath, fname)
      appendString( fpath )
      return os.path.join(self.rootPath, fname2)
    #end def create

    print("%s._remove using dir %s" % (__name__,self.rootPath))
    # Try to remove non existing path
    self.assertFalse( remove( '123456/test/*', False ) )
    
    fpath = create('remove')
    self.assertTrue( remove( fpath ) )
    # Try to remove none existing file second time
    self.assertTrue( remove( fpath ) )

    # Wildcard in path
    fpath2 = fpath; fpath2 = fpath2[0:3]+'?'+fpath2[4:len(fpath2)]
    self.assertFalse( remove( fpath2 ) )
    fpath2 = fpath; fpath2 = fpath2[0:3]+'*'+fpath2[4:len(fpath2)]
    self.assertFalse( remove( fpath2 ) )

    # Wildcard in fname, name, ext
    self.assertTrue( remove( create('12?45.remove') ) )
    self.assertTrue( remove( create('12*45.remove') ) )
    self.assertTrue( remove( create('*.remove') ) )
    self.assertTrue( remove( create('12345.*') ) )
  #end def _remove

  def testRun(self):
    #print("%s.testRun using dir %s" % (__name__,self.rootPath))
    self._hash_file()
    self._remove()

#end class TestCase
