from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from shutil import which
import sqlite3


class EPPDriver():
    '''Engineering and Public Policy Department'''
    department_name = "Engineering and Public Policy"
    def __init__(self):
        self.driver = object()
        self.university = "Carnegie Mellon University"
        self.college = "College of Engineering"
        self.department = "Engineering and Public Policy"
        self.position = "Faculty"


    def open_homepage(self):
        '''Initializing the class opens up a browser with access to the homepage of the university.'''
        self.url = "https://www.cmu.edu/epp/"
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
        faculty_profile_button = self.driver.find_element_by_link_text("Faculty")
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
        search_pattern = "photo filterable"
        faculty = soup.find_all("div", {"class": re.compile(search_pattern)})
        i = 0
        for member in faculty:
            bio_url = member.find("a",href=True)
            # Combine with faculty link webpage for access
            bio_url = "https://www.cmu.edu/epp/people/faculty/{}".format(bio_url["href"])
            self.driver.get(bio_url)
            # Collect and store name, title, bio, college, and department
            name = self.driver.find_elements_by_tag_name("h1")[1]
            title = self.driver.find_elements_by_tag_name("h2")[1]
            print(name.text,title.text)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            bio = re.search("Bio\s+(.*)[Education | Research | \s+]", soup.get_text().replace('\n', ' ').replace("\'",""))
            if bio == None:
                bio = "Not available at this time."
            research = ""
            interests = ""
            # Insert new row where values do not already exists
            sql_statement = """
                        INSERT OR IGNORE INTO cmu 
                        VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(self.university,
                                                                                                self.college,
                                                                                                self.department,
                                                                                                self.position,
                                                                                                name.text,
                                                                                                title.text.replace("\'",""),
                                                                                                bio[0],
                                                                                                research, interests)
            cur.executescript(sql_statement)

            # Return to Faculty homepage
            faculty_page = self.driver.find_element_by_link_text("Faculty")
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
    print("The ce_epp.py file has been loaded!")
    epp = EPPDriver()
    epp.open_homepage()
    epp.access_faculty_webpage()
    epp.connect_to_database()
    epp.insert_to_database()
    epp.close_browser_window()
    pd.options.display.max_columns = 11
    udc_df = pd.DataFrame(epp.view_database(),
                          columns=["id", "University", "College", "Department", "Position", "Name", "Title", "Bio",
                                   "Research", "Interests"])
    print(udc_df)
else:
    print("The ce_epp.py file has been imported!")