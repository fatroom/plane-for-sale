import requests
from bs4 import BeautifulSoup

HOST = "https://www.planecheck.com"
URL = HOST + "/aspseld.asp"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

# lookup content table by header
planes_t = soup.find("b", text="Date").parent.parent.parent.parent
planes_rows = planes_t.find_all("tr")

# remove header row
planes_rows.pop(0)

# extract plane data
planes = []
for row in planes_rows:
  cells = row.find_all("td")
  date = cells[0].text.strip()
  title = cells[1].text.strip()
  details = HOST + "/" + cells[1].find("a").get("href")
  price = cells[2].text.strip()
  if price == 'Inquire':
    price = None

  country = cells[3].text.strip()
  # find preview image
  hide_handler = row.get('onpointerout').strip() 
  img = None
  if hide_handler.find('rec') > 0:
    el_id = hide_handler[hide_handler.find('rec'):hide_handler.find("')")]
    img = HOST + soup.find(id=el_id).find('img').get('src')

  planes.append({
    "post_date": date,
    "plane": title,
    "price": price,
    "country": country,
    "url": details,
    "preview": img
  })

planes = filter(lambda plane: plane["price"] != None, planes)

for plane in planes:
  print(plane)

