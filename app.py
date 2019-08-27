import os
import requests
import lxml
import time
import gspread

from logging import getLogger
from flask import Flask
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials


# LOG = getLogger(__name__)
# LOG.info("Set up Logging Successfully!")


app = Flask(__name__)

departmentList = ['AE', 'AG', 'AR', 'BT', 'CE', 'CH', 'CS', 'CY', 'EC',
                  'EE', 'IM', 'GG', 'HS', 'MA', 'ME', 'MT', 'MI', 'NA', 'PH']

baseURL = "http://www.iitkgp.ac.in"



def profScrape(url):
    r = requests.get(url)
    encoding = r.encoding if "charset" in r.headers.get(
        "content-type", "").lower() else None
    profSoup = BeautifulSoup(r.content, "lxml", from_encoding=encoding)
    profData = profSoup.findAll('div', attrs={'class': 'researcharea'})

    researchAreas = []
    contact = {}

    profResearchArea = profData[len(profData)-2]
    try:
        if len(profData) < 3:
            contactTag = profData[0]
        else:
            contactTag = profData[len(profData)-3]

        contactInfo = contactTag.find("ul").findAll("li")

        contact["email"] = contactInfo[0].get_text().strip()
        contact["phone"] = contactInfo[1].get_text().strip()
    except:
        contact["email"] = None
        contact["phone"] = None

    links = profResearchArea.find("ul").findAll("li")

    for link in links:
        researchTopic = link.get_text().strip()
        researchAreas.append(researchTopic)

    return researchAreas, contact


def departmentScrape(depName):
    r = requests.get(baseURL + "/department/" + depName)
    encoding = r.encoding if "charset" in r.headers.get(
        "content-type", "").lower() else None
    soup = BeautifulSoup(r.content, "lxml", from_encoding=encoding)

    facultyList = {}
    facultyResearchList = {}
    facultyContact = {}

    data = soup.findAll(
        'div', attrs={'class': 'aboutTheDepartmentFacultyListing'})
    for div in data:
        links = div.find_all('a')
        for a in links:
            facultyURL = baseURL + a.attrs['href']
            facultyURL = str(facultyURL.split(";jsessionid")[0])
            facultyName = str(a.get_text())
            facultyList[facultyURL] = facultyName

    for link, faculty in facultyList.items():
        profAreas = profScrape(link)[0]
        profContact = profScrape(link)[1]
        facultyContact[faculty] = profContact
        facultyResearchList[faculty] = profAreas

    return facultyResearchList, facultyContact


def gScholarScrape(faculty):
    hIndex = 0
    topPapers = ["Not Available", "Not Available"]

    searchTerm = faculty.replace(' ', '+') + "+Kharagpur"
    searchURL = "https://scholar.google.com/citations?view_op=search_authors&mauthors={}&hl=en&oi=ao".format(
        searchTerm)
    r = requests.get(searchURL,headers = {'User-agent': 'your bot 0.1'})

    if r.status_code == 429:
        time.sleep(10800)

    soup = BeautifulSoup(r.content, "lxml")
    try:
        authorURL = soup.find("div", class_="gs_ai_t").find("a").attrs['href']
        r = requests.get("https://scholar.google.com" + authorURL)
        authorSoup = BeautifulSoup(r.content, "lxml")
        hIndex = authorSoup.findAll("td", class_="gsc_rsb_std")[2].get_text()
        paperList = authorSoup.findAll("tr", class_="gsc_a_tr")
        topPapers = []
        for paper in paperList[0:2]:
            topPapers.append(paper.get_text())
    except:
        pass

    return hIndex, topPapers


scope = ['https://spreadsheets.google.com/feeds' +
         ' ' + 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open("gresearch")


@app.route('/')
def index():
    depIndex = 0
    for department in departmentList:
        depIndex += 1
        if depIndex % 3 == 0:
            time.sleep(20)
        print("Starting for Department: " + department)
        try:
            worksheet = sheet.add_worksheet(
                title=department, rows="100", cols="20")
            worksheet.insert_row(
                ["Name", "Email", "Phone", "H-Index", "Top Paper-1", "Top Paper-2", "Research Area 1", "Research Area 2", "Research Area 3"], 1)
        except:
            worksheet = sheet.worksheet(department)
            worksheet.insert_row(
                ["Name", "Email", "Phone", "H-Index", "Top Paper-1", "Top Paper-2", "Research Area 1", "Research Area 2", "Research Area 3"], 1)
            print("Deleting previous rows!")
            for x in reversed(range(2, min(50, worksheet.row_count))):
                try:
                    worksheet.delete_row(x)
                except:
                    pass
            print("Successfully deleted rows!")

        time.sleep(10)
        researchList, contactInfo = departmentScrape(department)
        index = 2
        for faculty, areas in researchList.items():
            print("Starting for Professor: " + faculty)
            print("Getting Google Scholar Data for : " + faculty)
            hIndex, topPapers = gScholarScrape(faculty)
            print("Successfully received data for faculty.")
            row = []
            row.append(faculty)
            row.append(contactInfo[faculty]["email"])
            row.append(contactInfo[faculty]["phone"])
            row.append(hIndex)
            for paper in topPapers:
                row.append(paper)

            for area in areas:
                row.append(area)
            worksheet.insert_row(row, index)
            time.sleep(1)
            index += 1
        print("Completed for department: " + department)
        time.sleep(10)
    return "Updated successfully!"


if __name__ == "__main__":
    app.run()
