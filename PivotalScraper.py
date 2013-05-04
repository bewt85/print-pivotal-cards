import argparse
import requests
from bs4 import BeautifulSoup
import simplejson

from JSONSoup import JSONSoup

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
      
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('username', help="Your Pivotal Tracker username")
  parser.add_argument('password', help="Your Pivotal Tracker password")
  
  args = parser.parse_args()
  scraper = PivotalScraper()
  scraper.login(args.username, args.password)
  r = scraper.requestProjectDetails(project_id=807271)
  
  soup = JSONSoup()
  soup.loads(r.text)
  print soup
