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
import csv

class CEDriver(object):
    '''College of Engineering Driver
    Designed to search each department within the college and return a dataframe of results.'''
    # Inherit the school dictionary from CMUDriver object
    college_name = "College of Engineering"
    def __init__(self):
        # Initialize the inherited CMUDriver class to gain access to the parameters set within
        object.__init__(self)
        # Access the "Academics" section of CMU Webpage
        self.driver = object.access_academics_page(self)
        # Collect names of schools and colleges for CMU
        self.school_dictionary = object.find_schools_and_colleges(self)


    def search_be_dept(self):
        '''Search Biomedical Engineering Department'''
        # Access Department Homepage
        department_webpage = self.school_dictionary["College of Engineering"]["Biomedical Engineering"]
        self.driver.get(department_webpage)
        # Select People Section
        people_section = self.driver.find_element_by_link_text("People")
        people_section.click()
        # Search faculty section
        faculty_profile_button = self.driver.find_element_by_link_text("Faculty Profiles")
        faculty_profile_button.click()
        # Search and collect information for each faculty member, i.e. name, title, research interest
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        search_pattern = "^filterable"
        faculty = soup.find_all("div", {"class": re.compile(search_pattern)})
        i = 0
        person_list = []
        for member_number in range(0,len(faculty)):
            person_info = {}
            faculty_button = self.driver.find_elements_by_class_name("name")[member_number]
            self.driver.execute_script("arguments[0].click()", faculty_button)
            # Collect and store name, title, bio, college, and department
            name = self.driver.find_elements_by_tag_name("h1")[1]
            title = self.driver.find_elements_by_tag_name("h2")[1]
            person_info['Name'] = name.text
            person_info['Title'] = title.text
            print(name.text,title.text)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            bio = re.search("Bio\s\w(.*)Research Interests:",soup.get_text().replace('\n', ' ').replace("Publications",'')).group().split('Research')
            research = re.search("Research\s\w(.*)Research Interests:",soup.get_text().replace('\n'," ")).group().split("Research Interests:")
            interests = re.search("Research Interests:.+",soup.get_text()).group().split("Research Interests:")
            person_info['Bio'] = bio[0].encode("utf-8")
            person_info['Research'] = research[0].encode("utf-8")
            person_info['Interests'] = interests[1].encode("utf-8")
            person_info["College"] = "College of Engineering"
            person_info["Department"] = "Biomedical Enigeering"
            person_list.append(person_info)
            # Return to Faculty homepage
            faculty_page = self.driver.find_element_by_link_text("Faculty")
            faculty_page.click()
            i+=1
        print(i)
        # Save college info to csv file
        csv_columns = ['Name', 'Title', 'Bio', 'Research', 'Interests', 'College', 'Department']
        try:
            with open("data/cmu.csv", "w", newline='') as csvfile:
                writer = csv.DictWriter(csvfile,fieldnames=csv_columns)
                writer.writeheader()
                writer.writerows(person_list)
                csvfile.close()
        except IOError:
            print("I/O Error")
        return person_list

if __name__ == '__main__':
    print('The ce.py file has been loaded.')
else:
    print('The ce.py file has been imported.')
