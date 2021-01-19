import csv
from time import sleep

import requests
query = "Maastricht"

def auth():
    print("Enter Twitter API Bearer token:")
    return input()


def create_tweets_url(next_token):
    max_results = "100"
    expansions = "author_id"
    tweet_fields = "public_metrics,created_at"
    if next_token is None:
        return "https://api.twitter.com/2/tweets/search/recent?max_results={}&tweet.fields={}&expansions={}&query={}".format(
            max_results,
            tweet_fields,
            expansions,
            query
        )
    else:
        return "https://api.twitter.com/2/tweets/search/recent?max_results={}&next_token={}&tweet.fields={}&expansions={}&query={}".format(
            max_results,
            next_token,
            tweet_fields,
            expansions,
            query
        )


def create_user_url(user_id):
    user_fields = "username"
    return "https://api.twitter.com/2/users/{}?user.fields={}".format(
        user_id,
        user_fields
    )


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    json_response = response.json()
    if "meta" in json_response:
        if "next_token" in json_response["meta"]:
            return response.json(), json_response["meta"]["next_token"]
    return response.json(), None


def main():
    bearer_token = auth()
    headers = create_headers(bearer_token)
    tweet_data = []
    user_data = []
    next_token = None
    has_next = True
    while has_next:
        tweet_response = connect_to_endpoint(create_tweets_url(next_token), headers)
        print(tweet_response[0]["meta"]["result_count"])
        for tweet in tweet_response[0]["data"]:
            tweet_data.append({"id": tweet["id"], "tekst": tweet["text"], "accountnaam": tweet['author_id'], "timestamp": tweet["created_at"], "STAD_naam": query})
        for user in tweet_response[0]["includes"]["users"]:
            for tweet in tweet_data:
                if tweet["accountnaam"] == user["id"]:
                    tweet["accountnaam"] = user["username"]
        next_token = tweet_response[1]
        if next_token is None:
            has_next = False
        print("Waiting for ratelimit...")
        sleep(10)
    with open('output.csv', mode='w', newline='', encoding='utf-8') as output:
        fieldnames = ['id', 'tekst', 'accountnaam', 'timestamp', 'STAD_naam']
        output_writer = csv.DictWriter(output, fieldnames=fieldnames)
        output_writer.writeheader()
        for row in tweet_data:
            output_writer.writerow(row)
            print(row)


if __name__ == "__main__":
    main()
