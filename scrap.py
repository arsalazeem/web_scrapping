import pdb
import re
from bs4 import BeautifulSoup
import requests


def normalize_review(text):
    normal = text
    normal = normal.replace('<p class="text-body-2">', "")
    normal = normal.replace('</p>', "")
    return normal


def fetch_html_structure(url):
    header = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=header)
    return response


def normalize_text_sentence(org_text):
    normalize_text = org_text
    normalize_text = normalize_text.replace("</", "")
    normalize_text = normalize_text.replace('&amp;', '&')
    normalize_text = normalize_text.replace("&#x27;", "'")
    return normalize_text


def return_text(original_source, current_index, tag, slice_limit=1200):
    create_slice = slice(current_index, current_index + slice_limit)
    narrow_text = original_source[create_slice]
    narrow_text = narrow_text.split(tag)
    normalize_text = normalize_text_sentence(narrow_text[1])
    return normalize_text
    # for i in range(current_index,current_index+slice_limit+1):
    #     create_slice=slice(i,i+end_tag_lenth)
    #     print(create_slice)
    #     print(original_source[create_slice])


def search_from_index(currentindex, original_source, class_count, tag, data_type="_number"):
    if data_type == "_number":
        currentindex = currentindex + class_count
        end_index = currentindex + 8
        create_slice = slice(currentindex, end_index)
        fetch_value = original_source[create_slice]
        fetch_value = re.findall(r"\d+\.\d+", fetch_value)
        return fetch_value[0]
    elif data_type == "int":
        currentindex = currentindex + class_count
        end_index = currentindex + 8
        create_slice = slice(currentindex, end_index)
        fetch_value = original_source[create_slice]
        fetch_value = re.findall("[0-9]+", fetch_value)
        return fetch_value[0]

    elif data_type == "text":
        return return_text(original_source, currentindex, tag, 700)
    else:
        pass


def get_value(page, search, tag=None, data_type="_number"):
    get_index = page.index(search)
    return search_from_index(get_index, page, len(search), tag, data_type)


def get_reviews_using_soup(response):
    reviews_list = []
    soup = BeautifulSoup(response.content, 'lxml')
    the_latest = soup.find(class_="review-list")
    mydivs = soup.find_all("p", {"class": "text-body-2"})
    if len(mydivs) < 1:
        return reviews_list
    for i in range(0, len(mydivs) - 1):
        if i % 2 == 0:
            review_text = str(mydivs[i])
            review_text = normalize_review(review_text)
            reviews_list.append(review_text)

    return reviews_list


def fetch_profile_data(url):
    search_string = {
        "total_reviews": 'data-user-ratings-count',
        "rating": 'data-user-rating',
        "about_me": '<div class="description">'
    }
    response = fetch_html_structure(url)
    webpage_text = response.text
    # pdb.set_trace()
    total_reviews = get_value(webpage_text, search_string.get("total_reviews"), "None", "int")
    about_me = get_value(webpage_text, search_string.get("about_me"), "p>", "text")
    total_rating = get_value(webpage_text, search_string.get("rating"))
    reviews_list = get_reviews_using_soup(response)
    return {"total_reviews_recieved": total_reviews, "total_projects_completed": total_reviews,
            "total_rating": total_rating, "about_me": about_me, "reviews_list": reviews_list}

    # for i in range(0,100):
    #     try:
    #         reviews_list = the_latest.findAll("p")[i].text
    #         print(reviews_list)
    #     except Exception as e:
    #         pass


def handler_name(event, context):
    url=event["url"]
    response=fetch_profile_data(url)
    return response


if __name__ == '__main__':
    result = fetch_profile_data("https://www.fiverr.com/rankterpriseuk")
    print(result)
