# Issues Found in premium_calculator.py

| Issue | Type | Line(s) | Description | Fix Approach |
| ------- | ------ | --------- | ------------- | -------------- |
| Unsafe tar extraction | Security (Bandit B202, HIGH) | 64 | `tar.extractall()` without validating members — path traversal / Zip Slip attack | Validate each member's path before extracting |
| Unverified SSL context | Security (Bandit B323, MEDIUM) | 58 | `ssl._create_unverified_context()` disables HTTPS certificate validation | Use `ssl.create_default_context()` |
| Hardcoded 0.0.0.0 bind | Security (Bandit B104, MEDIUM) | 12 | `HOST = "0.0.0.0"` binds to all network interfaces | Use `"127.0.0.1"` or make configurable |
| Insecure temp file | Security (Bandit B108, MEDIUM) | 14 | Hardcoded `/tmp/` directory | Use `tempfile.gettempdir()` |
| Unvalidated XML parsing | Security (Bandit B314, MEDIUM) | 48 | `xml.etree.ElementTree.fromstring` vulnerable to XML bombs/XXE | Use `defusedxml.ElementTree` |
| Mutable default argument | Bug (Pylint W0102) | 17 | `discounts=[]` shared across calls and mutated with `append(500)` — corrupts later calls | Default to `None`, initialize inside; remove `append` |
| Bare except | Style/Bug (Flake8 E722) | 53 | `except:` swallows all exceptions silently | Catch specific exceptions |
| Hardcoded password | Security (Bandit B105) | 13 | `UNDERWRITER_TOKEN` hardcoded in source | Load from environment variable |
| Weak random for IDs | Security (Bandit B311) | 37 | `random.randint` not cryptographically secure | Use `secrets.randbelow` |
| Missing docstrings | Style (Pylint C0114/C0116) | 1, all functions | No module or function docstrings | Add docstrings |
| camelCase names | Style (Pylint C0103) | many | Function names not snake_case | Rename to snake_case |
| Line too long | Style (Flake8 E501) | 14, 17, 52, 87, 101 | Lines exceed 79 chars | Wrap lines |
| Missing blank lines | Style (Flake8 E302) | many | Need 2 blank lines between functions | Add blank lines |
| Age off-by-one | Bug (not flagged by tools) | 30–34 | `ageFromDob` ignores whether birthday passed this year | Compare month/day |
| Non-smoker treated as smoker | Bug (not flagged by tools) | 27 in main | `"no"` is truthy, applies smoker surcharge | Pass `False` or coerce |
| Negative premium possible | Bug (not flagged by tools) | 17–24 | Stacked discounts can push premium below zero | Add `max(premium, 0)` |
| Feb 29 crash | Bug (not flagged by tools) | 79–81 | `date.replace(year+1)` fails on Feb 29 | Use try/except |

*(This is more than 4 rows — great. The lab says minimum 4, but documenting everything helps your grade and the "fix ALL issues" bonus.)*
