import requests
from bs4 import BeautifulSoup
import re
import json
import time

# Accesses a specific course's preview webpage and gathers data, including the course title
# and description given a HTTP session, URL, and headers to use in the request.
def get_course_info(session:requests.Session, url:str, parser:str, headers:dict) -> dict:
    info = dict()
    status_code = 0
    # Repeatedly requests the course webpage until the response is successful
    while (status_code != 200):
        course_response = session.get(
            url = url,
            headers = headers
        )
        status_code = course_response.status_code
    course_soup = BeautifulSoup(course_response.content, parser)
    # Gets the header containing the course's name
    header = course_soup.find("h1", id="course_preview_title")
    info["title"] = header.string
    # Start searching for the course description following the course title header
    elements = list(header.next_siblings)
    course_desc = ""
    # Gathers all text between the first <hr> and <br> tag after the header
    for i in range(len(elements)):
        if elements[i].name == "hr":
            for j in range(i + 1, len(elements)):
                if elements[j].name == "br":
                    break
                text = elements[j].string
                course_desc += text.strip() if text != None else ""
            break
    info["description"] = course_desc
    return info

def courses_to_json(parser:str, domain:str, href:str, req_params:str, headers:str) -> str:
    start_time = time.time()
    json_data = dict()
    # Creates a HTTP session
    session = requests.Session()
    page_num = 1
    url = f"{domain}{href}"
    while (url != None):
        page_start_time = time.time()
        # Submits a request for a page containing many course links
        search_response = session.get(
            url = url,
            params = req_params,
            headers = headers
        )
        # Retries the request if the response fails
        if search_response.status_code != 200:
            print(f"Bad response from page {page_num}, retrying...")
            continue
        search_soup = BeautifulSoup(search_response.content, parser)
        # Returns all anchor elements that links to a course info preview
        course_anchors = search_soup.find_all(
            name = "a",
            href = re.compile("preview_course.+coid=.+")
        )
        # Also retries the request if no course info appears
        if len(course_anchors) == 0:
            print(f"No course results from page {page_num}, retrying...")
            continue
        # Gets individual course preview data from each anchor
        for anchor in course_anchors:
            temp_dict = get_course_info(
                session = session,
                url = f"{DOMAIN}{anchor['href']}",
                parser = PARSER,
                headers = headers
            )
            json_data[temp_dict["title"]] = temp_dict
        # Finds the first link to the next page
        page_anchor = search_soup.find(
            name = "a",
            attrs = {
                "href": re.compile(".*content.php?.+"),
                "aria-label": re.compile(f"Page {page_num + 1}")
            }        
        )
        url = f"{domain}{page_anchor['href']}" if page_anchor else None
        print(f"Page {page_num} parse time: {time.time() - page_start_time:.2f}s")
        page_num += 1
    json_obj = json.dumps(json_data, indent = 4)
    print(f"Total time for retrieving all course data: {time.time() - start_time:.2f}s")
    return json_obj
    
if __name__ == "__main__":
    PARSER = "html5lib"
    DOMAIN = "https://catalog.rpi.edu/"
    HREF = "content.php?"
    REQUEST_PARAMS = {
        "catoid": 26,
        "navoid": 671
    }
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46"
    }
    json_obj = courses_to_json(
        parser = PARSER,
        domain = DOMAIN,
        href = HREF,
        req_params = REQUEST_PARAMS,
        headers = HEADERS
    )
    with open("data.json", "w") as outfile:
        outfile.write(json_obj)