#!/usr/bin/env python3

import requests
import argparse

def parseRepo(repo):
    """
    Scans a given repository and returns reasons for why it might need looking into
    """
    contents_response = requests.get(repo['contents_url'][:-7])
    contents_data = contents_response.json()

    files_in_content = [content['name'] for content in contents_data]
    reasons = []

    required_files = ["README.md", "LICENSE", "Contributing.md"]
    for file_name in required_files:
        if file_name not in files_in_content:
            reasons.append("No file named {} found".format(file_name))

    if repo['fork']:
        reasons.append("Is a fork")

    return reasons


def parseOrganization(organization):
    repos_response = requests.get("https://api.github.com/orgs/{}/repos".format(organization))
    repos_data = repos_response.json()

    # Due to limitations in the Github API this might not work
    if repos_response.status_code == 403:
         return "{}\n{}\n".format(repos_data['message'], repos_data['documentation_url']) 


    try:
        # entries should follow this pattern: ("full_name", "url", "reason for being suspect")
        suspects = []
        for repo in repos_data:
            reasons = parseRepo(repo)
            if len(reasons) > 0:
                suspects.append((repo['full_name'], repo['url'], reasons))

        return suspects
    except:
        return "Something went wrong in the parsing. The most likely reason is that the API call" \
               " limit was reached, please try again later."


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Scan a GitHub organization for repos without READMEs or CONTRIBUTION pages.')
    parser.add_argument('organization', type=str, help='The GitHub organization to scan')

    args = parser.parse_args()
    print(parseOrganization(args.organization))
