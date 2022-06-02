import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import argparse
import logging
import sqlite3
import re
import time
import datetime

# create commandline arguments:
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

db = sqlite3.connect("rent.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cur = db.cursor()
cur.execute(
  """
  /* This table stores all the property information. */

  create table if not exists property_info(
    url primary key,
    type,
    agent,
    street,
    suburb,
    state,
    price,
    bond,
    bed,
    bath,
    parking,
    pet,
    furnished,
    retrieval_time)
  """
)

logging.basicConfig(level=logging.INFO)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# create a loop to paginate through each search result page, stopping when reaching an unfound URL
page_number = 1

while True:
  url = f'https://www.rent.com.au/properties/{suburb}/p{page_number}'

  logging.info(f"Getting request {url}...")

  try:

    r = requests.get(url, headers=headers)
    soup = bs(r.text, 'html.parser')
    
    if soup.find('div', {'class': 'ui-alert -warning'}) is not None:
      # no more pages to reach
      break

    else:
      properties = soup.find_all('a', {'class': 'link'}, href=re.compile(r'rent\.com\.au\/property\/'))

      logging.info("Inserting links to database...")

      for link in properties:
        exist = db.execute("SELECT count(*) FROM property_info WHERE url = ?", [link['href']]).fetchone()[0] > 0
        
        if not exist:

          logging.info(f"Inserting: {link['href']}...")

          with db:
            cur.execute("insert or ignore into property_info(url) values(?)", (link['href'],))
  
      page_number += 1
      time.sleep(3)
      
  except requests.exceptions.HTTPError:

    logging.info("page not found...")

    break

logging.info("Crawling finished.")


# create a loop to get elements from each link, skipping when reaching a link that was scrapped

while True:
  to_retrieve = [row[0] for row in db.execute("select url from property_info where retrieval_time is null")]

  if not to_retrieve:
    break

  else:
    for link in to_retrieve:
      link_request = requests.get(link)
      link_request.raise_for_status()
      soup = bs(link_request.text, 'html.parser')

      try: 
        type = getattr(soup.find('p', {'class': 'light'}), 'text', None)
        agent = soup.select('#property-contact > div.contact-panel > div > ul > li.light')[0].find(text=True, recursive=False)
        street = soup.find('address', {'class': 'detail-address'}).text.split(', ')[0]
        suburb = soup.find('address', {'class': 'detail-address'}).text.split(', ')[1]
        state = soup.find('address', {'class': 'detail-address'}).text.split(', ')[-1]
        price = soup.find('h2', {'class': 'price-header bold'}).get_text(strip=True)[1:].split(' ')[0]
        bond = soup.select('section.block > ul > li > p.bold')[0].find(text=True, recursive=False)[1:].split(' ')[0]
        bed = soup.find('span', {'class': 'value'}, string=re.compile(r'Bed')).text.split(' ')[0]
        bath = soup.find('span', {'class': 'value'}, string=re.compile(r'Bath')).text.split(' ')[0]
        parking = getattr(soup.find('span', {'class': 'value'}, string=re.compile(r'Car')), 'text', None).split(' ')[0]
        pet = getattr(soup.find('span', {'class': 'value'}, string=re.compile(r'Pet')), 'text', None)
        furnished = getattr(soup.find('span', {'class': 'value'}, string=re.compile(r'Furnished')), 'text', None)

      except:
        logging.info("Error...")
        print(link)


      logging.info("Inserting property information to database...")

      with db:
        logging.info(f"Inserting type:{type}, agent:{agent}, street:{street}, suburb:{suburb}, state:{state}, price:{price}, bond:{bond}, bed:{bed}, bath:{bath}, lots:{parking}, pet:{pet}, furnished:{furnished}...")

        db.execute(
          """
            update property_info 
            set type = ?,
                agent = ?,
                street = ?,
                suburb = ?,
                state = ?,
                price = ?,
                bond = ?,
                bed = ?,
                bath = ?,
                parking = ?,
                pet = ?,
                furnished = ?,
                retrieval_time = ?
            where url = ?
          """,
            (type, agent, street, suburb, state, price, bond, bed, bath, parking, pet, furnished, datetime.datetime.now(), link)
        )


logging.info("Scrapping finished.")      