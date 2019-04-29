# Logs Analysis

This project is an internal reporting tool required for Udacity's Full Stack Nanodegree Program. Using information from a PostgreSQL database, it prints out a report in plain text:
1. The most popular three articles of all time
2. The most popular authors of all time
3. The date in which more than 1% of requests lead to errors

## Getting Started

My operating system is a Mac so the installation instructions reflect this system. The code editor used was Atom. Most of the files and configurations were provided by Udacity.

### Installing Git

Git is already installed on MacOS, but these instructions are to ensure we have the latest version:

1. go to [https://git-scm.com/downloads](https://git-scm.com/downloads)
2. download the software for Mac
3. install Git choosing all the default options

Once everything is installed, you should be able to run `git` on the command line. If usage information is displayed, we're good to go!

### Configuring Mac's Terminal (OPTIONAL)

Git can be used without reconfiguring the terminal but doing so makes it easier to use.

To configure the terminal, perform the following:

1. download [udacity-terminal-config.zip](http://video.udacity-data.com.s3.amazonaws.com/topher/2017/March/58d31ce3_ud123-udacity-terminal-config/ud123-udacity-terminal-config.zip)
2. Move the `udacity-terminal-config` directory to the directory of your choice and name it `.udacity-terminal-config`(Note the dot in front)
3. Move the `bash-profile` to the same directory as in `step 2` and name it `.bash_profile`(Note the dot in front)
    * If you already have a `.bash_profile` file in your directory, transfer the content from the downloaded `bash_profile` to the existing `.bash_profile`

**Note:** It's considerably easier to just use
`mv bash_profile .bash_profile`
and `mv udacity-terminal-config .udacity-terminal-config`
when moving and renaming these files in order to avoid mac system errors

### First Time Git Configuration
Run each of the following lines on the command line to make sure everything is set up.
```
# sets up Git with your name
git config --global user.name "<Your-Full-Name>"

# sets up Git with your email
git config --global user.email "<your-email-address>"

# makes sure that Git output is colored
git config --global color.ui auto

# displays the original state in a conflict
git config --global merge.conflictstyle diff3

git config --list
```

### Git & Code Editor

The last step of configuration is to get Git working with your code editor. Below is the configuration for Atom. If you use a different editor, then do a quick search on Google for "associate X text editor with Git" (replace the X with the name of your code editor).
```
git config --global core.editor "atom --wait"
```

### Install Virtual Box

VirtualBox is the software that actually runs the virtual machine. Download it [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1). Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

### Install Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. Download it [here](https://www.vagrantup.com/downloads.html). Install the version for your operating system.

If vagrant is successfully installed, you will be able to run `vagrant --version` in the terminal to see the version number.

### Download VM configuration

Download [FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip). This will give you a directory called **FSND-Virtual-Machine**.

Alternatively you can fork the repo [https://github.com/udacity/fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) on Github.

Change to this newly downloaded directory using `cd` in the terminal. Change to the `vagrant`
directory inside.

### Starting the Virtual Machine

From your terminal, inside the vagrant subdirectory, run the command `vagrant up`. Vagrant will download the Linux operating system and install it. This may take quite a while (many minutes) depending on how fast your Internet connection is.

When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM!

### Logged In

If you are now looking at a shell prompt that starts with the word `vagrant` congratulations — you've gotten logged into your Linux VM.

### Download the data

Next, [download the data](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip). You will need to unzip this file after downloading it. The file inside is called `newsdata.sql`. Put this file into the `vagrant` directory, which is shared with your virtual machine.

To build the reporting tool, you'll need to load the site's data into your local database.

To load the data, `cd` into the `vagrant` directory and use the command `psql -d news -f newsdata.sql`.

Running this command will connect to your installed database server and execute the SQL commands in the downloaded file, creating tables and populating them with data.

#### Errors

Getting an error? If the command gives an error message, such as --

```
psql: FATAL: database "news" does not exist

psql: could not connect to server: Connection refused
```

-- this means the database server is not running or is not set up correctly. To correct this, download the virtual machine and start again.

## Version

This project uses `Python 3`

## Creating Views

In order to make our reporting more approachable we're going to create views in the `news` database

### Most Popular Three Articles

First we create a view detailing articles with their view numbers:

```
create view article_views as
    select path, count(*) as views from log
    group by path
    order by views desc
    offset 1 limit 8;
```

This view should return the table:

```
                    path                | views
    ------------------------------------+--------
     /article/candidate-is-jerk         | 338647
     /article/bears-love-berries        | 253801
     /article/bad-things-gone           | 170098
     /article/goats-eat-googles         |  84906
     /article/trouble-for-troubled      |  84810
     /article/balloon-goons-doomed      |  84557
     /article/so-many-bears             |  84504
     /article/media-obsessed-with-bears |  84383
```

Further, we want to create a view from THIS view which extracts the article title from the path:

```
create view substr_title as
    select substring(path, 10, 30) as path, views from article_views;
```

Which should return:

```
                 path            | views
      ---------------------------+--------
       candidate-is-jerk         | 338647
       bears-love-berries        | 253801
       bad-things-gone           | 170098
       goats-eat-googles         |  84906
       trouble-for-troubled      |  84810
       balloon-goons-doomed      |  84557
       so-many-bears             |  84504
       media-obsessed-with-bears |  84383
```

Finally we create a view that returns the article titles with author id's:

```
create view article_titles as
    select author, title, slug from articles;
```

This view should return:

```
 author |               title                |         slug
--------+------------------------------------+--------------------------
      3 | Bad things gone, say good people   | bad-things-gone
      4 | Balloon goons doomed               | balloon-goons-doomed
      1 | Bears love berries, alleges bear   | bears-love-berries
      2 | Candidate is jerk, alleges rival   | candidate-is-jerk
      1 | Goats eat Google's lawn            | goats-eat-googles
      1 | Media obsessed with bears          | media-obsessed-with-bear
      2 | Trouble for troubled troublemakers | trouble-for-troubled
      1 | There are a lot of bears           | so-many-bears
```

### Most Popular Authors

To make this easier, we make a view using information from the most popular three articles:

```
create view popular_articles as
    select title, views from article_titles, substr_title
    where article_titles.slug = substr_title.path
    order by substr_title.views desc;
```

This generates the table:

```
              title                | views  
-----------------------------------+--------
Candidate is jerk, alleges rival   | 338647
Bears love berries, alleges bear   | 253801
Bad things gone, say good people   | 170098
Goats eat Google's lawn            |  84906
Trouble for troubled troublemakers |  84810
Balloon goons doomed               |  84557
There are a lot of bears           |  84504
Media obsessed with bears          |  84383
```

Since we have a view of `article_titles`, with their associated author IDs, we can join it with this new view (so as to include the author id with the most popular articles) and create a separate view from this new view:

```
create view popular_authors as
    select author, article_titles.title as title, views
    from article_titles, popular_articles
    where article_titles.title = popular_articles.title
    order by views desc;
```

This view should return:

```
 author |               title                | views
--------+------------------------------------+--------
      2 | Candidate is jerk, alleges rival   | 338647
      1 | Bears love berries, alleges bear   | 253801
      3 | Bad things gone, say good people   | 170098
      1 | Goats eat Google's lawn            |  84906
      2 | Trouble for troubled troublemakers |  84810
      4 | Balloon goons doomed               |  84557
      1 | There are a lot of bears           |  84504
      1 | Media obsessed with bears          |  84383
```

We now join this with the `authors` table to get a list of most popular authors and create a view of that:

```
create view top_authors as
    select name, title, views from popular_authors, authors
    where authors.id = popular_authors.author
    order by views desc;
```

Which returns:

```
          name          |               title                | views
------------------------+------------------------------------+--------
 Rudolf von Treppenwitz | Candidate is jerk, alleges rival   | 338647
 Ursula La Multa        | Bears love berries, alleges bear   | 253801
 Anonymous Contributor  | Bad things gone, say good people   | 170098
 Ursula La Multa        | Goats eat Google's lawn            |  84906
 Rudolf von Treppenwitz | Trouble for troubled troublemakers |  84810
 Markoff Chaney         | Balloon goons doomed               |  84557
 Ursula La Multa        | There are a lot of bears           |  84504
 Ursula La Multa        | Media obsessed with bears          |  84383
```

### Date Which Had More Than 1% Errors

First we find the total where `status != 200 OK` and create a view of it:

```
create view errors as
    select cast(time as date) as date, count(*) as total,
        cast(sum(cast(status != '200 OK' as int)) as float)
    from log group by date;
```

This gives us:

```
           date    | total | sum
       ------------+-------+------
        2016-07-01 | 38705 |  274
        2016-07-02 | 55200 |  389
        2016-07-03 | 54866 |  401
        2016-07-04 | 54903 |  380
        2016-07-05 | 54585 |  423
        2016-07-06 | 54774 |  420
        2016-07-07 | 54740 |  360
        2016-07-08 | 55084 |  418
        2016-07-09 | 55236 |  410
        2016-07-10 | 54489 |  371
        2016-07-11 | 54497 |  403
        2016-07-12 | 54839 |  373
        2016-07-13 | 55180 |  383
        2016-07-14 | 55196 |  383
        2016-07-15 | 54962 |  408
        2016-07-16 | 54498 |  374
        2016-07-17 | 55907 | 1265
        2016-07-18 | 55589 |  374
        2016-07-19 | 55341 |  433
        2016-07-20 | 54557 |  383
        2016-07-21 | 55241 |  418
        2016-07-22 | 55206 |  406
        2016-07-23 | 54894 |  373
        2016-07-24 | 55100 |  431
        2016-07-25 | 54613 |  391
        2016-07-26 | 54378 |  396
        2016-07-27 | 54489 |  367
        2016-07-28 | 54797 |  393
        2016-07-29 | 54951 |  382
        2016-07-30 | 55073 |  397
        2016-07-31 | 45845 |  329
```

## Run logs_analysis.py

With data loaded and with `logs_analysis.py` in the `vagrant` directory, run:

```
python logs_analysis.py
```

or, if this doesn't work:

```
python3 logs_analysis.py
```

## Report

The results generated by running `logs_analysis.py` are contained in the `report.txt` file. For convenience they will also be printed in the terminal in the same format.

## Exit Vagrant

To exit vagrant, on your keyboard press `control + d`.

## Author(s)

* **Roy Telles, Jr.** *(with the help of the Udacity team)*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* I would like to acknowledge and give big thanks to Udacity and team for this excellent resume-building experience 
