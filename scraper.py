from bs4 import BeautifulSoup
import colorama
import json
import requests as rq
import time
import re
import random
def parser(html:str,name:str):
    dict_ = {}
    colorama.init(autoreset=True)
    soup = BeautifulSoup(html, "html.parser")
    if "ponisha" in name:
        find_all_div = soup.find_all("div", class_="MuiBox-root css-yd8sa2")

        for find in find_all_div:
            if not re.search("فروشگاه",find.text):
                

                skills = set()
                skill_div = find.find_next("div", class_="MuiBox-root css-wgqnl1")

                link = ""
                if skill_div:
                    a_tag = skill_div.find_next("a", href=True)
                    if a_tag:
                        link = a_tag.get("href")

                    for skill_span in skill_div.find_all("span", class_="MuiTypography-root MuiTypography-subtitle2 css-ol4h9u"):
                        skills.add(skill_span.text)

                parts = name.split("_")
                domain = ".".join(parts[:2])
                file1 = "https://" + domain + "/"

                dict_[find.find_next("span").text] = {
                    "skills": list(skills),
                    "project link": file1 + link
                }
    elif "karlancer" in name:
        find_all_div = soup.find_all("div",{"class":"bg-white br-9 text-right position-relative border-1-transparent card-hover p-30-20"})
        for find_ in find_all_div:
            if not re.search("فروشگاه",find_.text):
                skills = set()
                div_skill = find_.find("div",{"class":"overflow-hidden skills-container max-h-transition-0-3 d-none d-sm-block max-h-30 mt-20"})
                for skill in (div_skill.find_all("span",{"class":"ellipsis px-2 d-flex align-items-center h-30 py-1"})):
                    
                    skills.add(skill.text)
                parts = name.split("_")
                domain = ".".join(parts[:3])
                file1 = "https://" + domain + "/"
                project_link = file1 + (find_.find("a",href=True).get("href"))
                dict_[find_.find("h4").text] = {"skills":list(skills),"project link":project_link}
            # print(dict_)
    projects = {}
    for title, info in dict_.items():
        skills = info["skills"]
        if ("طراحی سایت" in title) or any(("طراحی سایت" in x) or ("web" in x.lower()) for x in skills):
            # print(title, info)
            projects[title] = info
    try:
        with open("output.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        if not isinstance(existing_data, dict):
            existing_data = {}
    except:
        existing_data = {}


    combined_data = {**existing_data, **projects}
    with open("output.json", "w", encoding="utf-8") as f:  
        json.dump(combined_data, f, ensure_ascii=False, indent=4)
site_list = [
    "https://www.karlancer.com/jobs/web-design?page={number}",
    "https://ponisha.ir/search/projects?page={number}&query=%D8%B7%D8%B1%D8%A7%D8%AD%DB%8C%20%D8%B3%D8%A7%DB%8C%D8%AA&order=approved_at%7Cdesc&category=-&promotion=-&filterByProjectStatus=open"
]


common_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd", 
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1", 
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Priority": "u=0, i", 
    "TE": "trailers", 
}

print("شروع جمع‌آوری صفحات وب...")

for i in range(len(site_list)):
    site_name_for_filename = site_list[i].split('/')[2].replace('.', '_') 
    
    print(f"\nدر حال پردازش سایت: {site_name_for_filename} (ایندکس: {i})")
    
    for number in range(1, 11): 
        if number > 1 and i == 0:
            break
        url = site_list[i].format(number=number)
        print(f"درخواست URL: {url}")
        try:
            response = rq.get(url, headers=common_headers, timeout=15)
            response.raise_for_status()
            text = response.text
            parser(text, site_name_for_filename)
        except rq.exceptions.Timeout:
            print(f"خطا: درخواست برای {url} زمان‌دار شد (Timeout).")
            break
        except rq.exceptions.RequestException as e:
            print(f"خطا در ارسال درخواست برای {url}: {e}")
            break 
        except Exception as e: 
            print(f"یک خطای غیرمنتظره رخ داد برای {url}: {e}")
            break
        time.sleep(int(random.randint(2,10))) 
