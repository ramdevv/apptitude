import urllib.parse
import requests
from bs4 import BeautifulSoup
import re


"""
location=San+Francisco: The jobs should be located in San Francisco.

f_TPR=1M: Only show jobs posted within the last 1 month.

f_SB2=70000: Filter jobs where the salary is $70,000 or more.

f_E=Mid: Filter jobs for mid-level experience.

f_WT=Remote: Only show remote jobs.

f_JT=Full-Time: Only show full-time jobs.

start=0: Start pagination at the first result (page 1).

limit=20: Limit the results to 20 jobs.



what have i gotten till now:
1)name of the company 
2)date it was posted
3)
"""


# making the class for the url
class UrlAttributes:
    def __init__(self, query_obj):
        self.host = query_obj.get("host", "www.linkedin.com")
        self.keyword = query_obj.get("keyword", "").replace(" ", "+")
        self.location = query_obj.get("location", "").replace(" ", "+")
        self.dateSincePosted = query_obj.get("dateSincePosted", "")
        self.jobType = query_obj.get("jobType", "")
        self.remoteFilter = query_obj.get("remoteFilter", "")
        self.salary = query_obj.get("salary", "")
        self.experienceLevel = query_obj.get("experienceLevel", "")
        self.sortBy = query_obj.get("sortBy", "")
        self.limit = query_obj.get("limit", 12)
        self.has_verification = query_obj.get("has_verification", False)
        self.under_10_applicants = query_obj.get("under_10_applicants", False)
        self.fetch_description = query_obj.get("getDiscription", False)

    # methods for calling the
    def get_date_since_posted(self):
        date_range = {
            "past month": "r2592000",
            "past week": "r604800",
            "24hr": "r86400",
        }
        return date_range.get(self.dateSincePosted.lower(), "")

    def get_experience_level(self):
        experience_range = {
            "internship": "1",
            "entry level": "2",
            "associate": "3",
            "senior": "4",
            "director": "5",
            "executive": "6",
        }
        return experience_range.get(self.experienceLevel.lower(), "")

    def get_job_type(self):
        job_type_range = {
            "full time": "F",
            "part time": "P",
            "contract": "C",
            "temporary": "T",
            "volunteer": "V",
            "internship": "I",
        }
        return job_type_range.get(self.jobType.lower(), "")

    def get_remote_filter(self):
        remote_filter_range = {
            "on-site": "1",
            "remote": "2",
            "hybrid": "3",
        }
        return remote_filter_range.get(self.remoteFilter.lower(), "")

    def get_salary(self):
        salary_range = {
            "40000": "1",
            "60000": "2",
            "80000": "3",
            "100000": "4",
            "120000": "5",
        }
        return salary_range.get(str(self.salary), "")

    def get_limit(self):
        return self.limit

    def get_has_verification(self):
        return "true" if self.has_verification else "false"

    def get_under_10_applicants(self):
        return "true" if self.under_10_applicants else "false"

    def get_job_description(self):
        return "true" if self.get_job_description else "false"

    def final_url(self, start=0):
        base_url = f"https://{self.host}/jobs-guest/jobs/api/seeMoreJobPostings/search?"  # this is the base of the url on which it will be made

        params = (
            {}
        )  # this is the list which would be appended into the base url to make the final url
        if self.keyword:
            params["keyword"] = (
                self.keyword
            )  # we have added the value of the keyword in the params dict
        if self.location:
            params["location"] = self.location
        if self.get_date_since_posted():
            params["f_TPR"] = self.get_date_since_posted()
        if self.get_salary():
            params["f_SB2"] = self.get_salary()
        if self.get_experience_level():
            params["f_E"] = self.get_experience_level()
        if self.get_remote_filter():
            params["f_WT"] = self.get_remote_filter()
        if self.get_job_type():
            params["f_JT"] = self.get_job_type()
        if self.get_has_verification():
            params["f_VJ"] = self.get_has_verification()
        if self.get_under_10_applicants():
            params["f_EA"] = self.get_under_10_applicants()
        if self.get_job_description():
            params["f_JD"] = self.get_job_description()
        if self.get_limit is not None:
            params["limit"] = self.get_limit()

        if self.sortBy == "resent":
            params["sortBy"] = "DD"  # this is written to sort by the most recent jobs
        if self.sortBy == "relevent":
            params["sortBy"] == "R"  # this sorts by the the most relevent jobs

        final_url = urllib.parse.urlencode(
            params
        )  # this would convert the params dict into a string

        return base_url + final_url


