import json
from csv import writer
from random import randrange

import requests
from bs4 import BeautifulSoup

baseUrl = 'https://www.thekingdomcollective.com'
totalNumberOfSermons = 3563


def getHtmlSoup(url):
    response = requests.get(url)
    htmlContent = response.text
    soup = BeautifulSoup(htmlContent, 'lxml')
    return soup


def getSermonTitles(linkTags):
    return list(map(lambda linkTag: linkTag.string, linkTags))


def getAllSermonLinkTags(soup):
    sermonList_a = soup.find(class_='sermon-list').findAll('a')
    return sermonList_a


def getSermonDetail(url):
    soup = getHtmlSoup(url)
    sermon_container = soup.find('article')
    sermonDetail = []
    for child in sermon_container.children:
        if child.name == 'h1':
            sermonDetail.append({
                "tag": "h1",
                "label": "sermon_title",
                "value": [child.getText()]
            })
        elif child.name == 'p':
            sermonDetail.append({
                "tag": child.name,
                "label": "paragraph",
                "value": [child.getText()]
            })
        elif child.name == 'blockquote':
            sermonDetail.append({
                "tag": child.name,
                "label": "quote",
                "value": [child.getText()]
            })
        elif child.name == 'ol':
            sermonDetail.append({
                "tag": child.name,
                "label": "ordered_list",
                "value": list(map(lambda content: content.string, child.contents))
            })
        else:
            if child.name:
                sermonDetail.append({
                    "tag": child.name,
                    "label": "unknown",
                    "value": [child.contents]
                })

    return sermonDetail


def writeToJSON(data, filename='sermons'):
    with open(f'{filename}.json', 'w') as jsonFile:
        json.dump(data, jsonFile, indent=2)


def scrapeFromSermonLinks(sermonLinks):
    sermons = []
    counter = 0
    percentageCompleted = 0
    for link in sermonLinks:
        detailUrl = f"{baseUrl}{link['href']}"
        sermonObject = {
            "url": link['href'],
            "title": link.string,
            "detail": getSermonDetail(detailUrl)
        }
        sermons.append(sermonObject)

        counter += 1

        tempCompleted = int((counter / totalNumberOfSermons) * 100)
        if percentageCompleted < tempCompleted:
            print(f'{tempCompleted}%')
            percentageCompleted = tempCompleted

    return sermons


def main():
    htmlSoup = getHtmlSoup(f'{baseUrl}/spurgeon/list/')
    sermonLinks = getAllSermonLinkTags(htmlSoup)
    # sermons = scrapeFromSermonLinks(sermonLinks)
    # writeToJSON(sermons)
    titles = getSermonTitles(sermonLinks)
    writeToJSON(titles, 'sermon-titles')


main()
