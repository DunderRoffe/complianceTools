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


def verifyRepo(repo, rules):
    """
    Verifies a given GitHub repository against compliance rules
    and returns any violations found as a list.
    """
    contents_response = requests.get(repo['contents_url'][:-7])
    contents_data = contents_response.json()

    files_in_content = [content['name'] for content in contents_data]
    reasons = []

    for rule in rules:
        reason = rule(repo, files_in_content)
        if reason is not None:
            reasons.append(reason)

    return reasons


def verifyOrganization(organization, rules):
    """
    Verifies that all accessible repositories of a given GitHub organization
    adheres to a set of rules.

    If the parsing was successfull the output will be formatted as follows:
    [
      {
        "name":    "Misbehaving repo",
        "url":     "https://github.com/org/repo",
        "reasons": [ "Reason 1", "Reason 2" ]
      }
    ]

    However, if an error occur while parsing the repository a dict containing
    the error message will be returned instead.
    """
    repos_response = requests.get("https://api.github.com/orgs/{}/repos".format(organization))
    repos_data = repos_response.json()

    # Due to limitations in the Github API this might not work
    if repos_response.status_code == 403:
         return repos_data


    try:
        suspects = []
        for repo in repos_data:
            reasons = verifyRepo(repo, rules)
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


def make_required_file_rule(file_name):
    """
    Returns a rule (function that takes two arguments: repo and files_in_repo)
    which is used to verify if a given file_name is found in a repository
    """
    return lambda _, files: "No file named {} found".format(file_name) if file_name not in files else None


def make_rules():
    """
    Return a list of rules
    """
    rules = []

    required_files = ["README.md", "LICENSE", "Contributing.md"]
    required_file_rules = [make_required_file_rule(file_name) for file_name in required_files]
    rules += required_file_rules

    no_forks_rule = lambda repo, _: "Is a fork" if repo['fork'] else None
    rules.append(no_forks_rule)
    return rules


def parseArguments():
    parser = argparse.ArgumentParser(description='Scan a GitHub organization for repos without READMEs or CONTRIBUTION pages.')
    parser.add_argument('organization', type=str, help='The GitHub organization to scan')
    parser.add_argument('--file', type=str, default=None, help='Specify name of file to write the output to.' \
            'If not specified, the output will be written to stdout.')
    parser.add_argument('--pretty', action='store_true', help='Pretty print the output.')

    args = parser.parse_args()
    return args.organization, args.pretty, args.file


def formatJSON(to_format, pretty):
    if pretty:
        indent = 4
    else:
        indent = None
    return json.dumps(to_format, indent=indent)


def output(to_output, file_name):
    if file_name is None:
        print(to_output)
    else:
        with open(file_name, "w") as f:
            f.write("{}\n".format(to_output))


if __name__=="__main__":
    organization, pretty, file_name = parseArguments()

    rules = make_rules
    violations = verifyOrganization(organization, rules)

    violations_json = formatJSON(violations, pretty)
    output(violations_json, file_name)
