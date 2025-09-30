import requests
import logging
import xml.etree.ElementTree as ET
import re
logger = logging.getLogger("sitemap")

# Regex for detection of urls
regexHttps = "https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)"

def deleteDuplicates(sitemaps):
    sitemaps


def extractUrlsFromSitemapIndex(sitemap, url, recursionOverflow):
    sitemapLinks = []

    # Asuming that infinite loop with 100+ sitemaps nestings
    if recursionOverflow >= 3:
        return sitemapLinks

    links = re.findall(regexHttps, (requests.get(sitemap).text))

    for i in range(len(links)):
        # We are asuming all .xml files are sitemaps
        if links[i][1].__contains__(".xml"):
            sitemapLinks.extend(
                extractUrlsFromSitemapIndex(
                    url + links[i][1], url, recursionOverflow + 1
                )
            )
        else:
            sitemapLinks.append(url + links[i][1])
    return sitemapLinks


def sitemapsFromUrl(url):
    clankerUrl = url + "/robots.txt"
    clankerData = requests.get(clankerUrl)
    robotData = clankerData.text.splitlines()
    sitemaps = []

    # This may seem redundant, but if a website has multiple Sitemaps in robots.txt this can handle it
    for i in range(len(robotData)):

        if robotData[i].__contains__("Sitemap"):
            siteUrl = (robotData[i].split(" "))[1]
            sitemapsindex = requests.get(siteUrl).text

            if sitemapsindex.splitlines()[1].__contains__("sitemapindex"):
                sitemapssss = re.findall(regexHttps, sitemapsindex)

                for j in range(len(sitemapssss)):
                    # We are asuming all .xml files are sitemaps (may cause issues later)
                    if sitemapssss[j][1].__contains__(".xml"):
                        sitemaps.extend(
                            extractUrlsFromSitemapIndex(url + sitemapssss[j][1], url, 0)
                        )

    sitemaps = list(set(sitemaps)) # Removes duplicates
    logger.info(sitemaps) #uncomment for debugging
    print(len(sitemaps)) #uncomment for debugging
    return sitemaps
