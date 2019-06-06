from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from shutil import which
import sqlite3


class BEDriver():
    '''Biomedical Engieering Department'''
    department_name = "Biomedical Engineering"
    def __init__(self):
        '''
        Initialize webpage driver
        '''
        self.driver = object()
        self.university = "Carnegie Mellon University"
        self.college = "College of Engineering"
        self.department = "Biomedical Engineering"
        self.position = "Faculty"

    def open_homepage(self):
        '''Initializing the class opens up a browser with access to the homepage of the university.'''
        self.url = "http://www.bme.cmu.edu/"
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
        '''Access Faculty webpage'''
        # Search faculty section
        people_section = self.driver.find_element_by_link_text("People")
        people_section.click()
        faculty_profile_button = self.driver.find_element_by_link_text("Faculty Profiles")
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
        '''Search Faculty webpage for members then store into sqlite database.'''
        conn = sqlite3.connect("./data/udc.db")
        cur = conn.cursor()
        # Search and collect information for each faculty member, i.e. name, title, research interest
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        search_pattern = "^filterable"
        faculty = soup.find_all("div", {"class": re.compile(search_pattern)})
        i = 0
        for member_number in range(0, len(faculty)):
            person_info = {}
            faculty_button = self.driver.find_elements_by_class_name("name")[member_number]
            self.driver.execute_script("arguments[0].click()", faculty_button)
            # Collect and store name, title, bio, college, and department
            name = self.driver.find_elements_by_tag_name("h1")[1]
            title = self.driver.find_elements_by_tag_name("h2")[1]
            print(name.text, title.text)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            bio = re.search("Bio\s\w(.*)Research Interests:",
                            soup.get_text().replace('\n', ' ').replace("Publications", '').replace("\'","")).group().split('Research')
            research = re.search("Research\s\w(.*)Research Interests:",
                                 soup.get_text().replace('\n', " ").replace("\'","")).group().split("Research Interests:")
            interests = re.search("Research Interests:.+", soup.get_text().replace("\'","")).group().split("Research Interests:")

            # Insert new row where values do not already exists

            sql_statement = """
            INSERT OR IGNORE INTO cmu 
            VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(self.university, self.college,
                                                                                    self.department, self.position,
                                                                                    name.text,
                                                                                    title.text, bio[0], research[0],
                                                                                    interests[1])
            cur.executescript(sql_statement)
            faculty_page = self.driver.find_element_by_link_text("Faculty")
            faculty_page.click()
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
    print("The ce_be.py file has been loaded!")
    be = BEDriver()
    be.open_homepage()
    be.access_faculty_webpage()
    be.connect_to_database()
    be.insert_to_database()
    be.close_browser_window()
    udc_df = pd.DataFrame(be.view_database(),columns = ["id", "University","College", "Department", "Position", "Name",
                                                        "Title", "Bio", "Research", "Interests"])
    print(udc_df)
else:
    print("The ce_be.py file has been imported!")