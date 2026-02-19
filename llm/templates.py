"""
templates.py
SAR narrative templates and typology examples for RAG (ChromaDB).
These are loaded into ChromaDB so the LLM can retrieve relevant 
examples when generating new SARs.
"""

SAR_TEMPLATES = [
    {
        "id": "tmpl_001",
        "typology": "Money Laundering - Layering",
        "title": "Multiple Account Aggregation then International Transfer",
        "template": """
SUBJECT INFORMATION:
The subject, [CUSTOMER NAME], holds account [ACCOUNT NO] opened [DATE].
Customer profile: [OCCUPATION], with an average monthly credit of [AMOUNT].

TRANSACTION SUMMARY:
Between [START DATE] and [END DATE], the subject received a total of [AMOUNT]
across [COUNT] inbound transfers from [COUNT] distinct originating accounts.
Subsequently, [AMOUNT] was transferred via SWIFT to [DESTINATION COUNTRY].

SUSPICIOUS ACTIVITY DESCRIPTION:
The transaction pattern is inconsistent with the customer's known financial profile.
The aggregation of funds from numerous unrelated sources followed immediately by 
international wire transfer is indicative of layering — a key stage of money laundering
where illicit funds are moved through multiple accounts to obscure their origin.
No legitimate business purpose has been identified to explain this activity.

TYPOLOGY MATCH:
This activity is consistent with the FATF money laundering typology:
"Structuring and layering through multiple accounts with rapid international movement."

WHY THIS IS SUSPICIOUS:
1. Volume far exceeds customer's stated income or business activity
2. 47 unique senders with no apparent relationship to customer
3. No time gap between receipt and outward remittance (same-day layering)
4. Destination jurisdiction flagged as high-risk by FATF
5. No invoices, contracts, or business rationale provided
        """
    },
    {
        "id": "tmpl_002",
        "typology": "Structuring / Smurfing",
        "title": "Sub-threshold Cash Deposits to Avoid Reporting",
        "template": """
SUBJECT INFORMATION:
The subject, [CUSTOMER NAME], holds account [ACCOUNT NO].
Customer profile: [OCCUPATION], no prior suspicious activity flagged.

TRANSACTION SUMMARY:
Over [TIMEFRAME], the subject made [COUNT] cash deposits ranging from 
[MIN AMOUNT] to [MAX AMOUNT] each, totaling [TOTAL AMOUNT].
Each individual deposit fell below the ₹50,000 mandatory reporting threshold.

SUSPICIOUS ACTIVITY DESCRIPTION:
The consistent sub-threshold deposit pattern strongly suggests deliberate structuring
to evade Currency Transaction Report (CTR) requirements. The deposits show a clear
behavioral pattern: amounts are consistently just below the reporting threshold,
deposits occur at irregular intervals designed to avoid detection, and no salary
credit or business receipts account for the cash origin.

TYPOLOGY MATCH:
FATF Typology: "Structuring (Smurfing) — deliberate fragmentation of large cash
amounts into sub-threshold transactions to evade mandatory reporting obligations."

WHY THIS IS SUSPICIOUS:
1. All 9 deposits deliberately below ₹50,000 CTR threshold
2. No salary or business income to explain cash source
3. Pattern of deposits clustered within 72 hours
4. Immediate withdrawal after last deposit
5. Customer could not explain source of funds when contacted
        """
    },
    {
        "id": "tmpl_003",
        "typology": "Account Takeover Fraud",
        "title": "Unauthorized Access Followed by Rapid Fund Transfer",
        "template": """
SUBJECT INFORMATION:
The subject account [ACCOUNT NO] belongs to [CUSTOMER NAME].
Account holder profile: [AGE], [OCCUPATION], established customer since [YEAR].

TRANSACTION SUMMARY:
On [DATE], a login was detected from a new device (Device ID: [DEVICE]) and 
new geographic location ([CITY/COUNTRY]). Within [TIMEFRAME] of login, a 
transfer of [AMOUNT] was initiated to a newly added beneficiary [BENEFICIARY NAME],
a first-time recipient never previously transacted with.

SUSPICIOUS ACTIVITY DESCRIPTION:
The sequence of events — new device login, new geography, new beneficiary addition,
and immediate high-value transfer — is strongly consistent with an account takeover
attack. The legitimate account holder confirmed they did not initiate these transactions.
The beneficiary account has since been flagged as a mule account by our fraud team.

TYPOLOGY MATCH:
Fraud Typology: "Account Takeover (ATO) — unauthorized access to customer account
using stolen credentials, followed by rapid asset extraction to mule accounts."

WHY THIS IS SUSPICIOUS:
1. Login from unrecognized device and IP geolocation mismatch
2. New high-value beneficiary added and paid within same session
3. Transaction amount significantly exceeds customer's normal behavior
4. Customer confirmed non-authorization of transaction
5. Receiving account flagged in cross-bank fraud consortium database
        """
    },
    {
        "id": "tmpl_004",
        "typology": "Trade-Based Money Laundering",
        "title": "Over/Under Invoicing in Import-Export Transactions",
        "template": """
SUBJECT INFORMATION:
The subject, [COMPANY NAME], is a registered importer/exporter, 
account [ACCOUNT NO], in operation since [YEAR].

TRANSACTION SUMMARY:
The subject received [COUNT] inward remittances totaling [AMOUNT] from 
[COUNTRY] during [TIMEFRAME], purportedly for goods export.
Corresponding customs declarations show declared export value of [LOWER AMOUNT],
creating an unexplained discrepancy of [DIFFERENCE].

SUSPICIOUS ACTIVITY DESCRIPTION:
The significant gap between remittances received and declared customs values 
indicates potential over-invoicing — a trade-based money laundering technique
where the value of goods is deliberately misrepresented to transfer value
across borders and integrate illicit funds into the legitimate financial system.

TYPOLOGY MATCH:
FATF Typology: "Trade-Based Money Laundering (TBML) — manipulation of international
trade transactions to transfer value and launder illicit proceeds."

WHY THIS IS SUSPICIOUS:
1. ₹2.3 crore discrepancy between bank receipts and customs declarations
2. Counterparty located in FATF-listed jurisdiction
3. Goods description vague — "general merchandise" with no HS codes
4. No corresponding import of raw materials for stated manufacturing activity
5. Director of company has prior AML advisory from another bank
        """
    },
    {
        "id": "tmpl_005",
        "typology": "Terrorist Financing",
        "title": "Small Transfers to High-Risk Jurisdiction",
        "template": """
SUBJECT INFORMATION:
The subject, [CUSTOMER NAME], account [ACCOUNT NO], 
[OCCUPATION], customer since [YEAR].

TRANSACTION SUMMARY:
Over [TIMEFRAME], the subject made [COUNT] outward remittances of small amounts
([AMOUNT RANGE] each) totaling [TOTAL] to recipients in [HIGH-RISK COUNTRY].
Recipients appear to be individuals with no known business relationship.

SUSPICIOUS ACTIVITY DESCRIPTION:
The pattern of multiple small transfers to a high-risk jurisdiction, combined with
the absence of any legitimate business or family connection, raises concerns of
potential terrorist financing or sanctions evasion. Small amounts are typically
used to avoid detection thresholds while cumulatively moving significant value.

TYPOLOGY MATCH:
FATF Typology: "Terrorist Financing — movement of small value funds to high-risk
jurisdictions to support extremist activities while avoiding detection thresholds."

WHY THIS IS SUSPICIOUS:
1. Recipients located in FATF high-risk and monitored jurisdiction
2. No family or business connection to justify transfers
3. Customer's income does not support frequency of international transfers
4. Amounts designed to stay below SWIFT reporting thresholds
5. Customer became evasive when asked purpose of transfers
        """
    }
]

