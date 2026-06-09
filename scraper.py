import json
import random
import re
import time
from bs4 import BeautifulSoup
import requests as rq
from colorama import init, Fore, Style

init(autoreset=True)

def extract_phones(text):
    """استخراج شماره تلفن از متن (پشتیبانی از اعداد فارسی و انگلیسی)"""
    # تبدیل اعداد فارسی به انگلیسی
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    for i in range(10):
        text = text.replace(persian_digits[i], english_digits[i])
    
    # الگوی شماره تلفن: 09123456789 یا 02112345678 یا 9123456789
    phone_pattern = r"(\d{11,12})|(\d{4,5}[-]?\d{4,5})"
    phones = re.findall(phone_pattern, text)
    
    # تمیز کردن لیست
    clean_phones = []
    for p in phones:
        for part in p:
            if len(part) >= 10 and part not in clean_phones:
                clean_phones.append(part.strip())
    
    return clean_phones

def parser(html, site_name):
    """پارس کردن صفحات پونیشا و کارلنسر و استخراج اطلاعات"""
    results = []
    soup = BeautifulSoup(html, "html.parser")
    
    if "ponisha" in site_name:
        items = soup.find_all("div", class_="MuiBox-root css-yd8sa2")
        
        for item in items:
            # فیلتر فروشگاه‌ها
            if re.search("فروشگاه", item.text):
                continue
            
            # استخراج عنوان
            title_tag = item.find("span")
            title = title_tag.text.strip() if title_tag else "بدون عنوان"
            
            # استخراج مهارت‌ها
            skills = []
            skill_div = item.find_next("div", class_="MuiBox-root css-wgqnl1")
            if skill_div:
                skill_spans = skill_div.find_all("span", class_="MuiTypography-root MuiTypography-subtitle2 css-ol4h9u")
                for s in skill_spans:
                    skills.append(s.text.strip())
            
            # استخراج لینک
            link = ""
            if skill_div:
                a_tag = skill_div.find_next("a", href=True)
                if a_tag:
                    link = "https://ponisha.ir" + a_tag.get("href")
            
            # استخراج شماره تلفن
            phones = extract_phones(item.text)
            
            results.append({
                "title": title,
                "skills": skills,
                "link": link,
                "phones": phones if phones else ["پیدا نشد"]
            })
    
    elif "karlancer" in site_name:
        items = soup.find_all("div", {"class": "bg-white br-9 text-right position-relative border-1-transparent card-hover p-30-20"})
        
        for item in items:
            # فیلتر فروشگاه‌ها
            if re.search("فروشگاه", item.text):
                continue
            
            # استخراج عنوان
            title_tag = item.find("h4")
            title = title_tag.text.strip() if title_tag else "بدون عنوان"
            
            # استخراج مهارت‌ها
            skills = []
            skill_div = item.find("div", {"class": "overflow-hidden skills-container max-h-transition-0-3 d-none d-sm-block max-h-30 mt-20"})
            if skill_div:
                skill_spans = skill_div.find_all("span", {"class": "ellipsis px-2 d-flex align-items-center h-30 py-1"})
                for s in skill_spans:
                    skills.append(s.text.strip())
            
            # استخراج لینک
            link = ""
            a_tag = item.find("a", href=True)
            if a_tag:
                link = "https://www.karlancer.com" + a_tag.get("href")
            
            # استخراج شماره تلفن
            phones = extract_phones(item.text)
            
            results.append({
                "title": title,
                "skills": skills,
                "link": link,
                "phones": phones if phones else ["پیدا نشد"]
            })
    
    return results

