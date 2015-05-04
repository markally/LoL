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

    def get_comments(self, submission, root_only=True):
        """get and store comment objects from all submissions"""
        if root_only:
            submission.replace_more_comments(limit=0)
        else:
            submission.replace_more_comments(limit=None)

    def parse_submission_data(self, submission):
        """Returns a tuple of relevant submission data"""
        sub_id = submission.id
        subreddit_id = str(submission.subreddit)
        creation_date = submission.created_utc
        comment_count = submission.num_comments
        score = submission.score
        return (sub_id, subreddit_id, creation_date, comment_count, score)

    def build_submission_table(self):
        """Returns a list of all submission data for the patch"""
        submission_table = []
        for submission in self.submissions:
            data = self.parse_submission_data(submission)
            submission_table.append(data)
        return submission_table

    def build_comment_table(self):
        pass


