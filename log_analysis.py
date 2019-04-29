#!/usr/bin/env python3
#
# Connect to database (while in the /vagrant directory) with:
#
#   psql -d news

import psycopg2
from datetime import datetime

"""
A reporting tool that prints out reports (in plain text) based on data in a
database. This reporting tool is a Python program using the psycopg2 module to
connect to the database.

What are we reporting?
1. What are the most popular three articles of all time?
   - Which articles have been accessed the most?
   - This information is presented as a sorted list with the most popular
     article at the top

2. Who are the most popular article authors of all time?
   - Which authors get the most page views?
   - This information is presented as a sorted list with the most popular
     author at the top

3. On which days did more than 1% of requests lead to errors?
   - This uses the 'status' column of the 'log' table which indicates the HTTP
     status code that the news site sent to the user's browser
"""
# Question 1: Most popular 3 articles
#
# This should give the number of views for each article:
#
#   select path, count(*) as views from log
#       group by path
#       order by views desc
#       offset 1 limit 8;
#
# This should result in:
#
#                    path                | views
#    ------------------------------------+--------
#     /article/candidate-is-jerk         | 338647
#     /article/bears-love-berries        | 253801
#     /article/bad-things-gone           | 170098
#     /article/goats-eat-googles         |  84906
#     /article/trouble-for-troubled      |  84810
#     /article/balloon-goons-doomed      |  84557
#     /article/so-many-bears             |  84504
#     /article/media-obsessed-with-bears |  84383
#
# Create this as a view:
#
#   create view article_views as
#       select path, count(*) as views from log
#           group by path
#           order by views desc
#           offset 1 limit 8;
#
# We also want to create a separate view from THIS view:
#
#   create view substr_title as
#       select substring(path, 10, 30) as path, views from article_views;
#
# This results in:
#
#                 path            | views
#      ---------------------------+--------
#       candidate-is-jerk         | 338647
#       bears-love-berries        | 253801
#       bad-things-gone           | 170098
#       goats-eat-googles         |  84906
#       trouble-for-troubled      |  84810
#       balloon-goons-doomed      |  84557
#       so-many-bears             |  84504
#       media-obsessed-with-bears |  84383
#
# And this just returns article titles with author id:
#
#   select author, title, slug from articles;
#
# This should result in:
#
#     author |               title                |         slug
#    --------+------------------------------------+--------------------------
#          3 | Bad things gone, say good people   | bad-things-gone
#          4 | Balloon goons doomed               | balloon-goons-doomed
#          1 | Bears love berries, alleges bear   | bears-love-berries
#          2 | Candidate is jerk, alleges rival   | candidate-is-jerk
#          1 | Goats eat Google's lawn            | goats-eat-googles
#          1 | Media obsessed with bears          | media-obsessed-with-bear
#          2 | Trouble for troubled troublemakers | trouble-for-troubled
#          1 | There are a lot of bears           | so-many-bears
#
# Create this as a view:
#
#   create view article_titles as
#       select author, title, slug from articles;
#
# Now we have a relationship between the two views article_titles and
# substr_title:
#
#   select title, views from article_titles, substr_title
#   where article_titles.slug = substr_title.path
#   order by substr_title.views desc;
#
# This results in the table:
#
#                      title                | views
#       ------------------------------------+--------
#       Candidate is jerk, alleges rival    | 338647
#       Bears love berries, alleges bear    | 253801
#       Bad things gone, say good people    | 170098
#       Goats eat Google's lawn             |  84906
#       Trouble for troubled troublemakers  |  84810
#       Balloon goons doomed                |  84557
#       There are a lot of bears            |  84504
#       Media obsessed with bears           |  84383
#
# To get the top 3 just limit this by 3 (our first query!):
#
#   select title, views from article_titles, substr_title
#   where article_titles.slug = substr_title.path
#   order by substr_title.views desc limit 3;
#
# Question 2: Most popular authors
#
# To make this a little easier, we make a view of the query from question 1:
#
#   create view popular_articles as
#       select title, views from article_titles, substr_title
#       where article_titles.slug = substr_title.path
#       order by substr_title.views desc;
#
# Since we have a view of article_titles, with their associated author IDs, we
# can join it with this new view (so as to include the author id with the most
# popular articles):
#
#   select author, article_titles.title as title, views
#   from article_titles, popular_articles
#   where article_titles.title = popular_articles.title order by views desc;
#
# This should return:
#
#    author |               title                | views
#   --------+------------------------------------+--------
#         2 | Candidate is jerk, alleges rival   | 338647
#         1 | Bears love berries, alleges bear   | 253801
#         3 | Bad things gone, say good people   | 170098
#         1 | Goats eat Google's lawn            |  84906
#         2 | Trouble for troubled troublemakers |  84810
#         4 | Balloon goons doomed               |  84557
#         1 | There are a lot of bears           |  84504
#         1 | Media obsessed with bears          |  84383
#
# We create a view from this:
#
#   create view popular_authors as
#      select author, article_titles.title as title, views
#      from article_titles, popular_articles
#      where article_titles.title = popular_articles.title order by views desc;
#
# We can now join this with the authors table to get a list of most popular
# authors:
#
#   select name, title, views from popular_authors, authors
#   where authors.id = popular_authors.author
#   order by views desc;
#
# This should return:
#
#             name          |               title                | views
#   ------------------------+------------------------------------+--------
#    Rudolf von Treppenwitz | Candidate is jerk, alleges rival   | 338647
#    Ursula La Multa        | Bears love berries, alleges bear   | 253801
#    Anonymous Contributor  | Bad things gone, say good people   | 170098
#    Ursula La Multa        | Goats eat Google's lawn            |  84906
#    Rudolf von Treppenwitz | Trouble for troubled troublemakers |  84810
#    Markoff Chaney         | Balloon goons doomed               |  84557
#    Ursula La Multa        | There are a lot of bears           |  84504
#    Ursula La Multa        | Media obsessed with bears          |  84383
#
# Creating a view from this:
#
#   create view top_authors as
#       select name, title, views from popular_authors, authors
#       where authors.id = popular_authors.author
#       order by views desc;
#
# From this view we return the most popular authors (with views included for
# convenience):
#
#   select name, max(views) as views from top_authors
#   group by name order by views desc;
#
# This query returns:
#
#             name          | views
#   ------------------------+--------
#    Rudolf von Treppenwitz | 338647
#    Ursula La Multa        | 253801
#    Anonymous Contributor  | 170098
#    Markoff Chaney         |  84557
#
# To just get the names we use (our second query!):
#
#   select name from top_authors group by name order by max(views) desc;
#
# Question 3: Which days were there more than 1% of errors
#
# First we find the total where status != '200 OK':
#
#   select cast(time as date) as date, count(*) as total,
#          cast(sum(cast(status != '200 OK' as int)) as float)
#   from log group by date;
#
# This should return:
#
#           date    | total | sum
#       ------------+-------+------
#        2016-07-01 | 38705 |  274
#        2016-07-02 | 55200 |  389
#        2016-07-03 | 54866 |  401
#        2016-07-04 | 54903 |  380
#        2016-07-05 | 54585 |  423
#        2016-07-06 | 54774 |  420
#        2016-07-07 | 54740 |  360
#        2016-07-08 | 55084 |  418
#        2016-07-09 | 55236 |  410
#        2016-07-10 | 54489 |  371
#        2016-07-11 | 54497 |  403
#        2016-07-12 | 54839 |  373
#        2016-07-13 | 55180 |  383
#        2016-07-14 | 55196 |  383
#        2016-07-15 | 54962 |  408
#        2016-07-16 | 54498 |  374
#        2016-07-17 | 55907 | 1265
#        2016-07-18 | 55589 |  374
#        2016-07-19 | 55341 |  433
#        2016-07-20 | 54557 |  383
#        2016-07-21 | 55241 |  418
#        2016-07-22 | 55206 |  406
#        2016-07-23 | 54894 |  373
#        2016-07-24 | 55100 |  431
#        2016-07-25 | 54613 |  391
#        2016-07-26 | 54378 |  396
#        2016-07-27 | 54489 |  367
#        2016-07-28 | 54797 |  393
#        2016-07-29 | 54951 |  382
#        2016-07-30 | 55073 |  397
#        2016-07-31 | 45845 |  329
#
# We create a view out of this:
#
#   create view errors as
#       select cast(time as date) as date, count(*) as total,
#          cast(sum(cast(status != '200 OK' as int)) as float)
#       from log group by date;
#
# Then we generate our query:
#
#   select date, sum/total * 100 as percentage from errors
#   where sum/total > 0.01;
#
# This returns:
#
#   2016-07-17 | 2.26268624680273

