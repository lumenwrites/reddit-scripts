import praw
import pickle
import datetime
import dateutil.relativedelta

def timestamp_to_age(timestamp):
    dt1 = datetime.datetime.fromtimestamp(timestamp)
    dt2 = datetime.datetime.now()
    rd = dateutil.relativedelta.relativedelta(dt2, dt1)
    age =  "%d days, %d hours" % (rd.days, rd.hours)
    return age

def timestamp_to_days(timestamp):
    dt1 = datetime.datetime.fromtimestamp(timestamp)
    dt2 = datetime.datetime.now()
    rd = dateutil.relativedelta.relativedelta(dt2, dt1)
    return rd.days




r = praw.Reddit(user_agent='Best /r/WritingPrompts authors by /u/raymestalez')
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

    # Pickle doesn't work
    # with open("top_posts.pck", "wb") as f:
    #     pickle.dump(list(top_posts),f)
    # print("Posts dumped!")
    # print(top_posts[0].comments[0].body)
    
    # with open("top_posts.pck", "rb") as f:        
    #     top_posts = pickle.load(f)        
    # print("Posts loaded!")
    # print(top_posts[0].comments[0].body)
          
    return top_posts

def get_top_comments(top_posts, limit=2500):
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

def calculate_karma(authors, limit=500):
    # Loop through each author's comments, calculate their combined /r/WritingPrompts karma
    authorsdata = []
    numberofauthors = len(authors)
    for index, author in enumerate(authors):
        author.wpscore = 0
        author.beststories = []

        upvotedstories = 0
        comments = author.get_comments(sort=u'top', time=u'all', limit=limit)

        # Combine stories score, collect the best stories.
        for comment in comments:
            if comment.subreddit.display_name == "WritingPrompts" and comment.is_root:
                author.wpscore += comment.score
                author.beststories.append(comment)
                if comment.score > 100:
                    upvotedstories += 1

        # Last time he was active on reddit
        lastcomment = list(author.get_comments(sort=u'new', time=u'all', limit=1))[0]
        author.lastactive = timestamp_to_age(lastcomment.created_utc) + " ago"

        # Last WP story
        recentcomments = list(author.get_comments(sort=u'new', time=u'all', limit=limit))
        for comment in recentcomments:
            if comment.subreddit.display_name == "WritingPrompts" and comment.is_root:
                author.laststory = timestamp_to_age(comment.created_utc) + " ago"
                break
            else:
                author.laststory = ""

        #  or timestamp_to_days(lastcomment.created_utc) > 30
        if len(author.beststories) > 10 and upvotedstories > 3:
            authorsdata.append(author)
        

        print("/r/WPs karma calculated: " + author.name + " - " + str(author.wpscore) + " " + str(index) + "/" + str(numberofauthors))

    print("All karma calculated.")
    print("Total authors: " + str(len(authorsdata)))
    # print("Test: " + authors[0].name + " " + str(authors[0].wpscore))

    # Sort authors by their /r/WritingPrompts karma
    sorted_authors = sorted(authorsdata, key=lambda x: x.wpscore, reverse=True)
    sorted_authors = sorted_authors[:100]
    print("Authors sorted!")
    
    return sorted_authors





def write_authors_to_file(sorted_authors):
    filename = "/home/ray/projects/reddit-scrpts/top_authors.md"
    metadata = "Title: Top authors\nSlug: leads\nDate: 2016-06-08\n\n"
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
        finalstring += "Karma: " + wpscore +  "  \nStories written: " + str(len(author.beststories)) + "  \nLatest story written: " + author.laststory + "  \nLast active on reddit: " + author.lastactive + "  \n\n"
        finalstring += best_stories_string + "\n\n----\n\n"
        print("Added to file: " + "[" + wpscore + "] " +  author.name + str(index) + "/" + str(len(sorted_authors)))
        with open(filename, "a") as text_file:
            text_file.write(finalstring)
        


def test():            
    top_posts = get_top_posts(limit=5)
    sorted_comments = get_top_comments(top_posts, limit=20)
    authors = extract_authors(sorted_comments)
    sorted_authors = calculate_karma(authors, limit=50)
    write_authors_to_file(sorted_authors)            
    # Don't accidentally override author's file!!


# def try_until_works(function):
#     while True:
#         try:
#             finction()
#             break
#         except urllib2.HTTPError, e:
#             if e.code in [429, 500, 502, 503, 504]:
#                 print "Reddit is down (error %s), sleeping..." % e.code
#                 time.sleep(60)
#                 pass
#             else:
#                 raise
#         except Exception, e:
#             print "couldn't Reddit: %s" % str(e)
#             raise
        
def final():
    while True:
        try:
            top_posts = get_top_posts()
            break
        except:
            print("Error. Reddit is down, trying again...")


    while True:
        try:
            sorted_comments = get_top_comments(top_posts)
            break
        except:
            print("Error. Reddit is down, trying again...")
            
    
    while True:
        try:
            authors = extract_authors(sorted_comments)
            break
        except:
            print("Error. Reddit is down, trying again...")            
            
    
    while True:
        try:
            sorted_authors = calculate_karma(authors)
            break
        except:
            print("Error. Reddit is down, trying again...")                        
            
    
    while True:
        try:
            write_authors_to_file(sorted_authors)            
            break
        except:
            print("Error. Reddit is down, trying again...")                                    
            
    
    # Don't accidentally override author's file!!

# test()
# final()

