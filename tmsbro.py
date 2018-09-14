import re
import smtplib
import os

# Selenium used to navigate to class page in TMS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

opts = ChromeOptions()
opts.binary_location = os.environ['GOOGLE_CHROME_BIN']
driver = webdriver.Chrome(executable_path=os.environ['CHROMEDRIVER_PATH'], chrome_options=opts)  

# Opens home page for TMS 
driver.get("https://termmasterschedule.drexel.edu/webtms_du/app?page=Home&service=page")

classData = {
  "Fall Quarter 18-19": {
    "Arts and Sciences": {
      "History": [
        "15501",
        "13534",
        "15498",
        "12945",
        "13790",
        "15506", # test course
      ]
    }
  }
}

report = 'Here is the tlsbro report:\n'
openClassExists = False

for semester, colleges in classData.items():
  driver.find_element_by_xpath('//a[contains(., "' + semester + '")]').click()
  for college, subjects in colleges.items():
    driver.find_element_by_xpath('//a[contains(., "' + college + '")]').click()
    for subject, crns in subjects.items(): 
      driver.find_element_by_xpath('//a[contains(., "' + subject + '")]').click()
      for crn in crns:
        driver.find_element_by_xpath('//a[contains(., "' + crn + '")]').click()
        html_source = driver.page_source

        # Page parsing component
        # urlopen(link).read().decode('utf-8')
        html_content = re.sub(r"[\n\t\s]*", "", html_source)
        matchClosed = re.findall('>CLOSED<', html_content);

        patternCRN = re.compile('CRN<\/td><tdclass="even"align="left">(.*)<\/td><\/tr><tr><tdclass="tableHeader">SubjectCode')
        patternSubjectCode = re.compile('SubjectCode<\/td><tdclass="odd">(.*)<\/td><\/tr><tr><tdclass="tableHeader">CourseNumber')
        patternCourseNumber = re.compile('CourseNumber<\/td><tdclass="even"align="left">(.*)<\/td><\/tr><tr><tdclass="tableHeader">Section<\/td><tdclass="odd">')

        patternCourseTitle = re.compile('Title<\/td><tdclass="odd">(.*)<\/td><\/tr><tr><tdclass="tableHeader">Campus<\/td><td')

        classCRN = ''.join(patternCRN.findall(html_content));
        classSubjectCode = ''.join(patternSubjectCode.findall(html_content));
        classCourseNumber = ''.join(patternCourseNumber.findall(html_content));
        classCourseTitle = ''.join(patternCourseTitle.findall(html_content));

        # Report compiling component
        if len(matchClosed) == 0: 
          openClassExists = True
          report += '<b>OPEN</b>: ' + classSubjectCode + ' ' + classCourseNumber + ' | ' + classCRN + ' | ' + classCourseTitle + '\n'
        else:
          report += '<b>CLOSED</b>: ' + classSubjectCode + ' ' + classCourseNumber + ' | ' + classCRN + ' | ' + classCourseTitle + '\n'
        driver.back()
      driver.back()
    driver.back()
  driver.get("https://termmasterschedule.drexel.edu/webtms_du/app?page=Home&service=page")
driver.close()

print(report)

# Email component
# Emails the report if an open class exists.
if openClassExists:
  gmail_user = 'vlgstudent036@gmail.com'  
  gmail_password = 'vlgvlgvlg123'

  sent_from = 'vlgstudent036@gmail.com'  
  to = ['vlgstudent036@gmail.com']  
  subject = 'tlsbro Report'  
  body = report

  email_text = """\  
  From: %s  
  To: %s  
  Subject: %s

  %s
  """ % (sent_from, ", ".join(to), subject, body)

  try:  
      server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
      server.ehlo()
      server.login(gmail_user, gmail_password)
      server.sendmail(sent_from, to, email_text)
      server.close()

      print('Email sent!')
  except:  
      print('Something went wrong...')