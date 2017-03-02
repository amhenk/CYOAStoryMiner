import requests
import re
import unicodedata
import sys
import os

from story_class import Story, Page					# Really basic story object
from HTMLParser import HTMLParser
from html import HTML				# used to generate the HTML for our Watson input
from lxml import html

"""
	Has to be run with python 2.7

	So, in order to get everything you're gonna need to install lxml
	and requests. To do that run:
		python -m pip install lxml
		python -m pip install requests
		python -m pip install html
"""

#Output so it doesn't clutter the console
#Also good for giving a general idea of the size of everything
f = open("adv.txt", 'w+')

# Data needed to request a different page within a story
form_data = {
	"__VIEWSTATE": "",
	"__VIEWSTATEGENERATOR": "",
	"SS": "",
	"pbAction": "FollowLink",		# Always want to follow the link
	"pbValue": 0					# Directs to page we want
}

pbValues = []

# regex used for getting the postback value for form_data
digit = re.compile('\d+')

def visit_stories(game_list,dir):
	global pbValues

	root_url = "http://chooseyourstory.com"
	page = requests.get(game_list)	
	tree = html.fromstring(page.text)
	xpath = ""
	count = 18 #ctl value for whatever reason, no explaination why it has to be 18 other than it just does
	story = Story()

	#Base URL for playing the game
	adv_story_url = "http://chooseyourstory.com/story/viewer/default.aspx?StoryId="

	for x in range(0,r):
		# This xpath gets the home page for each story, which leads to us getting the StoryID
		xpath = "//*[@id=\"MainContentPlaceHolder_StoriesGridView_HyperLink1_{0}\"]/@href".format(x)
		story_xpath = tree.xpath(xpath)	# Story's name along with redirect we use
		story_name = story_xpath[0][story_xpath[0].find('y/')+2:story_xpath[0].find('.aspx')]
		if not story_name:
			return	# Break if there is no story

		adv_url = root_url + tree.xpath(xpath)[0][2:]	# xpath returns ['../story/<game_name>']' thus the [0][2:]
		adv_page = html.fromstring(requests.get(adv_url).text)

		while(1):
			try:
				adv_num =  digit.findall(adv_page.xpath("//*[@id=\"ctl{0}\"]/input/@onclick".format(count))[0])[0]
				count = 18
				break
			except IndexError:
				if count > 100:
					break 		#Give up after this point
				count += 1

		print "StoryNum   StoryID   Storyname"
		print "{0:<3}{3:<8}{1:<5}{3:<5}{2:<30}\n".format(x,adv_num,story_name, ' ')
		# Pass in current game url, request the page using the StoryID, set the pbValue to 0
		story = Story(story_name)
		read_story(adv_story_url+adv_num,requests.get(adv_story_url+adv_num),0, story)
		f.write("\n\n+++++++\nEND {0}\n+++++++\n\n".format(story_name))

        
		if not os.path.exists("stories/"+dir) and "-i" not in sys.argv:
			os.makedirs("stories/"+dir)
		s_file = open("stories/"+dir+"/"+story_name+'.html', 'w+')
		s_file.write(story.write_story())
		s_file.close()
		#Clear pbValues for new page
		pbValues = []

def read_story(url,story_page, pbVal, html_story):
	#Gets the html from the page
	tree = html.fromstring(story_page.text)
	
	# This sees if there is a redirect and aborts the story
	if tree.xpath("//*[@id=\"ctl01\"]/div[4]/p[3]/a/@href"):
		return

	#Finds a specific area of the html you want to look at
	para = tree.xpath("/html/body/div[3]/div[1]/*/span/text()")
	if not para:
		para = tree.xpath("/html/body/div[3]/div[1]/*/text()")

	choices = tree.xpath("/html/body/div[3]/ul/li[*]/a/text()")
	#Prints text
	text = ""
	c = []
	#if pbVal not in pbValues:
	for x in para:
		x = x.replace('\t',"")
		x = x.replace('\"',"")
		text += x
		f.write(x.encode("utf-8") + '\n')
	if choices:
		for choice in choices:
			c.append(choice)
	html_story.pages.append(Page(text,pbVal, c))
	pbValues.append(pbVal)
	
	# Check for Inventory
	# inv = tree.xpath("/html/body/div[3]/table/tbody/tr/*/a/@onclick")
	# if inv:
		
	
	# Goes through every choice and populates form_data
	for x in tree.xpath("/html/body/div[3]/ul/li[*]/a/@onclick"):
		form_data["__VIEWSTATE"] = tree.xpath("//*[@id=\"__VIEWSTATE\"]/@value")[0]
		form_data["__VIEWSTATEGENERATOR"] = tree.xpath("//*[@id=\"__VIEWSTATEGENERATOR\"]/@value")[0]
		form_data["SS"] = tree.xpath("//form/input[3]/@value")
		for d in digit.findall(x):
			if d not in pbValues:
				#Postback value that determines page next visited
				form_data["pbValue"] = d

				#Prints the form data if verbose is on
				if v:
					for x in form_data.keys():
						print "{0}: {1}".format(x, form_data[x])
				# Passes current url while posting the form_data to load new story text
				read_story(url,requests.post(url,data=form_data), d, html_story)

	return 0

def shotgun_pbVal(url, html_story):
	for k in range(1,600):
		if k not in pbValues:
			form_data["pbValue"] = k
			if v:
				for y in form_data.keys():
					print "{0}: {1}".format(y, form_data[y])
			
			read_story(url,requests.post(url,data=form_data), k, html_story)
	
def main():
	genres = ["Fantasy_Adventure",
			"Modern_Adventure",
			"Sci_Fi_Adventure",
			"Mystery_Puzzle",
			"Horror",
			]
	# List all the stories on a page
	try:
		for g in genres:
			print g
			game_list = "http://chooseyourstory.com/Stories/{}.aspx".format(g)

			visit_stories(game_list,g)
	except KeyboardInterrupt:
		#If you get bored you can kill it and not lose your text
		pass

	#Be sure to close output file
	f.close()

if __name__ == '__main__':
	r = 250		# Defualt number of stories to look through
	v = False	# Do not print form_data if False
	i = False	# Do not write out into html if True

	# Directory where we store generated html, assumes you want html by default
	if not os.path.exists("stories") and "-i" not in sys.argv:
		os.makedirs("stories")
		print "----------------------------------------"
		print "       Created Stories Directory        "
		print "----------------------------------------"

	if "-h" in sys.argv:
		print "HELP: [-r <number>] [-v <verbose>]"
		print
		sys.exit(0)

	if "-r" in sys.argv:
		try:
			r = int(sys.argv[sys.argv.index("-r")+1])
		except IndexError:
			print "-r <number>"
			exit()
	
	if "-v" in sys.argv:
		v = True

	main()
