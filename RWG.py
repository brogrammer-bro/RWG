#!/usr/bin/env python

import urllib2
import re
import Image
from cStringIO import StringIO
import random
random.seed()
import ImageFont
import ImageDraw
from datetime import *
import os
import json
import colorsys
import math
import time

subreddits = ("spaceporn", "waterporn", "skyporn", "geologyporn", "animalporn", "botanicalporn", "fractalporn", "HDR", "wallpapers")
subreddit = random.choice(subreddits)
#subreddit = "braveryjerk" lol jk
print("/r/"+subreddit)

userAgent = "Reddit Wallpaper Generator by /u/brogrammer_bro v1.05"
headers = { 'User-Agent' : userAgent }
redditUrl = "http://www.reddit.com/r/" + subreddit + "/top/?sort=top&t=month"
redditReq = urllib2.Request(redditUrl, headers = headers)
done = False
while not(done):
    try:
        links = urllib2.urlopen(redditReq).read()
    except:
        print("Failed to open " + redditUrl)
        #print(sys.exc_info()[0])
        time.sleep(30)
        continue
    else:
        done = True
print("Reddit page downloaded\n")

urls = re.findall("http://i.imgur.com/\w+.(?:jpg)", links)
print("imgur urls: \n")
print(urls)

bgColor = (0,0,0)
desktopSize = (1366, 768)
finalImg = Image.new("RGB", desktopSize, bgColor)

print("\nBG generated\n")

usedUrls = []
numPics = 6
size = 384, 384
locations = ((10, 10), (20+384, 10), (30+2*384, 10),
             (10, 20+384), (20+384, 20+384), (30+2*384, 20+384))
for url in urls:
    if url in usedUrls:
        continue
    else:
        usedUrls.append(url)
        
    imgRequest = urllib2.Request(url, headers = headers)
    done = False
    while not(done):
        try:
            imgData = urllib2.urlopen(imgRequest)
        except:
            print("Failed to open " + url)
            #print(sys.exc_info()[0])
            time.sleep(30)
            continue
        else:
            done = True
    imgFile = StringIO(imgData.read())
    img = Image.open(imgFile)
    print("Loaded: " + url)
    
    squareSize = img.size[1] if img.size[0] > img.size[1] else img.size[0]
    img = img.crop(((img.size[0] - squareSize)/2, (img.size[1] - squareSize)/2, squareSize, squareSize))
    img = img.resize(size, Image.ANTIALIAS)
    print("resized")
    
    location = locations[len(usedUrls)-1][0], locations[len(usedUrls)-1][1]
    box = (location[0], location[1], size[0] + location[0], size[1] + location[1])
    finalImg.paste(img, box)
    print("added to bg\n")
    if len(usedUrls) >= numPics:
        print("All imgur links loaded and added\n")
        break


u24 = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf", 24)
u18 = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf", 18)
fillColor = "white"
highColor = "#FF4500"
lowColor = "#5f99cf"
print("Fonts loaded\n")

infox = 40 + 384*3
infocenter = 80 + 384*3
datey = 45
newline = 25
weathery = 140
newDay = 8 * newline
eventy = weathery + 2 * newDay
newEvent = 2.5 * newline

dayStr = date.today().strftime("%A")
dateStr = date.today().strftime("%B %d %Y")

draw = ImageDraw.Draw(finalImg)

draw.text((infox, datey), dayStr, font = u24, fill = fillColor)
draw.text((infox, datey + newline), dateStr, font = u24, fill = fillColor)
print("Date rendered\n")

url = "http://api.openweathermap.org/data/2.5/forecast/daily?q=Novi&mode=json&cnt=2"
req = urllib2.Request(url)
done = False
while not(done):
    try:
        response = urllib2.urlopen(req)
    except:
        print("Failed to open " + url)
        #print(sys.exc_info()[0])
        time.sleep(30)
        continue
    else:
        done = True
weatherStr = response.read()
weatherData = json.loads(weatherStr)
print("Weather data downloaded:")
print(weatherData)

weatherList = weatherData["list"]

for i in range(0, 2):
    draw.text((infox, weathery), "Today:" if i==0 else "Tomorrow:", font = u24, fill = fillColor)
    draw.text((infox, weathery + 1 * newline), weatherList[i]["weather"][0]["description"], font = u18, fill = fillColor)

    def K2F(K):
        return (K - 273.15) * 1.8 + 32.0

    avgTemp = K2F(weatherList[i]["temp"]["max"] + weatherList[i]["temp"]["min"])/2

    if avgTemp >= 50:
        psat = (avgTemp - 50)/50
        tempColor = (255, int(255 - psat * 255), int(255 - psat * 255))
    else:
        psat = (50 - avgTemp)/50
        tempColor = (int(255 - psat * 255), int(255 - psat * 255), 255)

    draw.text((infox, weathery + 2 * newline), "Temperature:", font = u18, fill = tempColor)
    draw.text((infocenter, weathery + 3 * newline), str(K2F(weatherList[i]["temp"]["max"])), font = u18, fill = highColor)
    draw.text((infocenter, weathery + 4 * newline), str(K2F(weatherList[i]["temp"]["min"])), font = u18, fill = lowColor)

    humidity = weatherList[i]["humidity"]
    psat = humidity / 75
    humidColor = (int(255 - psat * 255), 255, int(255 - psat * 255))
    draw.text((infox, weathery + 5 * newline), "Humidity:", font = u18, fill = humidColor);
    draw.text((infocenter, weathery + 6 * newline), str(humidity) + "%", font = u18, fill = humidColor);
    weathery += newDay
print("Weather data rendered\n")

class Event:
    def __init__(self, name, eventdate):
        assert isinstance(name, str), "Name must be a String: %r" % name
        assert isinstance(eventdate, date), "Date must be a datetime: %r" % date
        self.name = name
        self.date = eventdate
        
    def today(self):
        return date.today()
        
    def isPassed(self):
        return self.date < self.today()
    
    def daysUntil(self):
        return int(round((self.date - self.today()).total_seconds() / 86400))

events = [
    Event("First Day of School", date(2013, 8, 28)),
    Event("FRC Kickoff", date(2014, 1, 4)),
    Event("Stop Build Day?", date(2014, 1, 4)+timedelta(days=45))
]

print("Event data loaded")

for event in events:
    if event.isPassed():
        continue
    print("drawing " + event.name + " in " + str(event.daysUntil()) + " days")
    draw.text((infox, eventy), event.name, font = u18, fill = fillColor)
    draw.text((infox, eventy + newline), str(event.daysUntil()), font = u24, fill = fillColor)
    eventy += newEvent

#finalImg.save("wallpaper.jpg", "JPEG", quality = 95)
finalImg.save(os.getenv("HOME") + "/Wallpapers/wallpaper.jpg", quality = 95)
print("Wallpaper saved\n")
