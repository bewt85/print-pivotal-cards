import argparse
import requests
from bs4 import BeautifulSoup
import simplejson
import pdb

from JSONSoup import JSONSoup
from PivotalCardPrinter import Story
from ScrapedStoryRenderer import ScrapedStoryRenderer

TIME_ZONE_OFFSET = 1

class PivotalScraper():
  def __init__(self):
    self.session = None
  
  def reloadStories(self):
    self.stories = None
    self.loadStories()
  
  def loadStories(self):
    if not hasattr(self, 'stories') or self.stories == None:
      self.loadProjectSoup()
      stories = self.project_soup.matchKey('project').matchKey('stories')[0].get_raw()
      project_name = self.project_soup.matchKey('project').matchKey('name').get_raw()[0]
      self.loadAllEpics()
      self.loadAllLabels()  
      self.loadAllMembers()
      addProject = lambda x: self.addStatic('project_name', project_name, x)
      stories = map(addProject, stories)
      stories = map(self.epicsAndLabels_ID2String, stories)
      stories = map(self.requestedBy_ID2String, stories)
      stories = map(self.ownedBy_ID2String, stories)
      stories = map(self.tasks_format, stories)
      self.stories = stories          
  
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
  
  def reloadProjectSoup(self):
    self.project_soup = None
    self.loadProjectSoup
  
  def loadProjectSoup(self):
    if not hasattr(self, 'project_soup') or self.project_soup == None:
      r = self.requestProjectDetails(project_id=807271)
      self.project_soup = JSONSoup()
      self.project_soup.loads(r.text)
    
  def reloadAllEpics(self):
    self.all_epics = None
    self.loadAllEpics()
  
  def loadAllEpics(self):
    if not hasattr(self, 'all_epics') or self.all_epics == None:
      _epics = self.project_soup.matchKey('project').matchKey('epics')[0].get_raw()
      self.all_epics = {}
      for epic in _epics:
        self.all_epics.update({epic['label_id']: epic['name']})
    
  def reloadAllLabels(self):
    self.all_labels = None
    self.loadAllLables()
    
  def loadAllLabels(self):
    if not hasattr(self, 'all_labels') or self.all_labels == None:
      _labels = self.project_soup.matchKey('project').matchKey('labels')[0].get_raw()
      self.all_labels = {}
      for label in _labels:
        self.all_labels.update({label['id']: label['name']})

  def reloadAllMembers(self):
    self.all_members = None
    self.loadAllMembers()
    
  def loadAllMembers(self):
    if not hasattr(self, 'all_members') or self.all_members == None:
      _members = self.project_soup.matchKey('project').matchKey('members')[0].get_raw()
      self.all_members = {}
      for member in _members:
        self.all_members.update({member['id']: member})
  
  def addStatic(self, key, value, story):
    story[key] = value
    return story
      
  def epicsAndLabels_ID2String(self, story):
    story_labels = []
    story_epics = []
    for label_id in story['label_ids']:
      if label_id in self.all_epics.keys():
        story_epics.append(self.all_epics[label_id])
      else:
        story_labels.append(self.all_labels[label_id])
    story['epics'] = story_epics
    story['labels'] = story_labels
    return story
  
  def requestedBy_ID2String(self, story):
    if story['requested_by_id'] in self.all_members.keys():
      story['requested_by'] = self.all_members[story['requested_by_id']]['name']
    else:
      story['requested_by'] = "<Unknown: %s>" % story['requested_by_id']
    return story
  
  def ownedBy_ID2String(self, story):
    if story['owned_by_id'] == -1:
      story['owned_by'] = ""
    elif story['owned_by_id'] in self.all_members.keys():
      story['owned_by'] = self.all_members[story['owned_by_id']]['name']
    else:
      story['owned_by'] = "<Unknown: %s>" % story['owned_by_id']
    return story
    
  def tasks_format(self, story):
    class Task:
      def __init__(self):
        self.complete = False
        self.description = ""
    
    story_tasks = []
    for _task in story['tasks']:
      task = Task()
      task.description = _task['description']
      task.complete = _task['complete']
      story_tasks.append(task)
    story['tasks_list'] = story_tasks
    return story
    
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('username', help="Your Pivotal Tracker username")
  parser.add_argument('password', help="Your Pivotal Tracker password")
  parser.add_argument(
    "-o", "--output", 
    help="The HTML file you want to output to", 
    default=None
  )
  
  args = parser.parse_args()
  scraper = PivotalScraper()
  scraper.login(args.username, args.password)
  scraper.reloadStories()
  
  story_renderer = ScrapedStoryRenderer()
  story_renderer.render(scraper.stories, args.output)
