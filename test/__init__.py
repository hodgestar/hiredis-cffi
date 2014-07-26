from unittest import *
from . import reader

def tests():
  suite = TestSuite()
  suite.addTest(makeSuite(reader.ReaderTest))
  return suite
