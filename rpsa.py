import requests

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import praw
from textblob import TextBlob

# Would it be better to only look at root comments?
# Reddit patch sentiment analysis

# LoL Wiki URL to scrape patch IDs and patch notes URLs
url = "http://leagueoflegends.wikia.com/wiki/Patch"
user_agent = ("LoL Patch Sentiment analysis 1.0 by /u/LivingInSloMo")

# Initialize PRAW
r = praw.Reddit(user_agent=user_agent)

class Patch:
	"""a class representing a LoL patch"""

	def __init__(self, patchurl, expanded=False):
		self.url = patchurl
		self.expanded = expanded

	def SearchSubmissions(self):
		"""store a generator for submissions that match the url"""
		subreddit = "leagueoflegends"
		self.submissions = r.search(self.url, subreddit=subreddit)

	def GetComments(self):
		"""get and store comment objects from all submissions"""
		comments = []
		for submission in self.submissions:
			if self.expanded:
				submission.replace_more_comments()
			flatlist = praw.helpers.flatten_tree(submission.comments)
			for singlecomment in flatlist:
				comments.append(singlecomment)
		self.comments = comments

	def CalcSentiment(self):
		"""sets average sentiment and # of comments"""
		commentcount = 0
		sentimentsum = 0
		for comment in self.comments:
			commentcount += 1
			text = TextBlob(comment.body)
			sentimentsum += text.sentiment.polarity
		if commentcount > 0:
			self.sentiment = sentimentsum / commentcount
			self.commentcount = commentcount
		else:
			self.sentiment = 0
			self.commentcount = commentcount

	def Run(self):
		"""
		Searches for submissions matching patch
		Gets comments (expanded=True expands deeper in to threads)
		Calcs and returns an average sentiment score for the patch.
		"""
		self.SearchSubmissions()
		self.GetComments()
		self.CalcSentiment()

def ParseLoLWikiRow(row):
	patch = row[0].text.strip()
	date = row[1].text.strip()
	new_champion = row[2].text.strip()
	other = row[3].text.strip()
	link = row[4].find("a")["href"].strip()
	parsed_row = (patch, date, new_champion, other, link)
	return parsed_row


def ParseTable(table):
	"""Return tuple of parsed data"""
	parsedtable = []
	headers = table.find_all("th")
	tablewidth = len(headers)
	columnnames = [h.text.strip() for h in headers]
	rows = table.find_all("tr")
	for row in rows:
		data = row.find_all("td")
		if data:
			parsedtable.append(ParseLoLWikiRow(data))
	return parsedtable, columnnames


def ScrapeTable(url):
	"""Scrape website for the patch table and return it as a DataFrame"""
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data, "html.parser")

	table = soup.find("table", class_="wikitable")
	parsedtable, headers = ParseTable(table)
	return pd.DataFrame(data = parsedtable, columns = headers)

def Plot(data, xlabels):
	index = np.arange(len(data))

	plt.bar(index, data)

	plt.xlabel("Patch ID")
	plt.ylabel("Average Sentiment per Comment")
	plt.title("/r/LeagueOfLegends Patch Sentiment Scores")
	plt.xticks(index +.4, xlabels, rotation="70")

	plt.show()

def main(url):

	# Find patch IDs and links to official patch notes
	df = ScrapeTable(url)
	urls = df.Link.values
	urlcount = len(urls)
	# Get sentiment score for each patch, store
	patchsentiment = []
	for num, url in enumerate(urls):
		PatchObj = Patch(url, expanded=True)
		PatchObj.Run()
		patchsentiment.append(PatchObj.sentiment)
		print PatchObj.sentiment
		print 'On patch %s of %s' % (num, urlcount)
		temp = pd.DataFrame(patchsentiment)
		temp.to_csv('Temp Sentiments')

	df['Sentiment'] = patchsentiment
	return df

if __name__ == '__main__':
	# LoL Wiki URL to scrape patch IDs and patch notes URLs
	url = "http://leagueoflegends.wikia.com/wiki/Patch"
	user_agent = ("LoL Patch Sentiment analysis 1.0 by /u/LivingInSloMo")

	# Initialize PRAW
	r = praw.Reddit(user_agent=user_agent)
	result = main(url)
	result.to_csv('LoL Sentiment Scores')
