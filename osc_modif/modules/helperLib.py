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
    if fHash == hdigest:
      sHash = "OK"
    else:
      sHash = "FAIL"
                
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
  regex = "r'"+name+"'"
  # Escape dot
  i = name.find('.')
  if i >= 0: regex = name[0:i]+'\\'+name[i:len(name)]
    # Make Star a re.any = .*
  i = regex.find('*')
  if i >= 0: regex = regex[0:i]+'.'+regex[i:len(regex)]

  #print("name=%s, path=%s" % (name,path))
  try:
    fnames = os.listdir(path)
    for fname in fnames:
      #print("re.match(%s, %s)" % (regex,fname))
      if re.match( regex, fname, re.S):
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
    print("[FAIL] No such directory: %s!" % path)
    return False
    
#end def remove

def shakeUp(fpath, s=u'shakeUp'):
  """ For testing, add string 's' to a file """
  f = io.open(fpath, 'a'); f.write(s); f.close()

#end def shakeUp