# Typology risk keywords for risk scoring
RISK_KEYWORDS = {
    "high_risk": [
        "offshore", "shell company", "cash intensive", "structuring", "smurfing",
        "immediately transferred", "same day", "high risk jurisdiction", "fatf",
        "hawala", "cryptocurrency", "multiple accounts", "layering", "no business purpose",
        "beneficial owner unknown", "pep", "politically exposed", "sanctions"
    ],
    "medium_risk": [
        "unusual pattern", "inconsistent", "new beneficiary", "first time",
        "cannot explain", "no salary", "bulk transfer", "round amount",
        "late night transaction", "multiple devices", "new location"
    ],
    "low_risk": [
        "regular transaction", "known beneficiary", "salary credit",
        "utility payment", "small amount", "domestic transfer"
    ]
}

TYPOLOGY_PATTERNS = {
    "Money Laundering - Layering": [
        "multiple accounts", "international transfer", "same day", "layering",
        "offshore", "different sources", "immediately wired", "aggregation"
    ],
    "Structuring / Smurfing": [
        "below threshold", "cash deposits", "multiple deposits", "49000", "49,000",
        "sub-threshold", "structured", "avoid reporting", "fragmented"
    ],
    "Account Takeover Fraud": [
        "new device", "new location", "new beneficiary", "unauthorized",
        "unrecognized", "customer confirmed", "mule account", "credential"
    ],
    "Trade-Based Money Laundering": [
        "invoice", "import", "export", "customs", "trade", "discrepancy",
        "over-invoicing", "under-invoicing", "goods value"
    ],
    "Terrorist Financing": [
        "high risk country", "small transfers", "sanctioned", "fatf listed",
        "no business relationship", "frequent small", "monitored jurisdiction"
    ]
}
