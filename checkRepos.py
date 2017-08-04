#!/usr/bin/env python3
#
# Copyright (C) Pelagicore AB 2017
# SPDX-License-Identifier: MPL-2.0
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests
import argparse
import json

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
         return repos_data


    try:
        # Entries should follow this pattern: {"name": "Misbehaving repo",
        #                                      "url":  "https://github.com/org/repo",
        #                                      "reasons": ["reason for being suspect" ...]}
        suspects = []
        for repo in repos_data:
            reasons = parseRepo(repo)
            if len(reasons) > 0:
                suspect = dict()
                suspect['name'] = repo['name']
                suspect['url']  = repo['url']
                suspect['reasons'] = reasons
                suspects.append(suspect)

        return suspects
    except:
        return {'message': "Something went wrong in the parsing. The most likely reason is that the API call" \
               " limit was reached, please try again later."}


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Scan a GitHub organization for repos without READMEs or CONTRIBUTION pages.')
    parser.add_argument('organization', type=str, help='The GitHub organization to scan')
    parser.add_argument('--file', type=str, default=None, help='Specify name of file to write the output to.' \
            'If not specified, the output will be written to stdout.')
    parser.add_argument('--pretty', action='store_true', help='Pretty print the output.')

    args = parser.parse_args()
    result = parseOrganization(args.organization)

    # Setup pretty print
    if args.pretty:
        indent = 4
    else:
        indent = None

    # JSON formatting
    result = json.dumps(result, indent=indent)

    # Output result
    if args.file is None:
        print(result)
    else:
        with open(args.file, "w") as f:
            f.write("{}\n".format(result))
