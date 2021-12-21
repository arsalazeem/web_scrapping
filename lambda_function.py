import json
import pdb
import re
import urllib

from bs4 import BeautifulSoup
import requests
import json
import validators


def _fetch_html_structure(url):
    header = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=header)
    return response


def _get_reviews_using_soup(response):
    reviews_list = []
    soup = BeautifulSoup(response.content, "html.parser")
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
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        text_data = soup.find(class_=class_name).text
        return str(text_data)
    except Exception as e:
        return "Not found"


def fetch_profile(url):
    try:
        classes = {
            "average_review": 'rating-score rating-num',
            "total_reviews": 'ratings-count rating-count',
            "exact_review": "total-rating header-total-rating",
            "about_me": 'description',
        }
        response = _fetch_html_structure(url)
        average_review = _get_data_using_soup(response, classes.get("average_review"))
        total_reviews = _get_data_using_soup(response, classes.get("total_reviews"))
        if "k+" in total_reviews:
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(response, classes.get("exact_review"))
        about = _get_data_using_soup(response, classes.get("about_me"))
        reviews_list = _get_reviews_using_soup(response)
        total_reviews = total_reviews.replace("(", "")
        total_reviews = total_reviews.replace(")", "")
        total_reviews = total_reviews.replace(" reviews", "")
        about = about[11:]
        try:
            total_reviews = total_reviews.replace(',', "")
            total_reviews = float(total_reviews)
            average_review = float(average_review)
        except Exception as error:
            print(error)
        scrapped_data = {
            "total_projects_completed": total_reviews,
            "average_review": average_review,
            "total_reviews_count": total_reviews,
            "about_me": about,
            "reviews_list": reviews_list
        }

        return {"success": 1, "data": scrapped_data, "message": "User data scrapped successfully"}
    except Exception as error:
        error_string = str(error)
        return {"success": 0, "data": {}, "message": error_string}


def lambda_handler(event, context):
    url_body = json.loads(event['body'])
    get_url = url_body["url"]
    url = get_url
    try:
        classes = {
            "average_review": 'rating-score rating-num',
            "total_reviews": 'ratings-count rating-count',
            "exact_review": "total-rating header-total-rating",
            "about_me": 'description',
        }
        response = _fetch_html_structure(url)
        average_review = _get_data_using_soup(response, classes.get("average_review"))
        total_reviews = _get_data_using_soup(response, classes.get("total_reviews"))
        if "k+" in total_reviews:
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(response, classes.get("exact_review"))
        about = _get_data_using_soup(response, classes.get("about_me"))
        reviews_list = _get_reviews_using_soup(response)
        total_reviews = total_reviews.replace("(", "")
        total_reviews = total_reviews.replace(")", "")
        total_reviews = total_reviews.replace(" reviews", "")
        about = about[11:]
        try:
            total_reviews = total_reviews.replace(',', "")
            total_reviews = float(total_reviews)
            average_review = float(average_review)
        except Exception as error:
            print(error)
        scrapped_data = {
            "total_projects_completed": total_reviews,
            "average_review": average_review,
            "total_reviews_count": total_reviews,
            "about_me": about,
            "reviews_list": reviews_list
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "data": {"success": 1, "user_profile": scrapped_data, "message": "User data scrapped successfully"}
            })
        }
    except Exception as error:
        error_string = str(error)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "data": {"success": 0, "user_profile": {}, "message": error_string}
            })
        }