try:
    # Connect to database
    db = psycopg2.connect("dbname='news'")

    # Make a cursor object
    cur = db.cursor()

    # Views
    view1 = """
        select * from article_titles;
    """

    view2 = """
        select * from substr_title;
    """

    view3 = """
        select * from top_authors;
    """

    view4 = """
        select * from errors;
    """

    # Queries
    query1 = """
        select title, views from article_titles, substr_title
        where article_titles.slug = substr_title.path
        order by substr_title.views desc limit 3;
    """

    query2 = """
        select name from top_authors group by name order by max(views) desc;
    """

    query3 = """
        select date, sum/total * 100 as percentage from errors
        where sum/total > 0.01;
    """
    # Execute Views
    cur.execute(view1)

    article_titles = cur.fetchall()

    cur.execute(view2)

    substr_title = cur.fetchall()

    cur.execute(view3)

    top_authors_data = cur.fetchall()

    cur.execute(view4)

    error_data = cur.fetchall()

    # Execute Query 1
    cur.execute(query1)

    top_three = cur.fetchall()

    # Execute Query 2
    cur.execute(query2)

    top_authors = cur.fetchall()

    # Execute Query 3
    cur.execute(query3)

    error = cur.fetchall()

    # Close connection
    db.close()
    print("The Associated Views:")
    print("Article Titles: (id, title, slug)")
    for title in article_titles:
        print(title)

    print("\nSubstring Titles: (title, views)")
    for short in substr_title:
        print(short)

    print("\nTop Authors: (name, title, views)")
    for author in top_authors_data:
        print(author)

    print("\nErrors: (date, total, sum)")
    for error in error_data:
        print(datetime.strftime(error[0],'%b/%d/%Y'), error[1], error[2])

    print("\nTop 3 Articles:")
    for title in top_three:
        print(title[0])

    print("\nTop Authors:")
    for author in top_authors:
        print(author[0])

    print("\nDate Where Error > 1%:")
    print(datetime.strftime(error[0], '%b/%d/%Y'))

except Exception as e:
    print(e)
