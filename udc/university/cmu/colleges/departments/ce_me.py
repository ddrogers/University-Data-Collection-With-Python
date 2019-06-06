from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from shutil import which
import sqlite3


class MEDriver():
    '''Mechanical Engineering Department'''
    department_name = "Mechanical Engineering"
    def __init__(self):
        self.driver = object()
        self.university = "Carnegie Mellon University"
        self.college = "College of Engineering"
        self.department = "Mechanical Engineering"
        self.position = "Faculty"

    def open_homepage(self):
        '''Initializing the class opens up a browser with access to the homepage of the university.'''
        self.url = "http://www.cmu.edu/me/"
        # Search for available browser driver on system
        self.path = which("chromedriver.exe")
        # Load available driver
        self.driver = webdriver.Chrome(executable_path=self.path)
        self.driver.maximize_window()
        # Open the homepage url
        self.driver.get(self.url)

    def access_department_webpage(self,homepage_url):
        '''Access department homepage url as chosen.'''
        # Access desired college webpage
        self.driver.get(homepage_url)
        return self.driver

    def access_faculty_webpage(self):
        # Search faculty section
        people_section = self.driver.find_element_by_link_text("People")
        people_section.click()
        return self.driver

    def connect_to_database(self):
        '''Connect to a new database a create a new table'''
        conn = sqlite3.connect("./data/udc.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS cmu (id INTEGER PRIMARY KEY, university text, college text,"
                    " department text, position text, name text UNIQUE,title text, bio text, research text,"
                    " interests text)")
        conn.commit()
        conn.close()

    def insert_to_database(self):
        conn = sqlite3.connect("./data/udc.db")
        cur = conn.cursor()
        # Search and collect information for each faculty member, i.e. name, title, research interest
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        search_pattern = "facultyList"
        faculty = soup.find("ul", {"id": re.compile(search_pattern)})
        faculty_names = faculty.find_all("h4", {"class": "bioname"})
        faculty_titles = faculty.find_all("p", {"class": "biotitle"})
        faculty = faculty.find_all("p", {"class": "bioLink"})

        i = 0
        for name, title, member in zip(faculty_names, faculty_titles, faculty):
            member = member.find("a", href=True)
            bio_url = "https://www.meche.engineering.cmu.edu/directory/{}".format(member["href"])
            self.driver.get(bio_url)
            # bio
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            bio = soup.find("div", {"class": "faculty-bio-content-primary"})
            bio = bio.get_text().replace("\'","")
            print(name.text, title.text)
            research = ''
            interests = ''
            # Insert new row where values do not already exists
            sql_statement = """
                                    INSERT OR IGNORE INTO cmu 
                                    VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(self.university,
                                                                                                            self.college,
                                                                                                            self.department,
                                                                                                            self.position,
                                                                                                            name.text,
                                                                                                            title.text,
                                                                                                            bio,
                                                                                                            research,
                                                                                                            interests)
            cur.executescript(sql_statement)

            # Return to Faculty homepage
            directory = "https://www.meche.engineering.cmu.edu/directory/index.html"
            self.driver.get(directory)
            i += 1
        conn.commit()
        conn.close()

    def close_browser_window(self):
        self.driver.close()

    def view_database(self):
        conn = sqlite3.connect("./data/udc.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM cmu")
        rows = cur.fetchall()
        conn.close()
        return rows


if __name__ == "__main__":
    print("The ce_me.py file has been loaded!")
    me = MEDriver()
    me.open_homepage()
    me.access_faculty_webpage()
    me.connect_to_database()
    me.insert_to_database()
    #me.close_browser_window()
    pd.options.display.max_columns = 11
    udc_df = pd.DataFrame(me.view_database(),
                          columns=["id", "University","College", "Department", "Position", "Name", "Title", "Bio",
                                   "Research", "Interests"])
    print(udc_df)
else:
    print("The ce_me.py file has been imported!")
