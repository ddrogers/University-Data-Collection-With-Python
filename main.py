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

import os
import importlib
import glob
import re
import pandas as pd

class UniversityNavigator():
    def __init__(self):
        self.academics_driver = ''
        # Initialize variables for holding university object(s)
        self.university_menu_list = []
        self.university_choice = int()
        # Initialize variables for holding college object(s)
        self.college_menu_list = []
        self.college_choice = int()
        # Initialize variables for holding department object(s)
        self.department_menu_list = []
        self.department_choice = int()
        self.department_choice_list = []
        self.college_dictionary = {}
        self.college_initials = {}

    def find_available_universities(self):
        """
            Access files within each university subpackage to return the name of available universities.
            """
        # Search system for udc package and the university modules within
        university_package_path = "udc/university/*"
        universities = glob.glob(university_package_path)
        for university in universities:
            pack_length = len(university_package_path)
            if re.search('^[a-z]+', university[(pack_length - 1):]):
                option = university[(pack_length - 1):]
                print(option)
                # Find the __init__module within the package
                module_path = university_package_path[:-1] + option
                print(module_path)
                module_name = "{}.{}".format(module_path.replace("/", "."), option)
                class_name = "{}Driver".format(option.upper())
                print(module_name)
                # Run __init__.py file
                module = importlib.import_module(module_name)
                self.university_attribute = getattr(module, class_name)
                self.university_menu_list.append(self.university_attribute.university_name)


    def find_available_colleges(self):
        '''This function creates a menu for all available college pacakages in the
                            udc package'''
        # Inform user to make a selection
        # self.college_menu_list = []
        # Search system for udc pacakge and the university modules within
        college_package_path = "udc/university/*/college/*"
        # Take user to another menu for Colleges and Schools at a University
        subpackages = glob.glob(college_package_path)
        for subpackage in subpackages:
            if re.search('[a-z]+.py', subpackage):
                module_name = subpackage[:-3].replace("\\", ".").replace("/", ".")
                # print(module_name)
                path_len = len(re.search('(\w+[.])+', module_name).group())
                class_name = "{}Driver".format(module_name[path_len:].upper())
                # print(class_name)
                module = importlib.import_module(module_name)
                method = getattr(module, class_name)
                self.college_menu_list.append(method.college_name)
                self.college_initials[method.college_name] = re.search('[a-z]+.py', subpackage).group()[:-3]

    def find_available_departments(self):
        """Print available department names"""
        # Inform user to make a selection
        college_name = self.college_menu_list[self.college_choice]
        department_package_path = "udc/university/*/college/departments/" + self.college_initials[college_name] + "_*"
        # Print out list of available departments
        # Take user to another menu for Departments within a College
        subpackages = glob.glob(department_package_path)
        for subpackage in subpackages:
            if re.search('[a-z]+.py', subpackage):
                module_name = subpackage[:-3].replace("\\", ".").replace("/", ".")
                # print(module_name)
                path_len = len(re.search('(\w+[.])+\w+_', module_name).group())
                class_name = "{}Driver".format(module_name[path_len:].upper())
                # print(class_name)
                module = importlib.import_module(module_name)
                department_choice = getattr(module, class_name)
                self.department_choice_list.append(department_choice)
                self.department_menu_list.append(department_choice.department_name)

    def university_menu(self):
        # Print list of available options
        for item in enumerate(self.university_menu_list):
            print("{}. {}".format(item[0]+1, item[1]))

        self.university_choice = int(input("Select a University: "))
        os.system("cls")
        print("University: " + self.university_menu_list[self.university_choice-1])
        # Store university class object
        self.university_driver = self.university_attribute()

    def college_menu(self):
        # Print list of available options
        for item in enumerate(self.college_menu_list):
            print("{}. {}".format(item[0]+1, item[1]))
        self.college_choice = int(input("Select a College: "))
        os.system("cls")
        print("University: " + self.university_menu_list[self.university_choice-1])
        print("College: " + self.college_menu_list[self.college_choice-1])
        # Open webpage for selected College
        # print(self.college_menu_list[self.college_choice])

    def department_menu(self):
        # Print list of available options
        for item in enumerate(self.department_menu_list):
            print("{}. {}".format(item[0]+1, item[1]))
        self.dept_choice = int(input("Select a Department: "))
        os.system("cls")
        print("University: " + self.university_menu_list[self.university_choice-1])
        print("College: " + self.college_menu_list[self.college_choice-1])
        print("Department: " + self.department_menu_list[self.dept_choice-1])
        # Run selected department script from udc subdirectory
        # Access Department Page
        # Access Faculty webpage
        department_object = self.department_choice_list[self.dept_choice-1]()
        department_object.open_homepage()
        department_object.access_faculty_webpage()
        department_object.connect_to_database()
        department_object.insert_to_database()
        department_object.close_browser_window()
        self.udc_df = pd.DataFrame(department_object.view_database(),
                                   columns=["id", "University","College", "Department", "Position", "Name", "Title",
                                            "Bio", "Research", "Interests"])
        print(self.udc_df)

    def save_db_to_csv(self):
        self.udc_df.to_csv("data/udc.csv",index=False)

    def menu_navigator(self):
        self.find_available_universities()
        self.find_available_colleges()
        self.find_available_departments()
        os.system("cls")
        self.university_menu()
        self.college_menu()
        self.department_menu()
        while True:
            options = """ 
            Please select an option (Input a value of 1, 2, 3, or 4):
            1. Select another university. 
            2. Select another college.
            3. Select another department. 
            4. Exit.
            """
            choice = int(input(options))
            os.system("cls")
            if choice == 1:
                self.university_menu()
                self.college_menu()
                self.department_menu()
            elif choice == 2:
                print("University: " + self.university_menu_list[self.university_choice - 1])
                self.college_menu()
                self.department_menu()
            elif choice == 3:
                print("University: " + self.university_menu_list[self.university_choice - 1])
                print("College: " + self.college_menu_list[self.college_choice - 1])
                self.department_menu()
            else:
                print("Thank you for using the University Data Collection Demo."
                      " Goodbye.")
                self.save_db_to_csv()
                exit()

    def display_copyright(self):
        copyright = """
            University Data Collector  Copyright (C) 2019  Donald D. Rogers II
            This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
            This is free software, and you are welcome to redistribute it
            under certain conditions; type `show c' for details.

            To start program, enter 'start'.
            """
        while True:
            user_start = input(copyright)
            if user_start == 'show w':
                print("Please review warranty as given by GNU General Public License."
                      "License can be found at the following url: <https://www.gnu.org/licenses/>")
            elif user_start == 'show c':
                print("Please review conditions as given by GNU General Public License."
                      "License can be found at the following url: <https://www.gnu.org/licenses/>")
            elif user_start == 'start':
                break


if __name__ == "__main__":
    print("The udc_main.py file has been loaded!")
    un = UniversityNavigator()
    un.display_copyright()
    print("Welcome to the University Data Collection Demonstration Application:")
    un.menu_navigator()
else:
    print("The udc_main.py file has been imported!")