# complianceTools
A set of tools used to ease the management process of Compliance Offices

## CheckRepos
CheckRepos verifies that all repositories in a GitHub organization fulfills all
requirements. Currently these requirements are hard coded in to the program.

### How to use
```bash
./complianceTools --help
```

### Output format
```json
[{
    "name": "Misbehaving repo",
    "url": "https://github.com/org/repo",
    "reasons": ["Reason 1", "Reason 2" ... ]
}]
```

# License
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
