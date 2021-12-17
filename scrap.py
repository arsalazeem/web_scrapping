import pdb
import re
from bs4 import BeautifulSoup
import requests
import json
import lxml


def _fetch_html_structure(url):
    header = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=header)
    return response


def _get_reviews_using_soup(response):
    reviews_list = []
    soup = BeautifulSoup(response.content, 'lxml')
    the_latest = soup.find(class_="review-list")
    p_tags_list = soup.find_all("p", {"class": "text-body-2"})
    if len(p_tags_list) < 1:
        return reviews_list
    for i in range(0, len(p_tags_list) - 1):
        if i % 2 == 0:  # showing every even p tag because p at odd tags contains information text
            review_text = str(p_tags_list[i].text)
            # review_text = _normalize_review(review_text)
            reviews_list.append(review_text)

    return reviews_list


def _get_data_using_soup(response, class_name):
    soup = BeautifulSoup(response.content, 'lxml')
    text_data = soup.find(class_=class_name).text
    return text_data


def fetch_profile_data(url):
    classes = {
        "average_review": 'rating-score rating-num',
        "total_reviews": 'ratings-count rating-count',
        "about_me": 'description',
    }
    response = _fetch_html_structure(url)
    average_review = _get_data_using_soup(response, classes.get("average_review"))
    total_reviews = _get_data_using_soup(response, classes.get("total_reviews"))
    about = _get_data_using_soup(response, classes.get("about_me"))
    reviews_list = _get_reviews_using_soup(response)
    total_reviews = total_reviews.replace("(", "")
    total_reviews = total_reviews.replace(")", "")
    total_reviews = total_reviews.replace(" reviews", "")
    about = about[11:]
    scrapped_data = {
        "total_projects_completed": total_reviews,
        "average_review": average_review,
        "total_reviews_count": total_reviews,
        "about_me": about,
        "reviews_list": reviews_list

    }
    return scrapped_data


def handler_name(event, context):
    url = event["url"]
    response = fetch_profile_data(url)
    return response


if __name__ == '__main__':
    result = fetch_profile_data("https://www.fiverr.com/rankterpriseuk")
    print(result)
