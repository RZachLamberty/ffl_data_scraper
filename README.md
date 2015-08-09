# Fantasy Football Data Scraper

This is a simple fantasy football data scraper I put together using [`scrapy`](http://scrapy.org/) and [`postgres`](http://www.postgresql.org/) (via the [`psyocpg2`](http://initd.org/psycopg/) library). Currently only ESPN fantasy football league (FFL) data is supported, but It could pretty easily be extended to other leagues by defining other spiders.


## What it does

The `scrapy` workflow is pretty simple: you define some places to start (`start_urls`) and a way of parsing the html responses you would get if you requested those urls (a function called, oddly enough, `parse`). The module then iteratively loads urls, parses out the score projection information ESPN has for players, and persists that information to a local postgres database.


## How it does it

In my instance, I was interested in urls of the form `http://games.espn.go.com/ffl/tools/projections?&leagueId={}`, formatting the {} to have my particular fantasy league's brackets. One caveat: this will only work if you have a leagueId, I think -- it could (and should) be extended to work without one, but it would change the table format of the resulting html, so I'll punt (pun intended) for now. If you pull up a page like that, it will only be the first 40 or 60 elements, but of course I want all of the subsequent table pages (`&startIndex={40,80,120,...}`). To accomplish this, I do two things:

1. I define a parse function that looks at a given 40-element table page and parses each row into a `scrapy Item` class, and
2. At the end of the parsing of that page, I look for a "NEXT" link on that page and submit that as a follow-up `scrapy` request.

My `parse` function is pretty stupid -- mostly just using `xpath` expressions to jump around in the `response` object and doing some minor string manipulations. This item is then yielded up to the global scrapy process, which in turn passes that item through whatever pipelines have been defined. Here, I do something more complicated than the basic pring-to-screen pipeline -- I persist the details of that item to a table `raw_data` in a local postgres database `ffldata`.


## How you can do it, too

First, of course, you have to clone this bad boy. Next, you have to prepare a python and a postgres environment


### Python environment

You need to create an environment in which to execute the python code. I'm currently running anaconda, so my requirements.txt file is an anaconda requirements file (that is, you can run

```bash
# creating a conda environment
conda create --name <env> --file requirements.txt
```

to create a suitable environment.

If you're using virtualenvs / pip, I believe requirements.pip.txt will work for you as well (but won't be keeping that as up to date as the anaconda req file).
```bash
# virtualenv / pip environment
virtualenv /path/to/venv
source /path/to/venv/bin/activate
pip install -r requirements.pip.txt
```


### Postgres environemtn

Hopefully you have your own postgres instance which you can access and alter. If you can't [email me](mailto:r.zach.lamberty@gmail.com) and I can help you and whomever your admin is navigate the process of setting it up.

**Assuming you have access to the postgres user**, you will first need to create the user and database and build the table. This can be done relatively easily using the `bootstrap_postgres.sql` file I've provided:
```bash
sudo su - postgres
psql -f /path/to/cloned/repo/bootstrap_postgres.sql
```

After this, **assuming you have root acccess**, you will need to update the host based authentication properites of the `ffldata` user we just created by adding the line at the bottom:
```bash
# the following contents are from the file /etc/postgres/#.#/main/pg_hba.conf

# Database administrative login by Unix domain socket
local   all             postgres                                peer
local   ffldata         ffldata                                 md5
```
to your `pg_hba.conf` file


### Once that's all done...

With those pieces out of the way, you are free to scrape to your heart's content!

Start the scraper with
```bash
scrapy crawl espn [-a KEY=VALUE] [--set KEY=VALUE]
```

The `-a` flag is for parameters to pass directly to the spider, and there is only one of those:

+ `wipeTable`: a boolean, weather or not we should first drop all rows in `raw_input`. Note that running the web scraper for a second time *without* doing this
will fail, as all rows have already been added and second attempts will violated the primary key constraint for this table

The `--set` parameters are for overridding those set in `ffl_data_scraper\settings.py`, and which are used throughout the module (not just the spider). Notable `KEY, VALUE` options set this way are:

+ `LEAGUE_ID`: if you have your own league id in ESPN FFL, you can pass it here at the command line and your league's scoring method will be taken into accoutn.
+ `PG_USER`, `PG_DBNAME`, `PG_HOST`, and `PG_PASSWORD`: if set, these parameters will be used to make connections to the postgres database we created above.

A lot message will be written out to `/path/to/repo/ffl_data_scraper.log`, and you should be able to verify that the persistence to the postgres database worked by running

```sql
psql -u ffldata
SELECT count(*) FROM raw_data WHERE ffl_source = 'espn';
```

and having approximately 1660 rows.
