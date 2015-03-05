import re
import requests

import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import praw
from textblob import TextBlob
from pymongo import MongoClient
import pandas as pd

# Would it be better to only look at root comments?
# Reddit patch sentiment analysis

# LoL Wiki URL to scrape patch IDs and patch notes URLs
url = "http://leagueoflegends.wikia.com/wiki/Patch"

# Initialize PRAW
user_agent = ("LoL Patch Sentiment analysis 1.0 by /u/LivingInSloMo")
r = praw.Reddit(user_agent=user_agent)

# Initialize MongoDB for result storage
client = MongoClient()
db = client.LoL
collection = db.LoLPatchSentiment

class Patch:
	"""a class representing a LoL patch"""

	def __init__(self, patchID, url):
		self.patchID = patchID
		self.url = url

	def SearchSubmissions(self):
		"""store a generator for submissions that match the url"""
		subreddit = "leagueoflegends"
		self.submissions = r.search(self.url, subreddit=subreddit)

	def GetComments(self, expanded):
		"""get and store comment objects from all submissions"""
		comments = []
		for submission in self.submissions:
			if expanded:
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

	def Run(self, expanded):
		"""
		Searches for submissions matching patch
		Gets comments (expanded=True expands deeper in to threads)
		Calcs and returns an average sentiment score for the patch.
		"""
		self.SearchSubmissions()
		self.GetComments(expanded)
		self.CalcSentiment()

def ParseRow(row):
	"Checks if the row has data, and returns parsed data if it does"
	columns = row.find_all("td")
	if columns:
		patch = columns[0].text
		date = columns[1].text
		new_champion = columns[2].text
		other = columns[3].text
		link = columns[4].find("a")["href"]
		parsed_row = (patch, date, new_champion, other, link)
		return parsed_row

def ScrapeTable(url):
	"""Scrape website for the patch table and return it as a DataFrame"""
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data)
	wikidata = []

	table = soup.find("table", class_="wikitable")
	rows = table.find_all("tr")
	for row in rows:
		wikidata.append(ParseRow(row))
	return pd.DataFrame(wikidata)

def Plot(data, xlabels):
	index = np.arange(len(data))

	plt.bar(index, data)

	plt.xlabel("Patch ID")
	plt.ylabel("Average Sentiment per Comment")
	plt.title("/r/LeagueOfLegends Patch Sentiment Scores")
	plt.xticks(index +.4, xlabels, rotation="70")

	plt.show()

def main():

	# Find patch IDs and links to official patch notes
	patchtable = ScrapeTable(url)

	# Get sentiment score for each patch, store
	patchsentiment = []
	for patchID in links.keys():
		PatchObj = Patch(patchID, links[patchID])
		PatchObj.Run(True)
		patchsentiment.append([PatchObj.patchID, PatchObj.sentiment])
		collection.insert({
			"patch": PatchObj.patchID, 
			"sentiment": PatchObj.sentiment,
			"commentcount": PatchObj.commentcount
			})
		print PatchObj.patchID, PatchObj.sentiment

	collection.insert({"final": patchsentiment})

	# Plot Sentiments
	data = np.matrix(patchsentiment)
	data_asarray = np.asarray(data)
	Plot(patchsentiment)

if __name__ == '__main__':
		main()