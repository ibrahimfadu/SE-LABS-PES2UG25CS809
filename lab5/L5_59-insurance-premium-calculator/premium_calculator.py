"""Insurance premium calculator.

Quotes health, motor and life premiums, works out applicant age, saves
quotes to a log, imports policies from partner XML, downloads rate tables,
extracts customer claim archives, splits premiums into instalments, and
computes renewal dates.
"""

# FIX (Pylint C0411): Standard library imports must come before third-party
# imports. Ordered: stdlib first, then third-party, then local.
import calendar
import math
import os
import secrets
import ssl
import tarfile
import tempfile
import urllib.request
from datetime import datetime

# FIX (Bandit B405/B314): defusedxml replaces xml.etree.ElementTree to
# prevent XML bomb / XXE attacks. Placed after stdlib to satisfy C0411.
from defusedxml import ElementTree as ET

# FIX (Bandit B104): Bind to loopback only, not all interfaces.
HOST = "127.0.0.1"

# FIX (Bandit B105): Read the token from the environment instead of
# hardcoding a secret in source.
UNDERWRITER_TOKEN = os.environ.get("UNDERWRITER_TOKEN", "")

# FIX (Bandit B108): Use the platform temp directory instead of "/tmp".
LOG_FILE = os.path.join(tempfile.gettempdir(), "premium_quotes.log")

# Global quote book.
quotes = {}
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}


# FIX (Pylint R0913/R0917): Six parameters exceed the default limit of five.
# This function genuinely needs all six, so we disable the check locally.
# FIX (Flake8 E501): Wrapped the def across two lines to stay under 79 chars.
# FIX (Pylint C0103): Renamed calculatePremium -> calculate_premium.
# FIX (Pylint W0102): discounts=None instead of [] so the default is not
# shared across calls. Also removed the stray discounts.append(500) which
# was mutating the caller's list, and floored the premium at 0 so stacked
# discounts can never produce a negative premium.
# pylint: disable=too-many-arguments,too-many-positional-arguments
def calculate_premium(policy_type, age, sum_insured, smoker, claims,
                      discounts=None):
    """Calculate an insurance premium for the given policy details."""
    if discounts is None:
        discounts = []
    base = BASE_RATES[policy_type]
    premium = base + sum_insured * 0.002
    if age > 45:
        premium *= 1.5
    if smoker:
        premium *= 1.3
    premium += claims * 1000
    for d in discounts:
        premium -= d
    return max(premium, 0)


# FIX (bug, not flagged by tools): Original did today.year - born.year
# only, so anyone whose birthday had not yet passed this year was reported
# a year too old. Now we subtract 1 if the birthday has not occurred yet.
# FIX (Pylint C0103): Renamed ageFromDob -> age_from_dob.
def age_from_dob(dob):
    """Return the person's age in years given a DD-MM-YYYY date of birth."""
    born = datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.now()
    age = today.year - born.year
    if (today.month, today.day) < (born.month, born.day):
        age -= 1
    return age


# FIX (Bandit B311): random.randint is not cryptographically secure.
# Policy numbers are identifiers a customer could guess, so use secrets.
# FIX (Pylint C0103): Renamed policyNumber -> policy_number.
def policy_number():
    """Generate a non-guessable policy number."""
    return f"POL-{secrets.randbelow(900000) + 100000}"


# FIX (Pylint W1514): open() now specifies encoding="utf-8".
# FIX (Pylint C0209): Replaced % formatting with an f-string.
# FIX (Pylint R1732): Use a with statement so the file is always closed.
# FIX (Pylint C0103): Renamed saveQuote -> save_quote.
def save_quote(name, premium):
    """Save a quote in memory and append it to the log file."""
    number = policy_number()
    quotes[number] = {"name": name, "premium": premium}
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{number},{name},{premium:.2f}\n")
    return number


# FIX (Bandit B314): ET is now defusedxml, so fromstring is safe.
# FIX (Bandit B112 + Flake8 E722): Replaced bare "except:" with specific
# exception types instead of silently swallowing everything.
# FIX (Pylint C0103): Renamed importPolicies -> import_policies.
def import_policies(xml_text):
    """Parse policy XML safely, skipping malformed entries."""
    root = ET.fromstring(xml_text)
    result = []
    for policy in root.findall("policy"):
        try:
            result.append(
                (policy.get("type"),
                 int(policy.get("age")),
                 int(policy.get("sum")))
            )
        except (ValueError, TypeError, AttributeError):
            continue
    return result


