import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import json
import time

ClientSession = aiohttp.ClientSession

async def get_course_info(session:ClientSession, url:str, parser:str, data:dict) -> None:
    info = dict()
    status_code = 0
    # Repeatedly requests the course webpage until the response is successful
    while (status_code != 200):
        course_response = await session.get(url=url)
        status_code = course_response.status
    course_soup = BeautifulSoup(await course_response.text(), parser)
    # Gets the header containing the course's name
    header = course_soup.find("h1", id="course_preview_title")
    info["title"] = header.string
    # Start searching for the course description following the course title header
    elements = list(header.next_siblings)
    course_desc, misc_info = "", ""
    # Gathers all text between the first and second <hr> tag after the header
    for i in range(len(elements)):
        if elements[i].name == "hr":
            j = i + 1
            # Between the first <hr> and <br>, read all text as the course description
            while elements[j].name != "hr":
                text = elements[j].get_text()
                course_desc += text.strip() if text != None else ""
                # Between the first <br> and second <hr>, read all text as misc info
                if elements[j].name == "br":
                    k = j + 1
                    while elements[k].name != "hr":
                        text = elements[k].get_text()
                        misc_info += text.strip() if text != None else ""
                        k += 1
                    break
                j += 1
            break
    info["description"] = course_desc
    info["misc"] = misc_info
    data[info["title"]] = info

async def courses_to_json(parser:str, domain:str, href:str, req_params:str, headers:str) -> str:
    start_time = time.time()
    json_data = dict()
    page_num = 1
    url = f"{domain}{href}"
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
            # Finds all anchor elements that links to a course info preview
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
                        get_course_info(
                            session = session,
                            url = f"{domain}{anchor['href']}",
                            parser = parser,
                            data = json_data
                        )
                    )
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
    print(f"Total time to parse all courses: {time.time() - start_time:.2f}s")
    global write_start_time
    write_start_time = time.time()
    json_obj = json.dumps(json_data, indent = 4)
    return json_obj

async def main() -> None:
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
    json_obj = await courses_to_json(
        parser = PARSER,
        domain = DOMAIN,
        href = HREF,
        req_params = REQUEST_PARAMS,
        headers = HEADERS
    )
    with open("data.json", "w") as outfile:
        outfile.write(json_obj)
    print(f"Total time to write to JSON: {time.time() - write_start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())