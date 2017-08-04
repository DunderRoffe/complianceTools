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
