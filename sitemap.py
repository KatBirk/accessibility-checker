import requests
import xml.etree.ElementTree as ET
import re


def sitemapsFromUrl(url):
    clankerUrl = url + "robots.txt"
    data = requests.get(clankerUrl)
    robotData = data.text.splitlines()
    # Regex for detection of https and http links
    regexHttps = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"
    for i in range(len(robotData)):
        if robotData[i].__contains__("Sitemap"):
            siteUrl = (robotData[i].split(" "))[1]
            sitemaps = requests.get(siteUrl).text
            if sitemaps.splitlines()[1].__contains__("sitemapindex"):
                sitemapssss = re.findall(regexHttps,sitemaps)
                print(sitemapssss)




sitemapsFromUrl("https://www.google.com/")