# driver code
user_quarrie = {
    "keyword": "Software Engineer",
    "location": "San Francisco",
    "dateSincePosted": "past month",
    "salary": "70000",
    "experienceLevel": "Mid",
    "remoteFilter": "remote",
    "jobType": "Full-Time",
    "has_verification": True,
    "under_10_applicants": False,
    "page": 1,
    "limit": 20,
}

instance_of_the_class = UrlAttributes(user_quarrie)
new_url = instance_of_the_class.final_url()
url = f"{new_url}"


# to make a cleaner for my code
def clean_text(
    text: str,
) -> str:  # this will take the string input as the parameter and will also return a str
    text = text.replace("/n", "\n")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def scrap_url(url):

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            " AppleWebKit/605.1.15 (KHTML, like Gecko)"  # this is done so linkedin does not reject our request as this request would look like a human request
            " Version/15.3 Safari/605.1.15"
        },
    )
    i = 1
    all_jobs_data = []
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        job_postings = soup.find_all("div", class_="base-search-card")

        for job in job_postings:
            title_tag = job.find("h3", class_="base-search-card__title")
            title = title_tag.text.strip() if title_tag else ""

            company_tag = job.find("h4", class_="base-search-card__subtitle")
            companyName = company_tag.text.strip() if company_tag else ""

            benefits_tag = job.find("span", class_="job-posting-benefits__text")
            job_benefits = benefits_tag.text.strip() if benefits_tag else ""

            listedDate_tag = job.find("time", class_="job-search-card__listdate")
            listedDate = listedDate_tag.text.strip() if listedDate_tag else ""

            job_sallary = job.find("span", class_="job-search-card__salary-info")
            sallary = job_sallary.text.strip() if job_sallary else "not listed"

            has_verification = job.find("span", class_="verified-job-badge__icon")
            has_verification = "Verified" if has_verification else "Not Verified"

            experience_level_tag = job.find(
                "span", class_="job-search-card__experience"
            )
            experience_level = (
                experience_level_tag.text.strip()
                if experience_level_tag
                else "Not listed"
            )

            job_type_tag = job.find("span", class_="job-search-card__job-type")
            job_type = job_type_tag.text.strip() if job_type_tag else "Not listed"

            under10_applicants_tag = job.find(
                "span", string=lambda t: t and "applicants" in t
            )
            under10_applicants = (
                under10_applicants_tag.text.strip()
                if under10_applicants_tag
                else "Applicants info not listed"
            )

            remote_filter_tag = job.find("span", string=lambda t: t and "Remote" in t)
            remote_filter = "Remote" if remote_filter_tag else "On-site/Not mentioned"

            job_link = job.find("a", class_="base-card__full-link")
            if job_link and job_link.has_attr("href"):
                single_link = job_link["href"]
                link_response = requests.get(single_link)

                if link_response.status_code == 200:
                    link_html = link_response.text
                    link_soup = BeautifulSoup(link_html, "html.parser")
                    job_description_container = link_soup.find(
                        "div", class_="description__text"
                    )
                    if job_description_container:
                        job_descriptoin = clean_text(
                            job_description_container.get_text(separator="/n")
                        )
                        all_jobs_data.append(
                            {
                                "space": f"\n\n========JOB{i}========",
                                "title": title,
                                "company": companyName,
                                "salary": sallary,
                                "date_listed": listedDate,
                                "job_benefits": job_benefits,
                                "has_verification": has_verification,
                                "experience_level": experience_level,
                                "job_type": job_type,
                                "under10_applicants": under10_applicants,
                                "remote_filter": remote_filter,
                                "job_description": job_descriptoin,
                                "space": f"========JOB{i}=========\n\n",
                            }
                        )
                        i = i + 1

                    else:
                        print("could not find the description of the container")

                else:
                    print("we did not get any response from the link")

            else:
                return "we could not append in the list"

        return all_jobs_data
    else:
        return f"message {response.status_code}"


# driver code
print(scrap_url(url))
