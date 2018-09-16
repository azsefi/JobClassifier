from bs4 import BeautifulSoup
import requests
import sqlite3

req = requests.get("http://jobsearch.az/")
soup = BeautifulSoup(req.content.decode("utf8"), "lxml")


def getJobLinks():
    return {x.text.replace(u'\xa0', u' '): req.url + x.get("href") for x in soup.find_all("a", {"class": "hotv_text"})}


def getJobDescription(url):
    job_req = requests.get(url)
    job_soup = BeautifulSoup(job_req.content.decode("utf8"), "lxml")

    content = [x.find("td", {"class": "text"}).text
               for x in job_soup.find_all("td", {"class": "text"})
               if x.find("td", {"class": "text"}) is not None]

    if len(content) > 1:
        raise Exception("More than 1 element in contents")

    return content[0].replace(u'\xa0', u' ')


def crawlJobs(n=-1):
    links = list(getJobLinks().values())
    if n > 0:
        return {x: getJobDescription(x) for x in links[:n]}
    else:
        return {x: getJobDescription(x) for x in links}


def save(contents: dict):
    db = sqlite3.connect("contents.db")
    cursor = db.cursor()
    try:
        cursor.execute("create table jobs(job_url text primary key, job_description text)")
    except Exception as e:
        print(e)

    for x in contents.items():
        try:
            cursor.execute("insert into jobs(job_url, job_description) values(?, ?)", x)
        except:
            print(f"{x[0]} exists in db")

    db.commit()
    db.close()


def getJobs():
    db = sqlite3.connect("contents.db")
    cursor = db.cursor()

    jobs = cursor.execute("select job_url, job_description from jobs").fetchall()

    db.close()
    return [dict(job_url=x[0], job_description=x[1]) for x in jobs]


if __name__ == "__main__":
    # c = crawlJobs(5)
    # save(c)

    c = getJobs()
    print(c)