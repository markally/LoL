import requests

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import praw
from textblob import TextBlob

# Reddit patch sentiment analysis

class Patch:
	"""a class representing a LoL patch"""

	def __init__(self, patchurl, expanded=False):
		"""expanded = True returns all comments instead of top comments.
		Requires additional API calls"""
		self.url = patchurl
		self.expanded = expanded

	def SearchSubmissions(self):
		"""store a generator for submissions that match the url"""
		subreddit = "leagueoflegends"
		# praw isn't handling urls correctly, use url:'url' instead of just 'url'
		self.submissions = r.search('url:%s' % self.url, subreddit=subreddit)

	def GetComments(self):
		"""get and store comment objects from all submissions"""
		comments = []
		for submission in self.submissions:
			if self.expanded:
				submission.replace_more_comments()
				commentobjs = praw.helpers.flatten_tree(submission.comments)
				comments.extend([comment.body for comment in commmentobjs])
			else:
				submission.replace_more_comments(limit=0)
				comments.extend([comment.body for comment in submission.comments if comment.is_root])
		self.comments = comments
		self.commentcount = len(comments)

	def CalcSentiment(self):
		"""sets average sentiment and # of comments"""
		sentimentsum = 0
		if self.commentcount > 0:
			for comment in self.comments:
				text = TextBlob(comment)
				sentimentsum += text.sentiment.polarity
			self.sentiment = sentimentsum / self.commentcount
		else:
			self.sentiment = 0

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
	"""Scrape and clean elements of interest from row. Return as tuple."""
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
	"""Not functioning, not currently used."""
	index = np.arange(len(data))

	plt.bar(index, data)

	plt.xlabel("Patch ID")
	plt.ylabel("Average Sentiment per Comment")
	plt.title("/r/LeagueOfLegends Patch Sentiment Scores")
	plt.xticks(index +.4, xlabels, rotation="70")

	plt.show()

def main(url):
	"""Scrape the patch details from the LoL Wiki.
	Use Reddit API to access all the submissions pointing at each patch note URL.
	Collect root comments (all comments if expanded=True)
	Calculate average sentiment per patch, and add to table.
	Return a pandas DataFrame with all data.
	"""
	# Find patch IDs and links to official patch notes
	df = ScrapeTable(url)
	urls = df.Link.values
	urlcount = len(urls)
	# Get sentiment score for each patch, store
	patchsentiment = []
	for num, url in enumerate(urls):
		PatchObj = Patch(url)
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

	# Initialize PRAW
	# Praw has a build in rate limiter. 1 API call every 2 seconds.
	user_agent = ("LoL Patch Sentiment analysis 1.0 by /u/LivingInSloMo")
	r = praw.Reddit(user_agent=user_agent)

	result = main(url)
	result.to_csv('LoL Sentiment Scores', encoding='utf-8')
