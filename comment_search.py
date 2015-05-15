# Scrape Reddit for Patch Note submissions, and store all comment data
import pandas as pd
import praw

# Initialize PRAW
# Praw has a build in rate limiter. 1 API call every 2 seconds.
user_agent = ("LoL Patch Sentiment analysis 1.0 by /u/LivingInSloMo")
r = praw.Reddit(user_agent=user_agent)

class Patch:
    """a class representing a LoL patch"""

    def __init__(self, patch_id, patch_url):
        """root_only will return only top-level comments"""
        self.patch_id = patch_id
        self.url = patch_url
        self.submissions = None

    def search_submissions(self):
        """store a generator for submissions that match the url"""
        subreddit = "leagueoflegends"
        # praw isn't handling urls correctly, use url:'url' instead of just 'url'
        submission_generator = r.search('url:%s' % self.url, subreddit=subreddit)
        self.submissions = [sub_obj for sub_obj in submission_generator]

    def get_comments(submission, root_only=True):
        """get and store comment objects from all submissions"""
        if root_only:
            submission.replace_more_comments(limit=0)
        else:
            submission.replace_more_comments(limit=None)

    def parse_submission_data(submission):
        """Returns a tuple of relevant submission data"""
        sub_id = sub.id
        subreddit_id = sub.subreddit  
        creation_date = sub.created_utc
        comment_count = sub.num_comments
        score = sub.score
        return (sub_id, subreddit_id, creation_date, score, comment_count)

    def build_submission_table(self):
        sub_id = s




    def Run(self):
        """
        Searches for submissions matching patch
        Gets comments (root_only=True expands deeper in to threads)
        """
        self.SearchSubmissions()
        self.GetComments()
        self.CalcSentiment()

