from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
import pandas as pd
from pathlib import Path
import json


def get_jobs(keyword, num_jobs, verbose, path, slp_time):
    
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    
    #Initializing the webdriver
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    #Uncomment the line below if you'd like to scrape without a new Chrome window every time.
    options.add_argument('headless')
    
    #Change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.set_window_size(1120, 1000)
    
    url = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword="+keyword+"&sc.keyword="+keyword+"&locT=&locId=&jobType="
    #url = 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword="' + keyword + '"&locT=C&locId=1147401&locKeyword=San%20Francisco,%20CA&jobType=all&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=100&cityId=-1&minRating=0.0&industryId=-1&sgocId=-1&seniorityType=all&companyId=-1&employerSizes=0&applicationType=0&remoteWorkType=0'
    print(url)
    driver.get(url)
    jobs = []
    patience = 0
    while len(jobs) < num_jobs:  #If true, should be still looking for new jobs.
        
        #Let the page load. Change this number based on your internet speed.
        #Or, wait until the webpage is loaded, instead of hardcoding it.
        time.sleep(slp_time)
        #Test for the "Sign Up" prompt and get rid of it.
        # try:
        #     driver.find_element_by_class_name("selected").click()
        # except ElementClickInterceptedException:
        #     pass

        # if num_jobs % 30 == 0:
        #     try:
        #         driver.find_element_by_xpath('//*[@id="FooterPageNav"]/div/ul/li[7]/a').click() #clicking to the X.
        #         print(' Next Page Opened')
        #     except NoSuchElementException:
        #         print(' Next Page Button Failed')
        #     pass
        time.sleep(.1)

        try:
            driver.find_element_by_css_selector('[alt="Close"]').click() #clicking to the X.
            # print(' x out worked')
        except BaseException as e:
            # print(' x out failed')
            pass

        job_buttons = []
        #Going through each job in this page
        try: 
            job_buttons = driver.find_elements_by_class_name("react-job-listing")  #jl for Job Listing. These are the buttons we're going to click.
        except BaseException as e:
            print(' ERROR job_buttons', e)
            
        for job_button in job_buttons:  
            
            print("Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))
            if len(jobs) >= num_jobs:
                break

            job_button.click()  #You might 
            try:
                driver.find_element_by_css_selector('[alt="Close"]').click() #clicking to the X.
                # print(' x out worked')
            except NoSuchElementException:
                # print(' x out failed')
                pass

            time.sleep(1)
            collected_successfully = False
            attempt_count = 0
            while not collected_successfully and attempt_count < 10:
                try:
                    print("***********")
                    company_name = driver.find_element_by_xpath('//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div[3]/div[1]/div[1]').text.strip().split('\n')[0]
                    location = driver.find_element_by_xpath('//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div[3]/div[1]/div[3]').text.strip()
                    job_title = driver.find_element_by_xpath('//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div[3]/div[1]/div[2]').text.strip()
                    job_description = driver.find_element_by_xpath('.//div[@class="jobDescriptionContent desc"]').text.strip()
                    # print(company_name , " * ", location, " * ", job_title ," * ", job_description)
                    collected_successfully = True
                except BaseException as e:
                    company_name = -1
                    location = -1
                    job_title = -1
                    job_description = -1
                    print(e)
                    attempt_count +=1
                    time.sleep(5)

            
            try:
                salary_estimate = driver.find_element_by_xpath('//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div[3]/div[1]/div[4]/span').text.split("(")[0]
            except BaseException as e:
                print(' ERROR element ', e)
                salary_estimate = -1 #You need to set a "not found value. It's important."
            
            try:
                rating = driver.find_element_by_xpath('//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div[3]/div[1]/div[1]/span').text
            except BaseException as e:
                print(' ERROR element ', e)
                rating = -1 #You need to set a "not found value. It's important."

            #Printing for debugging
            if verbose:
                print("Job Title: {}".format(job_title))
                print("Salary Estimate: {}".format(salary_estimate))
                print("Job Description: {}".format(job_description[:500]))
                print("Rating: {}".format(rating))
                print("Company Name: {}".format(company_name))
                print("Location: {}".format(location))

            #Going to the Company tab...
            #clicking on this:
            #<div class="tab" data-tab-type="overview"><span>Company</span></div>
            try:
                # driver.find_element_by_xpath('.//div[@class="tab" and @data-tab-type="overview"]').click()

                # Headquarter not available in updated page
                # try:
                #     #<div class="infoEntity">
                #     #    <label>Headquarters</label>
                #     #    <span class="value">San Francisco, CA</span>
                #     #</div>
                #     headquarters = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Headquarters"]//following-sibling::*').text
                # except BaseException as e:
                #     print(' ERROR element ', e)
                #     headquarters = -1

                try:
                    size = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[1]/span[2]').text
                except BaseException as e:
                    print(' ERROR ', company_name, e)
                    size = -1

                try:
                    founded = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[2]/span[2]').text
                except BaseException as e:
                    print(' ERROR ', company_name, e)
                    founded = -1

                try:
                    type_of_ownership = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[2]/span[2]').text
                except BaseException as e:
                    print(' ERROR ', company_name, e)
                    type_of_ownership = -1

                try:
                    industry = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[4]/span[2]').text
                except BaseException as e:
                    print(' ERROR ', company_name, e)
                    industry = -1

                try:
                    sector = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[5]/span[2]').text
                except BaseException as e:
                    print(' ERROR ', company_name, e)
                    sector = -1

                try:
                    revenue = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[6]/span[2]').text
                except BaseException as e:
                    print(' ERROR ', company_name, e)
                    revenue = -1

                # Competitors not available in updated page
                # try:
                #     competitors = driver.find_element_by_xpath('.//div[@class="infoEntity"]//label[text()="Competitors"]//following-sibling::*').text
                # except BaseException as e:
                #     print(' ERROR element ', e)
                #     competitors = -1

            except NoSuchElementException:  #Rarely, some job postings do not have the "Company" tab.
                headquarters = -1
                size = -1
                founded = -1
                type_of_ownership = -1
                industry = -1
                sector = -1
                revenue = -1
                competitors = -1

            if attempt_count>3:
                patience+=1
                if (patience>=50):
                    return pd.DataFrame(jobs)

            if verbose:
                print("Headquarters: {}".format(headquarters))
                print("Size: {}".format(size))
                print("Founded: {}".format(founded))
                print("Type of Ownership: {}".format(type_of_ownership))
                print("Industry: {}".format(industry))
                print("Sector: {}".format(sector))
                print("Revenue: {}".format(revenue))
                print("Competitors: {}".format(competitors))
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            jobs.append({"Job Title" : job_title,
            "Salary Estimate" : salary_estimate,
            "Job Description" : job_description,
            "Rating" : rating,
            "Company Name" : company_name,
            "Location" : location,
            # "Headquarters" : headquarters,
            "Size" : size,
            "Founded" : founded,
            "Type of ownership" : type_of_ownership,
            "Industry" : industry,
            "Sector" : sector,
            "Revenue" : revenue,
            # "Competitors" : competitors
            })
            #add job to jobs
            
            
        #Clicking on the "next page" button
        try:
            driver.find_element_by_xpath('//*[@id="FooterPageNav"]/div/ul/li[7]/a').click()
        except BaseException as e:
            print("ERROR ON NEXT PAGE ", e)
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs)))
            break

    return pd.DataFrame(jobs)  #This line converts the dictionary object into a pandas DataFrame.

# CHROME_DRIVER_PATH = "/mnt/shared-dev/Development/Eisha/Glassdoor-Salary-Prediction/chromedriver"
CHROME_DRIVER_PATH = "Data Scraping/chromedriver.exe"

with open("Data Scraping/input_jobs.json") as f:
    input_jobs = json.load(f)
    all_jobs = []
    file_path = Path("glassdoor_jobs_new.csv")
    for i in range(len(input_jobs['job titles'])):
        try:
            print("fetching jobs for {}".format(input_jobs['job titles'][i]))
            x = pd.DataFrame()
            x = get_jobs(input_jobs['job titles'][i], input_jobs['job count'], False, CHROME_DRIVER_PATH, 30)
            all_jobs.append(x)

            if file_path.exists():
                x.to_csv(file_path, header=False, mode='a')
            else:
                x.to_csv(file_path, header=True, mode='w')

            time.sleep(25)
        except BaseException as e:
            print(" ERROR ", e)
            print("couldn't fetch jobs for {}".format(input_jobs['job titles'][i]))
            continue

df = pd.concat(all_jobs)
df.to_csv('../glassdoor_jobs_all.csv')
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#     print(df)

