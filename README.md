print-pivotal-cards
===================

Utility to print cards from [Pivotal Tracker](http://www.pivotaltracker.com). 

Tested with Python 2.7.x

1. You will need to install the [python requests module] (http://docs.python-requests.org/en/latest/)

2. Then you will need to get your own API token - this should be at the bottom of your Pivotal user profile page:
https://www.pivotaltracker.com/profile

3. Run 'python PivotalCardPrinter.py [your api token] [your project ID]' 

4. Optional Parameters:
  *  -o, --output [an html filename] - The file you want to output to (defaults to default_[timestamp].html)
  *  -s, --since [a date in mm/dd/yyyy format] - Specifies that you only want Stories created or modified since [date]<don't link> (defaults to the beginning of time)

5. This will create a HTML file with all stories from that project. 

6. Print in landscape

Coming up:
- filtering (probably via argparse) [somewhat done]
- more data on cards [somewhat done]
- prettier cards [somewhat done]
- more testing
- finish the scraping option
- making this simpler, faster, more robust and more useful (whoever gets to it first) 

Experimental:
7. Optional Parameters:
  *  -u, --username - Your Pivotal Tracker username
  *  -p, --password - Your Pivotal Tracker password
  
If you provide these details, the script scrapes the Pivotal Tracker website and pulls out further details such as tasks, epics and the project name.  This approach has a couple of disadvantages: Pivotal Tracker might change their website; so far I've not persuaded it to scrape recent changes.  More work (and testing) is needed.

Thanks to PSD for https://github.com/psd/pivotal-cards
