from langchain_community.document_loaders import PyPDFLoader

import os

file_path = "docs/2025년_2월_경제전망보고서(Indigo_Book).pdf"
print("Reading file from: ", file_path)

loader = PyPDFLoader(file_path)
print("Loader Created")

pages = []

print("Loading pages")
for page in loader.lazy_load():
    pages.append(page)
print("Pages loaded")

print(f"{pages[0].metadata}\n")
print(pages[0].page_content[:500])
