import praw
import datetime
import dateutil.relativedelta

def timestamp_to_age(timestamp):
    dt1 = datetime.datetime.fromtimestamp(timestamp)
    dt2 = datetime.datetime.now()
    rd = dateutil.relativedelta.relativedelta (dt2, dt1)
    age =  "%d days, %d hours" % (rd.days, rd.hours)
    return(age)


r = praw.Reddit(user_agent='Best /r/WritingPrompts stories by /u/raymestalez')
subreddit = r.get_subreddit('writingprompts')

def testing():
    user = r.get_redditor('raymestalez')
    user.wpscore = 0
    user.beststories = []
    comments = user.get_comments(sort=u'new', time=u'all', limit=1)
    c = list(comments)[0]
    print(timestamp_to_age(c.created_utc))
    
    
    print(c.parent_id)
    print(c.link_title)
    for comment in comments:
        if comment.subreddit.display_name == "WritingPrompts":
            user.wpscore += comment.score
            user.beststories.append(comment)
            print(comment._submission.url)
    print(user.wpscore)
    
    best_stories_string = ""
    for story in user.beststories:
        storyurl = story._submission.url
        storyprompt = story._submission.title
        storystring = " [" + storyprompt + "](" + storyurl + ")  \n"
        best_stories_string += storystring
        print(best_stories_string)        
        




# Grab top posts
def get_top_posts(limit=1000):
    top_posts=list(r.get_subreddit('writingprompts').get_top_from_all(limit=limit))
    print("Posts fetched!")

    return top_posts

def get_top_comments(top_posts, limit=1500):
    # Put all their comments in one list
    all_comments = []
    number_of_posts = len(top_posts)
    for index, post in enumerate(top_posts):
        real_comments = [c for c in post.comments if isinstance(c, praw.objects.Comment)]
        # great_comments = [c for c in real_comments if c.score > 1000]
        all_comments += real_comments # great_comments
        print("Added comments from post: " + str(index) + "/" + str(number_of_posts))

    # Sort comments
    sorted_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)
    sorted_comments = sorted_comments[:limit]
    print("Comments sorted!")

    return sorted_comments


def extract_authors(comments):
    authors = []
    number_of_comments = len(comments)
    # Put authors of all comments into one list
    for index, comment in enumerate(comments):
        try:
            if not comment.author in authors:
                print("Added to authors: " + comment.author.name + " " + str(index) + "/" + str(number_of_comments))
                authors.append(comment.author)
        except:
            pass


    print("Authors extracted!")
    return authors

def calculate_karma(authors, limit=100):
    # Loop through each author's comments, calculate their combined /r/WritingPrompts karma 
    for author in authors:
        author.wpscore = 0
        author.beststories = []

        comments = author.get_comments(sort=u'top', time=u'all', limit=limit)
        for comment in comments:
            if comment.subreddit.display_name == "WritingPrompts" and comment.is_root:
                # If it's a top-level /r/WPs reply, append it's score,
                # and add it to author's best stories
                author.wpscore += comment.score
                author.beststories.append(comment)
    
        lastcomment = list(author.get_comments(sort=u'new', time=u'all', limit=1))[0]
        author.lastactive = timestamp_to_age(lastcomment.created_utc) + " ago"

        # Last WP story
        # recentcomments = list(author.get_comments(sort=u'new', time=u'all', limit=limit))
        # for comment in recentcomments:
        #     if comment.subreddit.display_name == "WritingPrompts" and comment.is_root:
        #         author.lastactive = timestamp_to_age(comment.created_utc) + " ago"
        #         break

        print("/r/WPs karma calculated: " + author.name + " - " + str(author.wpscore))

    # Sort authors by their /r/WritingPrompts karma
    sorted_authors = sorted(authors, key=lambda x: x.wpscore, reverse=True)
    sorted_authors = sorted_authors[:500]
    print("Authors sorted!")
    
    return sorted_authors





def write_authors_to_file(sorted_authors):
    filename = "/home/ray/projects/wp-book/top_authors.md"
    filename = "/home/ray/projects/orangemind/content/pages/top_authors.md"
    metadata = "Title: Top authors\nSlug: top-authors\nDate: 2016-06-08\n\n"
    metadata += "<style>a{color:black;}</style>"
    with open(filename, "w") as text_file:
        text_file.write(metadata)
    
    for index, author in  enumerate(sorted_authors):
        indexstring = str(index+1)+"." 
        username = author.name
        authorurl = "["+username+ "](https://www.reddit.com/user/" + username + "/comments/?sort=top)"  
        wpscore = str(author.wpscore)
    
        best_stories_string = "Best stories:  \n\n"
    
        for index, story in enumerate(author.beststories[:5]):
            storyurl = story.permalink # link_url
            storyprompt = story.link_title
            storystring = str(index)+". [" + storyprompt + "](" + storyurl + ")  \n"
            best_stories_string += storystring
        
        finalstring = "#### " + indexstring + authorurl + "  \n"
        finalstring += "Karma: " + wpscore + "  \nLast active: " + author.lastactive + "  \n\n"
        finalstring += best_stories_string + "\n\n----\n\n"
        print("Added to file: " + "[" + wpscore + "] " +  author.name)
        with open(filename, "a") as text_file:
            text_file.write(finalstring)
        
def write_stories_to_file(sorted_comments):
    # incomplete
    filename = "/home/ray/projects/wp-book/top_stories.md"
    filename = "/home/ray/projects/orangemind/content/pages/top_stories.md"
    metadata = "Title: Top stories\nSlug: top-stories\nDate: 2016-06-08\n\n"
    metadata += "<style>a{color:black;}</style>"
    with open(filename, "w") as text_file:
        text_file.write(metadata)
    
    for comment in sorted_comments[:100]:
        prompt = "# " + comment._submission.title + "\n\n"
        score = "Score: " + str(comment.score) + "\n\n"
        try:
            username = comment.author.name            
            author = "["+username+ "](https://www.reddit.com/user/" + username + "/comments/?sort=top)"              
        except:
            author = ""

        storyurl = comment.permalink
        storyprompt = comment.link_title
        titlestring = "#### [" + storyprompt + "](" + storyurl + ")  \n"            
        # url = " [Story url]("+comment.permalink+") "
        
        body = comment.body + "\n\n----\n\n" + author + "\n\n" + url + "\n\n----\n\n"
        story = titlestring + score + author + body
        with open(filename, "a") as text_file:
            text_file.write(story)
    
        with open(filename, "a") as text_file:
            text_file.write(finalstring)
        


top_posts = get_top_posts()
sorted_comments = get_top_comments(top_posts)
authors = extract_authors(sorted_comments)
sorted_authors = calculate_karma(authors)
write_authors_to_file(sorted_authors)            
# Don't accidentally override author's file!!
