import simplejson
import copy
import pdb

class JSONSoup:
  def __init__(self):
    self.parent = None
    self.children = []

  def findAll(self, attrs):
    first_key_matches = self.matchAllKey(attrs.keys()[0])
    parents_of_first_key_matches = [m.parent for m in first_key_matches]
    
    matches = []
    for potential_match in parents_of_first_key_matches:
      raw_potential_match = potential_match.get_raw()
      ismatch = True
      if not set(attrs.keys()).issubset(raw_potential_match.keys()):
        ismatch = False
        continue
      for k,v in attrs.iteritems():
        if raw_potential_match[k] <> v:
          ismatch = False
          break
      if ismatch:
        matches.append(potential_match)
    
    if len(matches) == 0:
      return JSONSoup() # An empty soup
    else:
      results = JSONSoup()
      results.children = matches
      return results
      
  def matchKey(self, key):
    def dig(obj):
      if isinstance(obj, JSONSoup):
        obj = obj.children
        for _v in dig(obj):
          yield _v
      elif isinstance(obj, dict):
        if key in obj.keys():
          yield obj[key]
        else:
          for v in obj.values():
            for _v in dig(v):
              yield _v
      elif isinstance(obj, list):
        for v in obj:
          for _v in dig(v):
            yield _v
      else:
        return # Something like a string or an int
      
    new_soup = JSONSoup()
    new_soup.children = [o for o in dig(self.children)]
        
    return new_soup

  def matchAllKey(self, key):
    def dig(obj):
      if isinstance(obj, JSONSoup):
        obj = obj.children
        for _v in dig(obj):
          yield _v
      elif isinstance(obj, dict):
        if key in obj.keys():
          yield obj[key]
        for v in obj.values():
          for _v in dig(v):
            yield _v
      elif isinstance(obj, list):
        for v in obj:
          for _v in dig(v):
            yield _v
      else:
        return # Something like a string or an int
      
    new_soup = JSONSoup()
    new_soup.children = [o for o in dig(self.children)]
        
    return new_soup

  def matchValue(self, value):
    def dig(obj):
      if isinstance(obj, JSONSoup):
        obj = obj.children
      if isinstance(obj, dict):
        for v in obj.values():
          if value in dig(v):
            yield obj
          else:
            for _v in dig(v):
              yield _v
      elif isinstance(obj, list):
        for v in obj:
          if value in dig(v):
            yield obj
          else:
            for _v in dig(v):
              yield _v
      elif obj == value:
        yield obj 
    
    def makeSoup(obj):
      if not isinstance(obj, JSONSoup):
        new_soup = JSONSoup()
        new_soup.children = obj
        return new_soup
      else:
        return obj
      
    new_soup = JSONSoup()
    objs = [o for o in dig(self.children)]
    if objs == None:
      objs = []
    new_soup.children = map(makeSoup, objs)
    
    return new_soup
        
  def load(self, stuff):
    if isinstance(stuff, JSONSoup):
      self.__dict__ = stuff.__dict__.copy()
    elif isinstance(stuff, dict) or isinstance(stuff, list):
      self.load_obj(stuff)
    elif isinstance(stuff, str):
      self.loads(stuff)
    else:
      raise TypeError("Cannot load objects of this type")
    
  def loads(self, s):
    o = simplejson.loads(s)
    self.load_obj(o)
  
  def load_obj(self, obj):
    def replace(obj, parent):
      new_soup = JSONSoup()
      new_soup.children = obj
      new_soup.parent = parent
      
      if isinstance(obj, dict):
        for k,v in new_soup.children.iteritems():
          new_soup.children[k] = replace(v, new_soup)
      elif isinstance(obj, list):
        new_soup.children = map(lambda c: replace(c, new_soup), new_soup.children)
      
      return new_soup
    
    new_soup = replace(copy.deepcopy(obj), None)
    self.__dict__ = new_soup.__dict__
    
  def __str__(self):
    return self.get_raw().__str__()
  
  def get_raw(self):
    def dig(obj):
      if isinstance(obj, JSONSoup):
        obj = obj.children
        obj = dig(obj)
      elif isinstance(obj, dict):
        for k,v in obj.iteritems():
          obj[k] = dig(v)
      elif isinstance(obj, list):
        obj = map(dig, obj)
      
      return obj
      
    return dig(copy.deepcopy(self))
  
  def __iter__(self):
    for child in self.children:
      yield child
  
  def __setitem__(self, k, v):
    self.children[k] = v
  
  def prettify(self):
    return simplejson.dumps(self.get_raw(), indent=2)
  
  def __getitem__(self, k):
    return self.children[k]
  
  def __len__(self):
    return len(self.children)
  
  def __eq__(self, other):
    if not isinstance(other, JSONSoup):
      return False
    return self.get_raw() == other.get_raw()
  
    
