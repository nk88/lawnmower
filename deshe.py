# -*- coding: utf-8 -*-

from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re

browser = webdriver.Chrome()

DESHE_CONNECTION_URL = "https://%s:%s@deshe.matrix.co.il/deshe/"
WORKER_NAME = u'נועם מרקביץ (5084)'
CUSTOMER_NAME = u'משרד הבטחון-מפא"ת'
PROJECT_NAME = u'נוסבול'
HALF_AN_HOUR = u'קיזוז 0.5 שעה הפסקה צעל 6 שעות עבודה'
DESCRIPTION = "."
USERNAME = "noammar"
PASSWORD = 'UGFzc3dvcmQ0JA==\n'.decode("base64")
DATERANGE_REGEX = re.compile("(?P<from>\d{2}:\d{2}) - (?P<to>\d{2}:\d{2})")
HOUR_FORMAT = '%H:%M'

def choose_customer(customer_name):
    browser.execute_script("document.getElementById(\"ddlCustomers\").parentElement.querySelector('.ui-icon-triangle-1-s').click()")
    browser.execute_script("Array.prototype.slice.call(document.querySelectorAll(\".ui-menu-item\")).filter(function(v) { return v.innerText.indexOf('%s') > -1;})[0].click()" % customer_name)
    #customer = browser.find_element_by_name("ddlCustomers")
    #found = False
    #for option in customer.find_elements_by_tag_name('option'):
    #    if option.get_attribute("text") == customer_name:
    #        found = True
    #        break
    #if not found:
    #    raise Exception("Customer not found")

def choose_task(task_name):
    browser.execute_script("document.getElementById(\"ddlTasks\").parentElement.querySelector('.ui-icon-triangle-1-s').click()")
    browser.execute_script("Array.prototype.slice.call(document.querySelectorAll(\".ui-menu-item\")).filter(function(v) { return v.innerText.indexOf('%s') > -1;})[0].click()" % task_name)
    #task = browser.find_element_by_name("ddlTasks")
    #found = False
    #for option in task.find_elements_by_tag_name('option'):
    #    if option.text == task_name:
    #        option.click()
    #        found = True
    #        break
    #if not found:
    #    raise Exception("Task %s not found" % task_name)
        
def choose_project(project_name):
    browser.execute_script("document.getElementById(\"ddlProjects\").parentElement.querySelector('.ui-icon-triangle-1-s').click()")
    browser.execute_script("Array.prototype.slice.call(document.querySelectorAll(\".ui-menu-item\")).filter(function(v) { return v.innerText.indexOf('%s') > -1;})[0].click()" % project_name)
    #project = browser.find_element_by_name("ddlProjects")
    #found = False
    #for option in project.find_elements_by_tag_name('option'):
    #    if option.text == project_name:
    #        option.click()
    #        found = True
    #        break
    #if not found:
    #    raise Exception("Project %s not found" % project_name)
    
def fill_description(description):
    description_textarea = browser.find_element_by_name("txtElaboration")
    description_textarea.send_keys(DESCRIPTION)

def select_day(day_to_select):
    # Calendar
    calendar = browser.find_element_by_id("generalCalendar")

    # Select day of the month
    for day in calendar.find_elements_by_class_name("calDay") + calendar.find_elements_by_class_name("calSelectedDay"):
        if day.text == str(day_to_select):
            day.click()
            break
            
def choose_time(from_time, to_time):
    from_hours = browser.find_element_by_id("txtFromHours")
    from_minutes = browser.find_element_by_id("txtFromMinutes")
    to_hours = browser.find_element_by_id("txtToHours")
    to_minutes = browser.find_element_by_id("txtToMinutes")
    from_hours.clear()
    from_hours.send_keys(from_time.split(":")[0])
    from_minutes.clear()
    from_minutes.send_keys(from_time.split(":")[1])
    to_hours.clear()
    to_hours.send_keys(to_time.split(":")[0])
    to_minutes.clear()
    to_minutes.send_keys(to_time.split(":")[1])

