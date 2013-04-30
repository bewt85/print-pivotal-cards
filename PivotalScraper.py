import argparse
import requests
from bs4 import BeautifulSoup
import simplejson

TIME_ZONE_OFFSET = 1

class PivotalScraper():
  def __init__(self):
    self.session = None
  
  def login(self, username, password):
    authenticity_token = self.getAuthenticityToken()
    payload = {
      'authenticity_token': authenticity_token,
      'credentials[username]': username,
      'credentials[password]': password,
      'time_zone_offset': TIME_ZONE_OFFSET
    }
    
    r = requests.post("https://www.pivotaltracker.com/signin", verify=True, data=payload)
    self.session = {'t_session': r.cookies['t_session']}

  def getAuthenticityToken(self):
    r = requests.get("https://www.pivotaltracker.com/signin", verify=True)
    soup = BeautifulSoup(r.text)
    return soup.form.find(attrs={'name': 'authenticity_token'})['value']

  def get(self, url):
    if self.session <> None:
      r = requests.get(url, verify=True, cookies=self.session)
      return r
    else:
      return None
      
  def requestProjectDetails(self, project_id):
    return self.get('https://www.pivotaltracker.com/services/v5/projects/%s' % project_id)

class JSONSoup:
  """ Not really a proper Soup but certainly inspired by BeautifulSoup """
  def __init__(self, raw=None):
    if raw==None:
      raw = {}
    elif type(raw) == list or type(raw) == dict:
      raw = raw
    elif type(raw) == str:
      raw=simplejson.loads(json_text)
    else:
      # I could allow things like 'int's as well but then it would be ambiguous
      # whether a string is actually a string or a bit of JSON.
      raise TypeError("JSON soup cannot be initialised with this type")
    self.buildTree(raw)
  
  """
  def __repr__(self):
    return self.__str__()
  """
   
  def __str__(self):
    """ NB JSON null <--> Python None """
    def build(soup):
      if type(soup.children) == list:
        raw = []
        for c in soup.children:
          if isinstance(c, JSONSoup):
            raw.append(build(c))
          else:
            raw.append(c)
        return raw
      elif type(soup.children) == dict:
        raw = {}
        for k,c in soup.children.iteritems():
          if isinstance(c, JSONSoup):
            raw.update({k: build(c)})
          else:
            raw.update({k: c})
        return raw
      
    return build(self).__str__()
  
  def __getitem__(self, k):
    return self.children[k]
    
  def __setitem__(self, k,v):
    self.children[k] = self.v

  def __len__(self):
    return len(self.children)

  def buildTree(self, raw):
    self.parent = None
    if type(raw) == list:
      self.children = []
      for c in raw:
        if type(c) in [list, dict]:
          child = JSONSoup(c)
          child.parent=self
        else:
          child = c
        self.children.append(child)
    elif type(raw) == dict:
      self.children = {}
      for k,c in raw.iteritems():
        if type(c) in [list, dict]:
          child = JSONSoup(c)
          child.parent = self
        else:
          child = c
        self.children.update({k: child})
    else:
      raise TypeError("Should only have dicts and lists at this stage")

  def findAll(self, attrs):
    def hunt():
      for soup in self.findKey(attrs.keys()):
        match=True
        for (k,v) in attrs.iteritems():
          if type(soup.children) <> dict: #this shouldn't ever be the case
            match=False
            break
          if k not in soup.children.keys() or soup.children[k] <> v:
            match=False
            break
        if match:
          yield soup
          
    results = [result for result in hunt()]
    result_soup = JSONSoup(results)
    return result_soup

  def findKey(self, keys):
    key_set = set(keys)
    def hunt(soup):
      if isinstance(soup, JSONSoup):
        d = soup.children
      else:
        return # All dicts should be wraped within JSONSoups
      if type(d) == dict:
        if key_set.issubset(d.keys()):
          yield soup
        for v in d.values():
          for _v in hunt(v):
            yield _v
      elif type(d) == list:
        for v in d:
          for _v in hunt(v):
            yield _v
      return
    
    results = [result for result in hunt(self)]
    result_soup = JSONSoup(results)
    return result_soup
      
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('username', help="Your Pivotal Tracker username")
  parser.add_argument('password', help="Your Pivotal Tracker password")
  
  args = parser.parse_args()
  scraper = PivotalScraper()
  scraper.login(args.username, args.password)
  r = scraper.requestProjectDetails(project_id=807271)
  
  soup = JSONSoup(r.text)
  print soup
