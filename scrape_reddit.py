# Scrape Reddit for Patch Note submissions, and store all comment data
import pandas as pd
import praw

class Patch:
    """a class representing a LoL patch"""
    
    # Initialize PRAW
    # Praw has a build in rate limiter. 1 API call every 2 seconds.
    user_agent = ("LoL Patch Sentiment analysis 1.0 by /u/LivingInSloMo")
    r = praw.Reddit(user_agent=user_agent)

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

    def get_comments(self, submission, root_only):
        """
        Replaces MoreComment objects with Comment objects.
        Returns list of objects."""
        if root_only:
            # Iterate through root comments replacing MoreComment objects
            # API is the rate limiter, not loop time
            while praw.objects.MoreComments in submission.comments:
                for i, comment in enumerate(submission.comments):
                    if type(comment) == praw.objects.MoreComments:
                        submission.comments.extend(submission.comments.pop[i].comments())
            return submission.comments
        else:
            submission.replace_more_comments(limit=None)
            commentobjs = praw.helpers.flatten_tree(submission.comments)
            return commentobjs

    def parse_comment_data(self, comment):
        """Returns a tuple of relevant comment data"""
        comment_id = comment.id
        parent_id = comment.parent_id
        submission_id = comment.submission.id
        subreddit_id = str(comment.subreddit)
        creation_date = comment.created_utc
        score = comment.score
        controversiality = comment.controversiality
        text = comment.body
        return (
            comment_id,
            parent_id,
            submission_id,
            subreddit_id,
            creation_date,
            score,
            controversiality,
            text)

    def build_comment_table(self, root_only=True):
        comment_table = []
        for submission in self.submissions:
            comments = self.get_comments(submission)
            for comment in comments:
                data = self.parse_comment_data(comment)
                comment_table.append(data)
        return comment_table

    def collect_all(self, root_only=True):
        """collect all data and return submission and comment table"""
        self.search_submissions()
        submission_table = build_submission_table()
        comment_table = build_comment_table(root_only)
        return submission_table, comment_table




