import argparse
import requests
from bs4 import BeautifulSoup
import simplejson
import pdb

from JSONSoup import JSONSoup
from PivotalCardPrinter import Story
from StoryRenderer import StoryRenderer

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
      self.loadAllEpics()
      self.loadAllLabels()  
      self.loadAllMembers()
      stories = map(self.epicsAndLabels_ID2String, stories)
      stories = map(self.requestedBy_ID2String, stories)
      stories = map(self.ownedBy_ID2String, stories)
      stories = map(self.tasks_ID2String, stories)
      self.stories = stories          
  
  def mapStoryForRender(self, story):
    simple_mapping = {
      'id': 'id',
      'name': 'name',
      'decription': 'description',
      'owned_by': 'owned_by',
      'requester': 'requested_by'
    }
    details = {}
    for k,v in simple_mapping.iteritems():
      details[k] = story[v]
    
    details['labels'] = ", ".join(story['labels'])
    details['tasks'] = "<br>".join(story['tasks_str'])
    details['epic_name'] = ", ".join(story['epics'])

    # Hack to reuse StoryRenderer.  Could do with a refactor 
    class FakeStory():
      def __init__(self, details):
        self.details = details
    
    _story = FakeStory(details)
    return _story
    
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
    
  def tasks_ID2String(self, story):
    story_tasks = []
    for task in story['tasks']:
      story_tasks.append(task['description'])
    story['tasks_str'] = story_tasks
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
  
  stories = map(scraper.mapStoryForRender, scraper.stories)
  
  story_renderer = StoryRenderer()
  story_renderer.render(stories, args.output)
