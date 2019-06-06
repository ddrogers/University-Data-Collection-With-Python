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

from selenium import webdriver
from shutil import which
from bs4 import BeautifulSoup
import re
import time

class CMUDriver:
    """
    This script is designed to access the Carnegie Mellon University Webpage
    to collect information on faculty and students as made available by each
    department.
    """
    '''Carnegie Mellon University Driver
    Designed to open the hompage of the university and return a dictionary of
    schools and departments.'''
    university_name = "Carnegie Mellon University"
    def __init__(self,homepage="https://www.cmu.edu/",executable="chromedriver.exe"):
        '''Initializing the class opens up a browser with access to the homepage of the university.'''
        self.url = homepage
        # Search for available browser driver on system
        self.path = which(executable)
        # Create homepage dictionary variable
        self.homepage_urls = {}
        self.driver = object()

    def open_homepage(self):
        # Load available driver
        self.driver = webdriver.Chrome(executable_path=self.path)
        # Open the homepage url
        self.driver.get(self.url)

    def access_academics_webpage(self):
        # Create academics button object for driver to find "Academics" section on page
        academics_button = self.driver.find_element_by_link_text("Academics")
        # Click the Academics section on page
        self.driver.execute_script("arguments[0].click()", academics_button)
        time.sleep(10)
        return self.driver

    def collect_schools_and_colleges(self):
        '''
        Try selenium to scan for colleges and store to dictionary
        '''
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        school_dictionary = {}
        # Find all program and department names in school(s) with a CSS selector
        # Regex for school names
        school_pattern = "(grid column3 grey )|(grid column3 )"
        schools = soup.find_all("div", {"class": re.compile(school_pattern)})
        # Remove Interdisciplinary Programs from find_all results
        del schools[-1]
        for school in schools:
            # Print headers of research section
            school_name = school.find("h2").text
            #print(school_name)
            # Store hyperlinks of each school and its respective departments as dictionary
            # Initialize dictionary comprehension for department names and hyperlinks for respective schools
            self.homepage_urls[school_name] = {}
            # Using regex, create a regular expression to match all available departments
            dept_pattern = "(^[a-z]+.+)"
            department_fields = school.find_all("div", {"id": re.compile(dept_pattern)})
            for departments in department_fields:
                # Find all department sections in the html
                department = departments.find_all("a", {"href": re.compile("^http")})
                for dept in department:
                    self.homepage_urls[school_name].update({dept.text: dept.get('href')})
        print(self.homepage_urls)

    def closer_browser_window(self):
        self.driver.close()

if __name__ == "__main__":
    print("The cmu.py script has been loaded.")
else:
    print("The cmu.py script has been imported!")