import time
import math
import csv
import json
from bs4 import BeautifulSoup
from time import sleep
import requests
from random import randint
from html.parser import HTMLParser

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


class SearchEngine:
    """
    Part of the code provided by instructor, modified a little bit to dynamically search different page.
    """
    @staticmethod
    def search(query, sleep=True, page=1):
        if sleep:  # Prevents loading too many pages too soon
            time.sleep(randint(10, 100))
        temp_url = '+'.join(query.split())  # for adding + between words for the query
        url = 'https://www.ask.com/web?q=' + temp_url
        if page > 1:
            url += '&page='
            url += str(page)
        soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text, "html.parser")
        new_results = SearchEngine.scrape_search_result(soup)
        return new_results

    @staticmethod
    def scrape_search_result(soup):
        raw_results = soup.find_all("div", attrs={"class":"PartialSearchResults-item-title"})
        results = []
        # print(raw_results)
        # implement a check to get only 10 results and also check that URLs must not be duplicated
        check_set = set()
        for result in raw_results:
            link = result.find('a').get('href')
            check_str = link.replace("http://", "")
            check_str = check_str.replace("https://", "")
            check_str = check_str.replace("www.", "")
            check_str = check_str.lower()
            if check_str[-1] == "/":
                check_str = check_str[:-1]
            if check_str not in check_set:
                check_set.add(check_str)
                results.append(link)
        return results
#############Driver code############
# print(len(SearchEngine.search("Apple", sleep=False)))
####################################


def read_query_file():
    """
    Read the input query text file and return the prepared query for url.
    :return: list of string.
    """
    f = open("100QueriesSet3.txt", "r")
    q_list = []
    for q in f:
        temp = q.replace(" ?\n", "")
        temp = temp.replace(" ?", "")
        # temp = temp.replace(" ", "+")
        q_list.append(temp)
    f.close()
    return q_list


def str_process(url):
    """
    process the url to return a normal one.
    :param url: a string represent url.
    :return: a normalized url.
    """
    check_str = url.replace("http://", "")
    check_str = check_str.replace("https://", "")
    check_str = check_str.replace("www.", "")
    check_str = check_str.lower()
    if check_str[-1] == "/":
        check_str = check_str[:-1]
    return check_str


def compare(query):
    """
    Read 2 json file and compare their result.
    :param query: type list(of string), the entry of dict.
    :return:
    """
    js_file1 = open("Google_Result3.json")
    js_file2 = open("my_result_test1.json")
    data1 = json.load(js_file1)
    data2 = json.load(js_file2)
    overlap_list = []
    overlap_per_list = []
    rho_list = []
    # compare process.
    for q in query:
        google_list = data1[q]
        my_list = data2[q]
        overlap_count = 0
        dist = []
        for i in range(len(my_list)):
            my_str = str_process(my_list[i])
            for j in range(len(google_list)):
                google_str = str_process(google_list[j])
                if my_str == google_str:
                    dist.append((j - i) ** 2)
                    overlap_count += 1
        if len(dist) > 1:
            rho = 1 - 6 * (sum(dist) / (len(dist) * (len(dist) ** 2 - 1)))
        elif len(dist) == 1:
            if dist[0] == 0:
                rho = 1
            else:
                rho = 0
        else:
            rho = 0
        overlap_list.append(overlap_count)
        overlap_per_list.append(overlap_count * 10)
        rho_list.append(rho)
    with open('hw1.csv', 'w', newline='') as w_file:
        fieldnames = ['Queries', 'Number of Overlapping Results', 'Percent Overlap', 'Spearman Coefficient']
        writer = csv.DictWriter(w_file, fieldnames=fieldnames)
        writer.writeheader()
        rowdicts = []
        for i in range(len(query)):
            rowdict = dict()
            rowdict['Queries'] = 'Query ' + str(i + 1)
            rowdict['Number of Overlapping Results'] = overlap_list[i]
            rowdict['Percent Overlap'] = overlap_per_list[i]
            rowdict['Spearman Coefficient'] = rho_list[i]
            rowdicts.append(rowdict)
        writer.writerows(rowdicts=rowdicts)
        avgdict = dict()
        avgdict['Queries'] = 'Averages'
        avgdict['Number of Overlapping Results'] = sum(overlap_list) / len(overlap_list)
        avgdict['Percent Overlap'] = sum(overlap_per_list) / len(overlap_per_list)
        avgdict['Spearman Coefficient'] = sum(rho_list) / len(rho_list)
        writer.writerow(rowdict=avgdict)


queries = read_query_file()
query_result = dict()
compare(queries)

'''
for i in range(len(queries)):
    page_count = 1
    print("Currently searching " + str(i) + "th query")
    result = SearchEngine.search(queries[i], sleep=True)
    if len(result) < 10:
        page_count += 1
        print("Continue search 2nd page of " + str(i) + "th query")
        result.extend(SearchEngine.search(queries[i], sleep=True, page=page_count))
    if len(result) > 10:
        result = result[:10]
    query_result[queries[i]] = result

with open("my_result.json", "w") as outfile:
    json.dump(query_result, outfile, indent=4)
'''
# Did not maintain a set for checking combination,
# which means result 10 may be the same as what appears in first 9 results.
