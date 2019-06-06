###############################################################################
# University Data Collector
# The following code is designed to give a user a list
# of colleges and departments to choose for Faculty
# information collection.
#
# Copyright (C) 2019  Donald D. Rogers II
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
################################################################################
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from shutil import which
import sqlite3

class ECEDriver():
    '''Electrical & Computer Engineering Department'''
    department_name = "Electrical & Computer Engineering"
    def __init__(self):
        self.driver = object()
        self.university = "Carnegie Mellon University"
        self.college = "College of Engineering"
        self.department = "Electrical & Computer Engineering"
        self.position = "Faculty"


    def open_homepage(self):
        '''Initializing the class opens up a browser with access to the homepage of the university.'''
        self.url = "https://www.ece.cmu.edu/"
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
        people_section = self.driver.find_element_by_link_text("Directory")
        people_section.click()
        faculty_profile_button = self.driver.find_element_by_link_text("ECE faculty")
        faculty_profile_button.click()
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
        faculty = soup.find_all("a", {"class": "cta"}, href = True)
        i = 0
        for member in faculty:
            person_info = {}
            bio_url = "https://www.ece.cmu.edu/directory/{}".format(member["href"])
            self.driver.get(bio_url)
            # Collect and store name, title, bio, college, and department
            name = self.driver.find_elements_by_tag_name("h1")[1]
            title = self.driver.find_elements_by_tag_name("h2")[1]
            print(name.text, title.text)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            bio = re.search("Bio\s+\w(.*)[Education | Research]", soup.get_text().replace('\n', ' ').replace("\'","")).group().split('Education')
            person_info['Bio'] = bio[0].encode("utf-8")

            research = ""
            interests = ""
            # Insert new row where values do not already exists
            sql_statement = """
                        INSERT OR IGNORE INTO cmu 
                        VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(self.university,
                                                                                                self.college,
                                                                                                self.department,
                                                                                                self.position,
                                                                                                name.text.replace("\'",""),
                                                                                                title.text,
                                                                                                bio[0],
                                                                                                research, interests)
            cur.executescript(sql_statement)

            # Return to Faculty homepage
            faculty_page = self.driver.find_element_by_link_text("Directory")
            faculty_page.click()
            i+=1
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
    print("The ce_ece.py file has been loaded!")
    ece = ECEDriver()
    ece.open_homepage()
    ece.access_faculty_webpage()
    ece.connect_to_database()
    ece.insert_to_database()
    ece.close_browser_window()
    pd.options.display.max_columns = 11
    udc_df = pd.DataFrame(ece.view_database(),
                          columns=["id", "University", "College", "Department", "Position", "Name", "Title", "Bio",
                                   "Research", "Interests"])
    print(udc_df)
else:
    print("The ce_ece.py file has been imported!")