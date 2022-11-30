from datetime import *
from sentience import *



def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results


def isPost(obj):
    return isinstance(obj,praw.models.Submission)

def isComment(obj):
    return isinstance(obj,praw.models.Comment)

def triggered(text):
    return "vizzy t" in text or "vissy t" in text


def checkTime(obj):
    time = obj.created
    timestamp = datetime.fromtimestamp(time)
    # print(timestamp)
    if (datetime.now() - timedelta(hours=7)) < timestamp:
        return True
    else:
        # print("Skipping old comment.")
        return False


