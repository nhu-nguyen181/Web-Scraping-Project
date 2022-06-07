# Web-Scrapping-Project
This project is designed for web crawling, web scraping and interacting with local database and aims to get information of properties from a real estate website. 


Goals:

* To create a tool to scrape real estate data based on suburb, state and post code. 
* To create datasets of properties on a specific subject.
* To create a database to store the datasets and interact with data. 


Data sources:

* Real estate websites:

  * https://www.rent.com.au/
  *

Main libraries: 

* requests
* BeautifulSoup
* sqlite3

<br />

# How - to - do: 

1. Create commandline arguments to interact with database

```ruby
parser = argparse.ArgumentParser(description=
  """
  This script collects property links from rent.com.au. And process them to extract information
  about each property.
  """,
  formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("dbpath", help="Path to database file. Example: rent.db")
parser.add_argument("suburb", help="Name of suburb. Format: suburb-statecode-postcode. Example: annerley-qld-4103")
args = parser.parse_args()

dbpath = args.dbpath
suburb = args.suburb
```

  * Run this command:

    * `python3 rent_collect.py rent.db annerley-qld-4103`

  * To update property information from other suburbs: change the name of suburb
    * `python3 rent_collect.py rent.db marrickville-nsw-2204`

2. Create a database and table to store data
3. Get properties urls from website 
4. Access each url to scrape property information on a specific subject
5. Update database

<br />

## Caution:
This project uses requests and is not applicable for dynamic web pages built in JavaScript.