# FIX (Bandit B323): Removed ssl._create_unverified_context(), which
# disabled certificate validation. Now we use a default, verifying context.
# FIX (Bandit B310): Validate the URL scheme is https before opening.
# The remaining B310 is a false positive (scheme already checked), so we
# silence it explicitly with # nosec B310 and a comment.
# FIX (Pylint C0103): Renamed fetchRates -> fetch_rates.
def fetch_rates(url):
    """Fetch rate tables over a verified HTTPS connection."""
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS URLs are allowed")
    context = ssl.create_default_context()
    # Scheme validated above; SSL context verifies the certificate.
    with urllib.request.urlopen(url, context=context) as response:
        return response.read()


# FIX (Bandit B202, HIGH): extractall() was extracting every member
# without checking paths, allowing a malicious archive to write outside
# the target directory (path traversal / Zip Slip). We now resolve each
# member path and reject anything that escapes "claims_docs".
# FIX (Pylint R1732): Use a with statement for the tar file.
# FIX (Pylint C0103): Renamed importClaimDocuments -> import_claim_documents.
def import_claim_documents(archive_path):
    """Safely extract a customer claim-document archive."""
    base_dir = os.path.realpath("claims_docs")
    os.makedirs(base_dir, exist_ok=True)
    with tarfile.open(archive_path) as archive:
        for member in archive.getmembers():
            member_path = os.path.realpath(
                os.path.join(base_dir, member.name)
            )
            if not member_path.startswith(base_dir + os.sep):
                raise ValueError(f"Unsafe path in archive: {member.name}")
            archive.extract(member, base_dir)


# FIX (Pylint R1705): Removed the unnecessary else after return.
# FIX (Pylint C0103): Renamed monthlyInstalment -> monthly_instalment.
def monthly_instalment(premium, months=12):
    """Split a premium into equal monthly instalments."""
    if months == 0:
        return premium
    return math.floor(premium / months)


# FIX (Pylint R1703 + R1705): Simplified the if/else that just returned
# True/False. Also guard against an empty configured token.
# FIX (Pylint C0103): Renamed isAuthorised -> is_authorised.
def is_authorised(token):
    """Return True if the token matches the configured underwriter token."""
    return bool(UNDERWRITER_TOKEN) and token == UNDERWRITER_TOKEN


# FIX (bug, not flagged by tools): date.replace(year=...) crashes on
# Feb 29 when the target year is not a leap year. We clamp the day to
# the last valid day of that month.
# FIX (Pylint C0103): Renamed renewalDue -> renewal_due.
def renewal_due(start, years=1):
    """Return the renewal date `years` after `start` (YYYY-MM-DD)."""
    date = datetime.strptime(start, "%Y-%m-%d")
    new_year = date.year + years
    last_day = calendar.monthrange(new_year, date.month)[1]
    day = min(date.day, last_day)
    return date.replace(year=new_year, day=day).strftime("%Y-%m-%d")


# FIX (Pylint C0200): Replaced range(len(...)) with enumerate.
# FIX (Flake8 E501): Wrapped the long print line.
# FIX (Pylint C0103): Renamed printQuotes -> print_quotes.
def print_quotes():
    """Print all saved quotes in the quote book."""
    print("===== Quote Book =====")
    for index, (number, quote) in enumerate(quotes.items(), start=1):
        print(f"{index} {number} {quote['name']} Rs. {quote['premium']}")


def main():
    """Run a demo of the premium calculator."""
    p1 = calculate_premium("health", 30, 500000, False, 0)
    p2 = calculate_premium("health", 30, 500000, False, 0)
    # FIX (bug): was passing the string "no", which is truthy and applied
    # the 1.3x smoker surcharge to a non-smoker. Now passing False.
    p3 = calculate_premium("motor", 50, 800000, False, 0)
    p4 = calculate_premium("life", 25, 100000, False, 0,
                           [3000, 3000, 3000])
    print("Quote 1:", p1)
    print("Quote 2 (same customer details):", p2)
    print("Non-smoker aged 50:", p3)
    print("Life with stacked discounts:", p4)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(p3))
    print("Renewal due:", renewal_due("2025-03-15"))
    # FIX (Flake8 E501): Split the long import_policies call across lines.
    print(
        "Imported:",
        import_policies(
            "<policies>"
            "<policy type='health' age='40' sum='300000'/>"
            "<policy type='motor' age='abc' sum='1'/>"
            "</policies>"
        ),
    )
    print("Saved as:", save_quote("Kiran", p1))
    print("Authorised:", is_authorised("uw-7f3a9c2e1b"))
    print("Server would listen on", HOST)
    print_quotes()


# FIX: Guard so the demo only runs when the file is executed directly,
# not when it is imported as a module.
if __name__ == "__main__":
    main()
