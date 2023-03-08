import asyncio
import re
import time

import aiohttp
from bs4 import BeautifulSoup
from translate import translate

async def translate_text(text, src, dest, session):
    try:
        response = await translate(text, src=src, dest=dest, session=session)
        return response.translated
    except Exception as exception:
        print(f"Element : {text!r}\n{exception}\n\n")
        return ""

async def translate_html_file(file_path: str, src: str, dest: str) -> None:
    with open(file_path, "r", encoding="UTF-8") as fp:
        data = fp.read()

    soup = BeautifulSoup(data, "html.parser")

    async with aiohttp.ClientSession() as session:
        elements_to_translate = []
        for element in soup.find_all(string=True):
            if element.parent.name not in ('script', 'style',):
                text = re.sub(r"\n", "", str(element)).strip()
                if text:
                    elements_to_translate.append((element, text))

        batch_size = 15
        for i in range(0, len(elements_to_translate), batch_size):
            batch_elements = elements_to_translate[i:i+batch_size]
            batch_text = [element[1] for element in batch_elements]
            batch_translated = await asyncio.gather(*[translate_text(text, src, dest, session) for text in batch_text])
            for j, element in enumerate(batch_elements):
                translated_text = batch_translated[j]
                if translated_text:
                    print(f"Translated {element[1]!r} to {translated_text!r}")
                    element[0].replace_with(translated_text)
                    time.sleep(1.0)

    with open(f"{file_path[:-5]}_translated.html", "w", encoding="UTF-8") as fp:
        fp.write(str(soup))

async def main() -> None:
    """[Function]"""
    
    files_to_translate = [
        
        "D:/jupyter/newtry/www.classcentral.com/report/cs50-free-certificate/index.html",
        "D:/jupyter/newtry/www.classcentral.com/report/open-university-insiders-perspective/index.html",
        "D:/jupyter/newtry/www.classcentral.com/about/privacy-policy.html",
        "D:/jupyter/newtry/www.classcentral.com/about/careers.html",
        "D:/jupyter/newtry/www.classcentral.com/report/free-google-certifications/index.html",
        "D:/jupyter/newtry/www.classcentral.com/report/writing-free-online-courses/index.html",
        "D:/jupyter/newtry/www.classcentral.com/provider/udacity.html",
        "D:/jupyter/newtry/www.classcentral.com/subject/cybersecurity.html",
        "D:/jupyter/newtry/www.classcentral.com/subject/psychology.html",
        "D:/jupyter/newtry/www.classcentral.com/institution/microsoft.html",
        "D:/jupyter/newtry/www.classcentral.com/institution/smithsonian.html"
        

    ]

    tasks = []
    for file_path in files_to_translate:
        task = asyncio.create_task(translate_html_file(file_path, "en", "hi"))
        tasks.append(task)

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