def select_month(month_to_select):
    current_month = datetime.now().month
    if month_to_select - current_month > 0:
        # Click next month
        click_element = browser.find_element_by_id("Header1_MonthAndYearBrowser1_imgbtnNextMonth")
    elif month_to_select - current_month < 0:
        # Click previous month
        click_element = browser.find_element_by_id("Header1_MonthAndYearBrowser1_imgbtnPrevMonth") 
    else:
        return
        
    for _ in range(abs(month_to_select - current_month)):
        click_element.click()
    
    
def fill_day(day_to_select, from_time, to_time):
    """
    Fills an entire work day.
    If the work day is more than 6 hours, add a 30 minutes break
    """
    browser.switch_to_default_content()
    browser.switch_to.frame(browser.find_elements_by_tag_name("iframe")[3])
    browser.switch_to.frame(browser.find_elements_by_tag_name("frame")[1]) #u'frmHoursReportsDataEntry'
    
    select_day(day_to_select)
    
    from_time_datetime = datetime.strptime(from_time, HOUR_FORMAT)
    to_time_datetime = datetime.strptime(to_time, HOUR_FORMAT)
    tdelta = to_time_datetime - from_time_datetime
    if tdelta.seconds > 21600: # Bigger than 6 hours
        choose_project(PROJECT_NAME)
        choose_task(WORKER_NAME)
        fill_description(DESCRIPTION)
        choose_time(from_time, "12:00")
        save()
        
        choose_task(HALF_AN_HOUR)
        fill_description(DESCRIPTION)
        choose_time("12:00", "12:30")
        save()
        
        choose_task(WORKER_NAME)
        fill_description(DESCRIPTION)
        choose_time("12:30", to_time)
        save()
    else:
        choose_task(WORKER_NAME)
        choose_time(from_time, to_time)
        save()

def get_hours(monthday_element, selected_day):
    """
    Get a row in the table frmHoursReportList, return the time range in it
    """
    date_range = monthday_element.find_elements_by_tag_name("td")[4].text
    pattern = DATERANGE_REGEX.search(date_range)
    #from_time_datetime = datetime.strptime(pattern.group("from"), HOUR_FORMAT)
    #to_time_datetime = datetime.strptime(pattern.group("to"), HOUR_FORMAT)
    #TODO: should return the hours and not fill the day
    fill_day(selected_day, pattern.group("from"), pattern.group("to"))

def add_break(day_to_select, selected_month):
    """
    Adds a half an hour break in a work day only if the work day is more than 6 hours
    """
    browser.switch_to_default_content()
    browser.switch_to.frame(browser.find_elements_by_tag_name("iframe")[3])
    browser.switch_to.frame(browser.find_elements_by_tag_name("frame")[0]) #u'frmHoursReportList'
    monthdays = browser.find_elements_by_class_name("seperateDay") # Work day row
    date_to_select = date(date.today().year, selected_month, day_to_select)
    
    # gridNoneWorkingDay
    for monthday_element in monthdays:
        if monthday_element.get_attribute("rowdate") == date_to_select.strftime("%Y%m%d"):
            get_hours(monthday_element, day_to_select)
            break

    
def save():
    save = browser.find_element_by_name("btnSaveNew")
    save.click()

def main():
    MONTH = 9
    browser.get(DESHE_CONNECTION_URL % (USERNAME, PASSWORD) )
    select_month(MONTH)
    browser.switch_to.frame(browser.find_elements_by_tag_name("iframe")[3])
    browser.switch_to.frame(browser.find_elements_by_tag_name("frame")[1]) #u'frmHoursReportsDataEntry'
    choose_customer(CUSTOMER_NAME)
    
    while True:
        import pdb; pdb.set_trace()
        result = raw_input("1. fill day, 2. add_break: ")
        if result == "1":
            day = raw_input("enter day: ")
            from_time = raw_input("enter from time: ")
            to_time = raw_input("enter to time: ")
            fill_day(day, from_time, to_time)
        elif result == "2":
            day = raw_input("enter day: ")
            add_break(int(day), MONTH)    
        #add_break(31, MONTH)
        
    browser.close()

    
if __name__ == "__main__":
    main()
