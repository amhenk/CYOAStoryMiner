"""
This set of classes is going to be used for easy HTML generation
for Watson to read. Syntax is as follows:
	<html>
	<body>
		<div class="Story" id="Game Name">
			<div class="Page" value=0>
				TEXT OR SOMETHING
				<div class="Choice" value=0> Go to Castle </div>
				<div class="Choice" value=1> Go Home </div>
			</div>
			<div class="Page" value=1>
				....
			<div>
			....
		<div> 
	<body>
	<html>
"""
import unicodedata

from BeautifulSoup import BeautifulSoup as bs
from html import HTML

class Page:
	def __init__(self, text, number=0, choices=[]):
		self.text = text
		self.num = number
		self.choices = choices

	def __str__(self):
		print self.text

	def __repr__(self):
		print "\n\n\n\n********************what*********************\n\n\n\n"

class Story:
	"""
		Class for containing each story in an orderly way.

		Primarily going to be used for writing the information
		out to an HTML format that's readable to Watson
	"""
	def __init__(self, title=""):
		self.title = title
		self.pages = []		# List of Page objects


	def write_story(self):
		#This is where we add the tags
		h = HTML()
		h.html()
		h.body()
		h.div(klass="Story",id=self.title)

		for (x, p) in enumerate(self.pages):
			# print x, p.text, p.choices
			# exit()
			h.div(klass="Page",value=str(x))
			if isinstance(p.text,unicode):
				h+=HTML(text=unicodedata.normalize('NFKD', p.text).encode('ascii','ignore'))
			else:
				h+=HTML(text=p.text)
			for (k, choice) in enumerate(p.choices):
				if isinstance(choice, unicode):
					choice = unicodedata.normalize('NFKD', choice).encode('ascii','ignore')
				h.div(choice,klass="Choice", value=str(k))
			h+=HTML('/div')
			pass

		h += HTML('/div')
		h += HTML('/body')
		h += HTML('/html')
		soup = bs(str(h))
		return soup.prettify()

# Example of what the input looks like
# p1 = Page("hello", 0,["Go Away","Go to Castle"])
# p2 = Page("Goodbye", 1,["Leave"])
# p3 = Page("I died ;_;", 2, [])
# s = Story("Bitches")

# Appends p1, p2, and p3 to the end of the pages array
# [s.pages.append(x) for x in (p1,p2,p3)]

# what = s.write_story()
# soup = bs(str(what))
# pretty = soup.prettify()

# with open("test.html","w+") as f:
# 	f.write(s.write_story())
