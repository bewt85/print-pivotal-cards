from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os

class StoryRenderer():
  def __init__(self):
    self.cardno = 0
  
  def mapStoryForRender(self, story):
    class FakeStory(object):
      pass
      
    _story = FakeStory()
    
    simple_mapping = {
      'id': 'id',
      'name': 'name',
      'decription': 'description',
      'owned_by': 'owned_by',
      'requester': 'requested_by',
      'type': 'story_type',
      'labels': 'labels',
      'tasks': 'tasks_list',
      'project_name': 'project_name'
    }
    
    for k,v in simple_mapping.iteritems():
      if v in story.keys():
        _story.__setattr__(k, story[v])
    
    if 'epics' in story.keys():
      _story.__setattr__('epic_name', ", ".join(story['epics']))
    
    if 'cardno' not in story.keys():
      _story.__setattr__('cardno', self.cardno)
      self.cardno += 1
    else:
      _story.__setattr__('cardno', stork['cardno'])
    
    return _story
    
  def storiesToPages(self, stories, stories_per_page):
    count = 0
    pages = []
    for story in stories:
     if count % stories_per_page == 0:
       pages.append([])
     pages[-1].append(story)
     count += 1
    
    return pages 
  
  def render(self, _stories, file_name=None, stories_per_page=4):
    env = Environment(
      loader=FileSystemLoader(
        os.path.join(os.path.dirname(__file__),
        'templates')))

    if file_name == None:
      file_name = "default_%s.html" % datetime.strftime(datetime.now(),"%Y%m%d-%H%M%S")
    
    stories = map(self.mapStoryForRender, _stories)
    pages = self.storiesToPages(stories, stories_per_page)

    options = {
      "filing-colours": True,
      "rubber-stamp": True,
      "double-sided": True,
      "white-backs": True
    }  

    options_classes = " ".join([key for key in options.keys() if options[key] == True]) 

    template = env.get_template('printable.html')
    html = template.render(pages = pages, options_classes = options_classes)            
    
    with open(file_name, 'w') as f:
      f.write(html.encode('utf-8'))    
      

