import requests
import sys
import argparse
import urllib
from xml.dom import minidom

from StoryRenderer import StoryRenderer


class PivotalAPIParser:
  def __init__(self):
    self.api_credential = None
    self.headers = None
    self.stories = {}
    
  def login(self, api_credential):
    self.api_credential = api_credential
    self.headers={'X-TrackerToken' : self.api_credential}

  def reloadStories(self, project_id, modified_since=None, params={}):
    self.stories = None
    self.loadStories(project_id, modified_since, params)
  
  def loadStories(self, project_id, modified_since=None, params={}):
    if not hasattr(self, 'stories') or self.stories == None:
      self.stories = {}
      if modified_since<>None:
        params.update({'filter': "modified_since:%s includedone:true" % modified_since})
        
      params_url = urllib.urlencode(params)
      if len(params_url) > 0:
        params_url = "?" + params_url
      
      r = self.get(
        "https://www.pivotaltracker.com/services/v3/projects/%s/stories%s" % 
        (project_id, params_url)
      )
      r_xml = minidom.parseString(r.text)
      
      for story_xml in r_xml.getElementsByTagName("story"):
        story_id = int(self.getXMLElementData(story_xml,"id"))
        name = self.getXMLElementData(story_xml,"name")
        description = self.getXMLElementData(story_xml,"description")
        owned_by = self.getXMLElementData(story_xml,"owned_by")
        labels = self.getXMLElementData(story_xml,"labels")
        requester = self.getXMLElementData(story_xml,"requested_by")
        self.stories[story_id] = {
          "id": story_id, 
          "name": name,
          "description": description,
          "owned_by": owned_by,
          "requester": requester,
          "labels": [labels]
        }
        
      self.setIterationOfStories(project_id)
      
  def setIterationOfStories(self, project_id):
    # A bit of a hack because Pivotal Tracker does not report whether a story
    # is in the backlog, current or done.  Currently cannot spot if a story is
    # in the icebox.
    for iteration in ["current", "backlog", "done"]:
      r = self.get(
        "https://www.pivotaltracker.com/services/v3/projects/%s/iterations/%s" % 
        (project_id, iteration)
      )
      r_xml = minidom.parseString(r.text)
      for story_xml in r_xml.getElementsByTagName("story"):
        story_id = int(self.getXMLElementData(story_xml, "id"))
        if story_id in self.stories.keys(): 
          # Sometimes self.stories does not have all the stories.
          # For example because we did a filtered search or because there
          # was an update in Pivotal Tracker between updating the stories
          # list and setting this parameter
          self.stories[story_id]['iteration'] = iteration
  
  def get(self, url):
    return requests.get(url,
      verify = True,
      headers = self.headers) 
  
  def getXMLElementData(self, the_xml, tag_name):
    results = the_xml.getElementsByTagName(tag_name)
    if len(results) == 0:
      return ""
    elif results[0].firstChild == None:
      return ""
    else:
      return results[0].firstChild.data
    
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "token", 
    help="Your Pivotal Tracker API Token from 'www.pivotaltracker.com/profile'"
  )
  parser.add_argument(
    "pid", 
    help="Your Project ID (e.g. www.pivotaltracker.com/s/projects/<pid>)", 
    type=int
  )
  parser.add_argument(
    "-o", "--output", 
    help="The HTML file you want to output to", 
    default=None
  )
  parser.add_argument(
    "-s", "--since", 
    help="Filters to only cards created or updated since <date>.  Format date as 'Nov 16 2009' or '11/16/2009' (NB American style)", 
    default=None
  )
  
  args = parser.parse_args() 
  
  api_parser = PivotalAPIParser()
  api_parser.login(args.token)
  
  print('Getting stories for project %s' % args.pid)
  api_parser.reloadStories(args.pid, args.since)
    
  story_renderer = StoryRenderer()
  stories  = api_parser.stories.values()
  
  print('Sending %s stories to the renderer'%len(stories))
  story_renderer.render(stories, file_name=args.output) # renderer needs a list of stories
