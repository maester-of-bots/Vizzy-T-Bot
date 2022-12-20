from datetime import *
from modules.cloud_sql import *

cloud_db = db()

def get_gen_len(gen):
    x = 0
    ffp = 0
    for thing in gen:
        if thing.subreddit.display_name == 'freefolk':
            ffp += 1

        x += 1
    return ffp, x

def check_post(post, sub):
    query = post.title

    seen = []

    for exPost in sub.search(query):
        if exPost.title == query and exPost.id != post.id:
            seen.append(f'https://www.reddit.com{exPost.permalink}')

    if seen and not cloud_db.check_db(post.id, 'spam'):

        author_detail = check_user(post.author)

        if author_detail is not True:
            response = author_detail + "\n\nFound these similar posts:\n\n" + "\n".join(
                seen) + "\n\nPlease reach out to u/SOBER-Lab if this is an error.  If OP actually responds to this comment, they might be a real account."


            report = f"This is an exact repost, the title has been seen {len(seen)} times before and the account is new."

            return response, report
        else:
            return True
    else:
        return True


def check_user(author):

    # Data for the author's account

    created = author.created_utc

    now = datetime.now().timestamp()

    account_age = int(((now - created) / 60 / 60 / 24))

    if account_age > 365:

        return True

    # Data for the author's karma

    comment_karma = author.comment_karma

    post_karma = author.link_karma

    total_karma = comment_karma + post_karma

    if total_karma > 1500:

        return True

    # Data for the author's activity

    comment_count = author.comments.new(limit=None)

    comments_freefolk, comments_all = get_gen_len(comment_count)

    posts_count = author.submissions.new(limit=None)

    posts_freefolk, posts_all = get_gen_len(posts_count)

    freefolk_activity = comments_freefolk + posts_freefolk

    if freefolk_activity > 5:

        return True

    all_activity = comments_all + posts_all

    if all_activity > 15:

        return True

    else:

        response = f"""This account is probably a karma-grubbing repost-bot.

Account Age:  {account_age} days

Number of Comments in r/FreeFolk:  {comments_freefolk}

Number of Posts in r/FreeFolk:  {posts_freefolk}

Total Comment Karma:  {comment_karma}

Total Post Karma:  {post_karma}

Total Combined Instances of Activity:  {all_activity}

Account Age:  {account_age}"""

        return response
