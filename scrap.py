import pdb
import re
from bs4 import BeautifulSoup
import requests
import json


def _normalize_review(text):
    normal = text
    normal = normal.replace('<p class="text-body-2">', "")
    normal = normal.replace('</p>', "")
    return normal


def _fetch_html_structure(url):
    header = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=header)
    return response


def _normalize_text_sentence(org_text):
    normalize_text = org_text
    normalize_text = normalize_text.replace("</", "")
    normalize_text = normalize_text.replace('&amp;', '&')
    normalize_text = normalize_text.replace("&#x27;", "'")
    return normalize_text


def _return_text(original_source, current_index, tag, slice_limit=1200):
    create_slice = slice(current_index, current_index + slice_limit)
    narrow_text = original_source[create_slice]
    narrow_text = narrow_text.split(tag)
    normalize_text = _normalize_text_sentence(narrow_text[1])
    return normalize_text
    # for i in range(current_index,current_index+slice_limit+1):
    #     create_slice=slice(i,i+end_tag_lenth)
    #     print(create_slice)
    #     print(original_source[create_slice])


def _search_from_index(currentindex, original_source, class_count, tag, data_type="_number"):
    if data_type == "_number":
        currentindex = currentindex + class_count
        end_index = currentindex + 8
        create_slice = slice(currentindex, end_index)
        fetch_value = original_source[create_slice]
        try:
            fetch_value = re.findall(r"\d+\.\d+", fetch_value)
            return fetch_value[0]
        except Exception as e:
            fetch_value = re.findall("[0-9]+", fetch_value)
            return fetch_value[0]

    elif data_type == "int":
        currentindex = currentindex + class_count
        end_index = currentindex + 8
        create_slice = slice(currentindex, end_index)
        fetch_value = original_source[create_slice]
        fetch_value = re.findall("[0-9]+", fetch_value)
        return fetch_value[0]

    elif data_type == "text":
        return _return_text(original_source, currentindex, tag, 700)
    else:  # this code is unreachable
        pass


def _get_value(page, search, tag=None, data_type="_number"):
    get_index = page.index(search)
    return _search_from_index(get_index, page, len(search), tag, data_type)


def _get_reviews_using_soup(response):
    reviews_list = []
    soup = BeautifulSoup(response.content, 'lxml')
    the_latest = soup.find(class_="review-list")
    p_tags_list = soup.find_all("p", {"class": "text-body-2"})
    if len(p_tags_list) < 1:
        return reviews_list
    for i in range(0, len(p_tags_list) - 1):
        if i % 2 == 0:  # showing every even p tag because p at odd tags contains information text
            review_text = str(p_tags_list[i])
            review_text = _normalize_review(review_text)
            reviews_list.append(review_text)

    return reviews_list


def fetch_profile_data(url):
    search_string = {
        "total_reviews": 'data-user-ratings-count',
        "rating": 'data-user-rating',
        "about_me": '<div class="description">'
    }
    response = _fetch_html_structure(url)
    webpage_text = response.text
    # pdb.set_trace()
    total_reviews = _get_value(webpage_text, search_string.get("total_reviews"), "None", "int")
    about_me = _get_value(webpage_text, search_string.get("about_me"), "p>", "text")
    total_rating = _get_value(webpage_text, search_string.get("rating"))
    reviews_list = _get_reviews_using_soup(response)
    scrapping_data = {"total_reviews_recieved": total_reviews, "total_projects_completed": total_reviews,
                      "total_rating": total_rating, "about_me": about_me, "reviews_list": reviews_list}
    scrapping_data = json.dumps(scrapping_data)  # conveting python dictonary into Json
    return scrapping_data

    # for i in range(0,100):
    #     try:
    #         reviews_list = the_latest.findAll("p")[i].text
    #         print(reviews_list)
    #     except Exception as e:
    #         pass


def handler_name(event, context):
    url = event["url"]
    response = fetch_profile_data(url)
    return response


if __name__ == '__main__':
    result = fetch_profile_data("https://www.fiverr.com/rankterpriseuk")
    print(result)
