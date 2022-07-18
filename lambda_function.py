import os

import requests
import datetime
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
import boto3


def fetch_panes():
    host = "https://www.planecheck.com"
    url = host + "/aspseld.asp"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    # lookup content table by header
    planes_t = soup.find("b", text="Date").parent.parent.parent.parent
    planes_rows = planes_t.find_all("tr")
    # remove header row
    planes_rows.pop(0)

    # extract plane data

    def to_plane(row):
        cells = row.find_all("td")
        date = cells[0].text.strip()
        title = cells[1].text.strip()
        details = host + "/" + cells[1].find("a").get("href")
        price = cells[2].text.strip()
        if price == 'Inquire':
            price = None

        country = cells[3].text.strip()
        # find preview image
        hide_handler = row.get('onpointerout').strip()
        img = None
        if hide_handler.find('rec') > 0:
            el_id = hide_handler[hide_handler.find('rec'):hide_handler.find("')")]
            img = host + soup.find(id=el_id).find('img').get('src')

        return {
            "post_date": date,
            "title": title,
            "price": price,
            "country": country,
            "url": details,
            "preview": img
        }

    return map(to_plane, planes_rows)


def filter_planes(planes):
    # filter out planes without specified price
    planes = filter(lambda plane: plane["price"] is not None, planes)
    # filter out non german planes
    planes = filter(lambda plane: plane["country"] == 'Germany', planes)
    # filter out posts older than 2 days
    max_post_date = datetime.timedelta(days=2)
    today_date = datetime.datetime.now()
    return filter(
        lambda plane: (today_date - datetime.datetime.strptime(plane["post_date"], '%d-%m-%Y')) < max_post_date,
        planes)


def to_html(planes):
    # format template
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape()
    )
    template = env.get_template("email.html")
    return template.render(planes=planes)


def send_email(message):
    ses_client = boto3.client('ses')
    email = os.environ['NOTIFICATION_RECIPIENT']
    send_args = {
        'Source': email,
        'Destination': {'ToAddresses': [email]},
        'Message': {
            'Subject': {'Data': "Your daily plane digest"},
            'Body': {
                'Html': {'Data': message}
            }
        }
    }
    ses_client.send_email(**send_args)


def lambda_handler(event, context):
    send_email(to_html(filter_planes(fetch_panes())))

    return {
        'statusCode': 200,
        'body': {}
    }

print(to_html(filter_planes(fetch_panes())))