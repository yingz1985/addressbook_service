email_to_addr = {
    "Aruna.Balasubramanian@stonybrook.edu":"Aruna Balasubramanian",
}
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def get_emails(url):
    f = open("emails.txt", "a")
    response = simple_get(url)
    if response is not None:
        html = BeautifulSoup(response,'html.parser')
        for tr in html.find_all('tr'):
            tds = tr.find_all('td')
            if("Send Email" in tds[1].text):
                f.write(tds[1].text[:tds[1].text.find("Send Email")].strip()+"\n")

def get_names(url):
    f = open("names.txt", "a")
    response = simple_get(url)
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        for n  in html.find_all('div', attrs={"class":"name"}):
            f.write(n.text.strip()+"\n")

url ="https://adam.cc.sunysb.edu:8443/acc/new-dirsearch.cgi?name_string=neil&status=Any"
#get_names(url)
#get_emails(url)

def print_pretty():
    email = open("emails.txt", "r").readlines()
    name = open("names.txt", "r").readlines()

    for i in range(101):
        email_to_addr[email[i].strip().lower()] = name[i].strip()

    print(json.dumps(email_to_addr,indent=3))

print_pretty()




