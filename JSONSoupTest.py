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
      ],
      't': {
        'u': 1,
        'v': 2,
        'w': {
          'x': 3,
          'y': [5, 6],
          'z': 7
        }
      }
    }
    self.soup = JSONSoup()
    self.soup.load_obj(self.d)
    
  def test_findAll_1(self):
    _expected_results = [self.d['k']]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    self.assertEqual(self.soup.findAll({'b': {'e':4, 'd': 5}}), expected_results)
  
  def test_findAll_2(self):
    _expected_results = [{'u': 1, 'w': {'y': [5, 6], 'x': 3, 'z': 7}, 'v': 2}]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    self.assertEqual(self.soup.findAll({'u': 1}), expected_results)
    
  def test_findAll_parent(self):
    _expected_results = {
      'u': 1,
      'v': 2,
      'w': {
        'x': 3,
        'y': [5, 6],
        'z': 7
      }
    }
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    self.assertEqual(self.soup.findAll({'x':3})[0].parent, expected_results)
  
  def test_matchKey_1(self):
    _expected_results = [self.d['f'][4]['b']]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    self.assertEqual(self.soup.matchKey('f').matchKey('b'), expected_results)
    
  def test_matchKey_2(self):
    _expected_results = [self.d['k']['b'], self.d['f'][4]['b']]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    self.assertEqual(self.soup.matchKey('b'), expected_results)
    
  def test_matchKey_3(self):
    alt_d = {'u': 1, 'w': {'y': [5, 6], 'x': 3, 'z': 7}, 'v': 2}
    alt_soup = JSONSoup()
    alt_soup.load_obj(alt_d)
    _expected_results = [3]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    self.assertEqual(alt_soup.matchKey('x'), expected_results)
  
  def test_matchKey_4(self):
    alt_d = {'u': 1, 'w': {'y': [5, 6], 'x': 3, 'z': 7}, 'v': 2}
    alt_soup = JSONSoup()
    alt_soup.children=[JSONSoup()]
    alt_soup.children[0].children = JSONSoup()
    alt_soup.children[0].children.load_obj(alt_d)
    _expected_results = [3]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    self.assertEqual(alt_soup.matchKey('x'), expected_results)
    
  def test_matchValue_returns_soup(self):
    results = self.soup.matchValue(4)
    for soup in results:
      self.assertEqual(isinstance(soup, JSONSoup), True)
  
  def test_matchValue_1(self):
    _expected_results = [{'e': 4, 'g': 5}, {'e': 4, 'd': 5}]
    _expected_results.sort()
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    results = self.soup.matchValue(4)
    self.assertEqual(isinstance(results.children, list), True)
    results.children.sort()
    self.assertEqual(results, expected_results)
  
  def test_matchValue_2(self):
    _expected_results = [{'x': 3, 'y': [5, 6], 'z': 7}]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    results = self.soup.matchValue(7)
    self.assertEqual(results, expected_results)
    
  def test_findAll_matchValue_1(self):
    _expected_results = [3]
    expected_results = JSONSoup()
    expected_results.load_obj(_expected_results)
    partial_results = self.soup.findAll({'u': 1})
    results = partial_results.matchKey('x')
    self.assertEqual(results, expected_results)
