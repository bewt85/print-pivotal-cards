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
  def __init__(self, raw=None):
    if raw=None:
      self.raw = None
    elif type(raw) == list or type(raw) == dict:
      self.raw = raw
    elif type(raw) == str:
      self.raw=simplejson.loads(json_text)
    else:
      # I could allow things like 'int's as well but then it would be ambiguous
      # whether a string is actually a string or a bit of JSON.
      raise TypeError("JSON soup cannot be initialised with this type")
      
  def __str__(self):
    """ NB JSON null <--> Python None """
    return simplejson.dumps(self.raw, indent=2)

  def __getattr__(self, name):
    return raw[name]
    
  def __getitem__(self, k):
    return raw[k]
    
  def __setitem__(self, k,v):
    raw[k] = v

  def findAll(self, attrs):
    def hunt(d):
      if type(d) == dict:
        for k,v in attrs.iteritems():
          if k in d.keys() and d[k] == v:
            yield d
        for v in d.values():
          for _v in hunt(v):
            yield _v
      elif type(d) == list:
        for v in d:
          for _v in hunt(v):
            yield _v
      return
    
    results = [result for result in hunt(self.raw)]
    result_soup = JSONSoup()
    result_soup.raw = results
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
