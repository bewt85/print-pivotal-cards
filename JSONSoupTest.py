import pdb
import unittest
from JSONSoup import JSONSoup

class JSONSoupTest(unittest.TestCase):
  def setUp(self):
    self.d = {
      'a': 1, 
      'k': {
        'b': {
          'e': 4, 
          'd': 5
        },
        'l': 1
      }, 
      'c': 3, 
      'f': [
        0, 
        1, 
        2, 
        3, 
        {
          'b': {
            'e': 4,
            'g': 5
          }
        }
      ]
    }
    self.soup = JSONSoup()
    self.soup.load_obj(self.d)
    
  def test_matchKey_1(self):
    _results = [self.d['k']]
    results = JSONSoup()
    results.load_obj(_results)
    self.assertEqual(self.soup.findAll({'b': {'e':4, 'd': 5}}), results)
    
  def test_matchKey_2(self):
    _results = [self.d['k']['b'], self.d['f'][4]['b']]
    results = JSONSoup()
    results.load_obj(_results)
    self.assertEqual(self.soup.matchKey('b'), results)
    
  def test_matchKey_3(self):
    _results = [self.d['f'][4]['b']]
    results = JSONSoup()
    results.load_obj(_results)
    self.assertEqual(self.soup.matchKey('f').matchKey('b'), results)
