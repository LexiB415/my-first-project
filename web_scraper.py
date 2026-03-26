import requests
from bs4 import BeautifulSoup
import datetime

url = "https://pixelford.com/blog/"
import random
random_number = random.randint(1, 10000)
response = requests.get(url, headers = {'user-agent': f'{random_number}'})
html = response.content
soup = BeautifulSoup(html, 'html.parser')
a_tags = soup.find_all('a', class_="entry-title-link")
blogs = soup.find_all('article', class_="type-post")

for blog in blogs:
    title = blog.find('a', class_="entry-title-link").get_text()

    blog_datetime_string = blog.find('time', class_='entry-time').get('datetime')
    blog_datetime = datetime.datetime.fromisoformat(blog_datetime_string)
    pretty_date = blog_datetime.strftime("%b %d %Y")
   
    print(f"{pretty_date} - {title}")


print(f'Hello {random_number}')