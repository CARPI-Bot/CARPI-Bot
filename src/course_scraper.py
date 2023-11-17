import asyncio
import aiohttp
from bs4 import BeautifulSoup, Tag
import re
import json
import time

ClientSession = aiohttp.ClientSession

"""
Example header.getText() -> CSCI 1100 - Computer Science I

Given a course title of type bs4.Tag, checks that the title contains a valid department
name, course number, and a non-empty course name. Parses the title and returns a tuple
in the form of (dept_name, course_num, course_name).
"""
async def split_course_title(header:Tag) -> tuple:
    title = header.getText()
    # Check that both the department and course number are valid 
    try:
        # There should be a hyphen in every course title
        if title.find("-"):
            title_list = title.split("-")
            course_name = "-".join(title_list[1:]).strip()
            dept_and_num = title_list[0].split()
            if len(dept_and_num) < 2:
                raise
            dept_name = dept_and_num[0].strip()
            course_num = dept_and_num[1].strip()
        # If for whatever reason there is no hyphen
        else:
            title_list = title.split()
            if len(title_list) < 3:
                raise
            course_name = "-".join(title_list[2:]).strip()
            dept_name = title_list[0].strip()
            course_num = title_list[1].strip()
        # Course numbers may contain a period
        float(course_num)
        if not (len(dept_name) == 4 and dept_name.isalpha()) or len(course_name) == 0:
            raise
    except:
        print(f"Bad course title \"{title.strip()}\", ignoring...")
        raise
    return dept_name, course_num, course_name

"""
Example course preview page: https://catalog.rpi.edu/preview_course_nopop.php?catoid=26&coid=61385

Given a course title of type bs4.Tag and a dictionary to store course attributes in,
parses all course information below the course title. Any recognized attributes in the
parsed content such as requisites, credit hours, etc. are added to the dictionary.
"""
async def parse_course_content(header:Tag, course_info:dict) -> None:
    # Start searching for the course description following the course title header
    elements = tuple(header.next_siblings)
    raw_info = ""
    # Gathers all text between the first and second <hr> tag after the header
    for i in range(len(elements)):
        if elements[i].name == "hr":
            j = i + 1
            while elements[j].name != "hr" and j < len(elements):
                if elements[j].name == "br" and len(raw_info) > 0 and raw_info[-1] != "\n":
                    raw_info += "\n"
                buffer = elements[j].get_text()
                raw_info += buffer.strip() if buffer != None else ""
                j += 1
            break
    raw_info = raw_info.strip("\n").split("\n")
    pattern = re.compile("[\W_]+")
    # Keywords match order in which attributes are listed on webpage
    misc_keywords = {
        "prerequisitescorequisites": "prereq/coreq",
        "corequisite": "coreq",
        "whenoffered": "offered",
        "crosslisted": "crosslisted",
        "colisted": "colisted",
        "credithours": "credits",
        "contactlectureorlabhours": "contact_lecture_lab_hours" 
    }
    for i, field in enumerate(raw_info):
        pair = field.split(":")
        sanitized_key = pattern.sub("", pair[0].lower())
        if sanitized_key in misc_keywords:
            # NOTE: Fix missing spaces between colons
            course_info[misc_keywords[sanitized_key]] = ":".join(pair[1:])
        else:
            if i == 0:
                course_info["description"] = field

async def scrape_course(session:ClientSession, url:str, parser:str, data:dict) -> None:
    course_info = dict()
    status_code = 0
    # Repeatedly requests course preview page until response is successful
    while status_code != 200:
        course_response = await session.get(url)
        status_code = course_response.status
    page_soup = BeautifulSoup(await course_response.text(encoding="utf-8"), parser)
    course_response.close()
    # Gets header containing the course's title
    header = page_soup.find("h1", id="course_preview_title")
    try:
        # Splits course title into multiple attributes
        course_title_tup = await split_course_title(header)
        dept_name = course_title_tup[0]
        course_info["title"] = " ".join(course_title_tup)
        course_info["code"] = course_title_tup[1]
        course_info["name"] = course_title_tup[2]
        # Parses remainder of course preview, adding to dictionary
        await parse_course_content(header, course_info)
    except:
        return
    if dept_name in data:
        data[dept_name].append(course_info)
    else:
        data[dept_name] = [course_info]

async def courses_to_dict(parser:str, domain:str, req_params:str, headers:str) -> dict:
    start_time = time.time()
    json_data = dict()
    page_num = 1
    url = f"{domain}content.php?"
    async with ClientSession(headers=headers) as session:
        while (url != None):
            page_start_time = time.time()
            search_response = await session.get(
                url = url,
                params = req_params
            )
            # Retries the request if the response fails
            if search_response.status != 200:
                print(f"Bad response from page {page_num}, retrying...")
                continue
            search_soup = BeautifulSoup(await search_response.text(), parser)
            # Finds all anchor elements that links to a course preview page
            course_anchors = search_soup.find_all(
                name = "a",
                href = re.compile("preview_course.+coid=.+")
            )
            # Retries the request if no course info appears in the response
            if len(course_anchors) == 0:
                print(f"No course results from page {page_num}, retrying...")
                continue
            # Asynchronously makes requests to all found course links, retrieving each's data
            async with asyncio.TaskGroup() as tg:
                for anchor in course_anchors:
                    tg.create_task(
                        scrape_course(
                            session = session,
                            url = f"{domain}{anchor['href']}",
                            parser = parser,
                            data = json_data
                        )
                    )
            # Finds the link to the next page of courses
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
    print(f"Total time to parse all courses: {time.time() - start_time:.2f}s")
    return json_data

async def main() -> None:
    PARSER = "html5lib"
    DOMAIN = "https://catalog.rpi.edu/"
    REQUEST_PARAMS = {
        "catoid": 26,
        "navoid": 671
    }
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46",
        "Accept-Language": "en-US,en;q=0.9"
    }
    print(f"Collecting all course data from \"{DOMAIN}\"...")
    json_data = await courses_to_dict(
        parser = PARSER,
        domain = DOMAIN,
        req_params = REQUEST_PARAMS,
        headers = HEADERS
    )
    write_start_time = time.time()
    with open("data.json", "w", encoding="utf-8") as outfile:
        json.dump(json_data, outfile, ensure_ascii=False, indent=4)
    print(f"JSON write time: {time.time() - write_start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())