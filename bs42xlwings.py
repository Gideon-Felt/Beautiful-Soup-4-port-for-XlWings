import xlwings as xw
from bs4 import BeautifulSoup
import os
import pickle
import requests
import re
import uuid
from uuid import UUID

URL_PATTERN = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


# STATIC METHOD
def validate_uuid(uuid_string):
    uuid_string = uuid_string.replace('-','')
    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string 
        # is not a valid hex code for a UUID.
        return False

    # If the uuid_string is a valid hex code, 
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a 
    # valid uuid4. This is bad for validation purposes.

    return val.hex == uuid_string


# STATIC METHOD
def file_handeler(htmlData):
    unique_id = uuid.uuid4()
    pickle.dump(htmlData, open(os.path.dirname(__file__) + f'/html/{unique_id}.pickle', "wb"))
    # return str(unique_id)
    return f'{unique_id}'

# STATIC METHOD
def get_page_source(url):
    if not re.match(URL_PATTERN, str(url)) and not validate_uuid(str(url)): # returns soup object of actual html text
        return BeautifulSoup(str(url), 'html.parser')
    if validate_uuid(url): # checks if uuid or acual url
        url = pickle.load( open( os.path.dirname(__file__) + f'/html/{url}.pickle', "rb" ) )
        return BeautifulSoup(str(url), 'html.parser')
    elif re.match(URL_PATTERN, str(url)) is not None:
        page_source = requests.get(url)
        return BeautifulSoup(str(page_source.content), 'html.parser')

@xw.func
def whats_myDir():
    basedir = os.path.abspath(os.path.dirname(__file__))
    return basedir

@xw.func
def get_pageSource(url):
    htmlData = requests.get(url).content.decode('UTF-8')
    return file_handeler(htmlData)

@xw.func
def find_element_by_css_selector(selector, url):
    page = get_page_source(url)
    return str(page.select(selector)[0])#.contents

@xw.func
def find_child_by_css_selector(selector, child, url):
    page = get_page_source(url)
    return find_element_by_css_selector(f"{str(selector)}:nth-of-type({str(child)})", page)#[2:-2]

@xw.func
def get_contents(element):
    # only use on actual html data wont collect html data from url.
    return str(re.findall(r'>(.*?)<', element)[0])


# print(find_element_by_css_selector(".greyBackground", get_pageSource("https://slco.org/assessor/new/valuationInfoExpanded.cfm?parcel_id=22344020090000&nbhd=2&PA=1")))
# print(get_pageSource("https://slco.org/assessor/new/valuationInfoExpanded.cfm?parcel_id=22344020090000&nbhd=2&PA=1"))

#+---------------------+
#| SELECTOR USE CASE's |
#+---------------------+

# print(get_html_Data("https://requests.readthedocs.io/en/master/"))

# soup.select('div')
# All elements named <div>

# soup.select('#author')
# The element with an id attribute of author

# soup.select('.notice')
# All elements that use a CSS class attribute named notice

# soup.select('div span')
# All elements named <span> that are within an element named <div>

# soup.select('div > span')
# All elements named <span> that are directly within an element named <div>, with no other element in between

# soup.select('input[name]')
# All elements named <input> that have a name attribute with any value

# soup.select('input[type="button"]')
# All elements named <input> that have an attribute named type with value button