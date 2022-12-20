from sql import *

def debug(comment):
    '''This executes when Steve comments saying "Why didn't you respond here, Vizzy?"'''

    parent = comment.parent()

    parent.refresh()

    in_db = checkDB(parent.id)

    if in_db:

        parent.replies.replace_more()

        child_comments = parent.replies.list()

        for child_comment in child_comments:
            if child_comment.author.name.lower() == "vizzy_t_bot":
                url = f"https://www.reddit.com{child_comment.permalink}"
                reply = f"[It's right here, smartass.]({url})"
                comment.reply(body=reply)
                return
    else:

        user_text, residual_sentience = comment_processer(parent)

        is_triggered = triggered(user_text)

        is_depleted = parent.id in getCommentsdwarf()

        report = f"Comment by {parent.author.name}\n\nResidual Sentience: {str(residual_sentience)}\n\nComment ID in response database: {str(in_db)}\n\nComment ID in depleted database: {str(is_depleted)}\n\nTriggered? {str(is_triggered)}\n\n"

        if not residual_sentience and not is_triggered:
            note = "*This comment did not contain trigger words, and was not a reply to a comment with residual sentience.*"
        elif residual_sentience and is_depleted and not is_triggered:
            note = "*This comment did not contain trigger words.  It was a reply to a comment that had residual sentience, but it was used by another Redditor.*"
        else:
            note = "*I am not sure why this comment was not processed, sorry.  Would you like to see the tapestries?*"

        final = report + note

        comment.reply(body=final)