def save_to_json(data, filename="output.json"):
    """ذخیره داده در فایل JSON"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if not isinstance(existing, list):
            existing = []
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    
    # اضافه کردن داده‌های جدید (بدون تکرار)
    existing_titles = {item["title"] for item in existing}
    for item in data:
        if item["title"] not in existing_titles:
            existing.append(item)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=4)

def save_to_excel(data, filename="output.xlsx"):
    """ذخیره داده در فایل Excel (اختیاری - نیاز به pandas و openpyxl)"""
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        # تبدیل لیست مهارت‌ها و شماره‌ها به متن
        df["skills"] = df["skills"].apply(lambda x: ", ".join(x))
        df["phones"] = df["phones"].apply(lambda x: ", ".join(x))
        df.to_excel(filename, index=False)
        print(Fore.GREEN + f"✅ فایل Excel نیز ذخیره شد: {filename}")
    except ImportError:
        print(Fore.YELLOW + "⚠️ برای ذخیره Excel به pandas و openpyxl نیاز است. نصب کنید: pip install pandas openpyxl")

# لیست سایت‌ها برای اسکرپ
site_list = [
    "https://www.karlancer.com/jobs/web-design?page={number}",
    "https://ponisha.ir/search/projects?page={number}&query=%D8%B7%D8%B1%D8%A7%D8%AD%DB%8C%20%D8%B3%D8%A7%DB%8C%D8%AA&order=approved_at%7Cdesc&category=-&promotion=-&filterByProjectStatus=open"
]

common_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

print(Fore.CYAN + "=" * 50)
print(Fore.YELLOW + "🚀 شروع اسکرپ پروژه‌های طراحی سایت")
print(Fore.CYAN + "=" * 50)

all_projects = []

for i, base_url in enumerate(site_list):
    site_name = base_url.split('/')[2].replace('.', '_')
    print(Fore.BLUE + f"\n📌 در حال پردازش: {site_name}")
    
    # تعیین تعداد صفحات بر اساس سایت
    max_pages = 5 if "ponisha" in site_name else 1  # کارلنسر فقط صفحه اول
    
    for page in range(1, max_pages + 1):
        url = base_url.format(number=page)
        print(f"   🔍 در حال اسکرپ صفحه {page}...")
        
        try:
            response = rq.get(url, headers=common_headers, timeout=15)
            response.raise_for_status()
            
            results = parser(response.text, site_name)
            if results:
                all_projects.extend(results)
                print(Fore.GREEN + f"   ✅ استخراج {len(results)} پروژه از صفحه {page}")
            else:
                print(Fore.YELLOW + f"   ⚠️ هیچ پروژه‌ای در صفحه {page} یافت نشد")
            
            # تاخیر تصادفی بین درخواست‌ها
            delay = random.randint(3, 8)
            time.sleep(delay)
            
        except rq.exceptions.Timeout:
            print(Fore.RED + f"   ❌ خطا: تایم‌اوت در صفحه {page}")
            break
        except rq.exceptions.RequestException as e:
            print(Fore.RED + f"   ❌ خطا در درخواست صفحه {page}: {e}")
            break
        except Exception as e:
            print(Fore.RED + f"   ❌ خطای غیرمنتظره: {e}")
            break

# ذخیره نتایج
print(Fore.CYAN + "\n" + "=" * 50)
print(Fore.YELLOW + "💾 ذخیره نتایج...")

if all_projects:
    save_to_json(all_projects, "projects.json")
    save_to_excel(all_projects, "projects.xlsx")
    
    print(Fore.GREEN + f"\n✅ اسکرپ با موفقیت انجام شد!")
    print(Fore.GREEN + f"📊 تعداد کل پروژه‌های استخراج شده: {len(all_projects)}")
    print(Fore.GREEN + f"📁 خروجی‌ها: projects.json , projects.xlsx")
    
    # نمایش چند نمونه
    print(Fore.CYAN + "\n📋 نمونه پروژه‌های استخراج شده:")
    for i, proj in enumerate(all_projects[:5], 1):
        print(f"   {i}. {proj['title'][:50]}... | تلفن: {', '.join(proj['phones'][:2])}")
else:
    print(Fore.RED + "❌ هیچ پروژه‌ای استخراج نشد. احتمالاً ساختار سایت تغییر کرده یا نیاز به بروزرسانی کلاس‌ها دارد.")

print(Fore.CYAN + "=" * 50)
print(Fore.YELLOW + "🏁 پایان اسکرپ")
