from bs4 import BeautifulSoup
import imghdr
from fuzzywuzzy import fuzz
import requests
from urllib.request import urlopen
from urllib.parse import urljoin
import re
import os, sys
import json
import youtube_dl

def similar(a, b):
    return fuzz.token_set_ratio(a.lower(), b.lower())

# adapted from http://stackoverflow.com/questions/20716842/python-download-images-from-google-image-search
def get_soup(url,header):
    return BeautifulSoup(requests.get(url,headers=header).text,'html.parser')

# scrapes google images for the first image, downlaods and saves it
def scrape_img(query, save_directory,  output='.img.jpg'):
        image_type="Action"

        query= query.split()
        query='+'.join(query)
        url="https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
        header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

        soup = get_soup(url,header)
        ActualImages=[]# contains the link for Large original images, type of  image

        for a in soup.find_all("div",{"class":"rg_meta"}):
            link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
            ActualImages.append((link,Type))
        for img, Type in ActualImages:
            try:
                raw_img = urlopen(img).read()
                f = open(os.path.join(save_directory , output), 'wb')
                f.write(raw_img)
                f.close()

                if not imghdr.what(os.path.join(save_directory, output)) == None:
                    break
                else:
                    os.remove(os.path.join(save_directory, output))
            except Exception as e:
                #print("could not load : "+img)
                #print(e)
                None

# scrapes youtube for the first link, downlaods and saves it
def scrape_vid(query, max_links=1):
        query= query.split()
        query='+'.join(query)
        url="https://www.youtube.com/results?search_query="+query
        header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

        soup = get_soup(url,header)

        for link in soup.find_all("a"):
            link = link.get('href')
            if 'watch' in link:
                full_link = urljoin("https://www.youtube.com", link) 
                return full_link

# downloads youtube video into mp3
def download_youtube(query, save_directory, output='.song', link=None):
    if not link:
        link = scrape_vid(query)
    output = os.path.join(save_directory, output)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': output+".%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def get_metadata(query):
    url = "https://itunes.apple.com/search?term="
    url += "+".join(query.strip().split(" "))

    header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    req = requests.get(url, headers=header)
    results =  req.json()

    if results['resultCount'] == 0:
        return None 
    else:
        # finds which result is most correlated to the query
        most_likely = None
        score = 0
        for result in results['results']:
            new_score = similar(query.lower(), (result['trackName'] + " " + result['artistName']).lower())
            if  new_score > score:
                score = new_score
                most_likely = result

        return most_likely


if __name__ == '__main__':
    #download_youtube("kendrick lamar king kunta lyrics", os.getcwd() + "/")
    #scrape_img("kendrick lamar to pimp a butterfly album cover", os.getcwd() +"/")
    #print(get_metadata("kendrick lamar king kunta"))
    None
