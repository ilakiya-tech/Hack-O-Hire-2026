"""
scenarios.py
Pre-built demo scenarios for testing and presentation.
Use these during the hackathon demo to impress judges.
"""

DEMO_SCENARIOS = [
    {
        "name": "Scenario 1: Money Laundering (Layering)",
        "customer_name": "Rajesh Kumar Sharma",
        "account_number": "SB-4521-8834-2201",
        "analyst_name": "Priya Verma",
        "transactions": """
TRANSACTION PERIOD: 01-Feb-2026 to 08-Feb-2026
ACCOUNT TYPE: Savings Account | CUSTOMER SINCE: 2019 | OCCUPATION: Textile Trader

INBOUND TRANSACTIONS (Week of Feb 1-7):
- 01-Feb: ₹1,10,000 from ACC-2341 (Unknown Individual, Mumbai)
- 01-Feb: ₹98,500  from ACC-7821 (Unknown Individual, Delhi)
- 02-Feb: ₹1,25,000 from ACC-3301 (Unknown Individual, Surat)
- 02-Feb: ₹87,000  from ACC-9912 (Unknown Individual, Kolkata)
- 03-Feb: ₹1,40,000 from ACC-4421 (Unknown Individual, Chennai)
- 03-Feb: ₹1,15,000 from ACC-6621 (Unknown Individual, Hyderabad)
- 04-Feb: ₹92,000  from ACC-8831 (Unknown Individual, Pune)
- 04-Feb: ₹1,08,000 from ACC-1142 (Unknown Individual, Bangalore)
- 05-Feb: ₹1,33,000 from ACC-5521 (Unknown Individual, Ahmedabad)
- 05-Feb: ₹97,500  from ACC-7741 (Unknown Individual, Jaipur)
- 06-Feb: ₹1,21,000 from ACC-2211 (Unknown Individual, Lucknow)
- 06-Feb: ₹88,500  from ACC-4431 (Unknown Individual, Nagpur)
[... 35 more similar transactions totaling ₹50,23,500 from 47 unique accounts]

OUTBOUND TRANSACTION:
- 07-Feb: ₹49,85,000 via SWIFT Wire Transfer to HSBC Dubai, UAE
  Beneficiary: Al-Manar Trading LLC (Account: AE760330000010284920201)
  Purpose stated: "Trade payment for textile goods"

ACCOUNT HISTORY:
- Average monthly credit (last 12 months): ₹2.1 lakhs
- No prior international transactions
- No import/export license on file
- No invoices provided for the stated trade payment
- Customer unreachable on registered mobile number
        """,
        "additional_context": "Customer has no prior international transactions. No trade license on file. 47 unique senders with no prior relationship to customer. Same-day aggregation and wiring of funds is highly unusual."
    },
    {
        "name": "Scenario 2: Structuring / Smurfing",
        "customer_name": "Anita Desai",
        "account_number": "CA-3312-9901-7745",
        "analyst_name": "Suresh Nair",
        "transactions": """
TRANSACTION PERIOD: 10-Feb-2026 to 13-Feb-2026
ACCOUNT TYPE: Current Account | CUSTOMER SINCE: 2023 | OCCUPATION: Self-employed (declared)

CASH DEPOSITS - CHRONOLOGICAL ORDER:
- 10-Feb 10:23 AM: Cash deposit ₹49,500 at Branch ATM, Andheri West
- 10-Feb 02:41 PM: Cash deposit ₹48,900 at Branch Counter, Andheri East  
- 11-Feb 09:15 AM: Cash deposit ₹49,800 at Branch ATM, Bandra
- 11-Feb 11:30 AM: Cash deposit ₹49,200 at Branch Counter, Kurla
- 11-Feb 04:22 PM: Cash deposit ₹48,500 at Branch ATM, Dharavi
- 12-Feb 10:05 AM: Cash deposit ₹49,700 at Branch Counter, Sion
- 12-Feb 02:18 PM: Cash deposit ₹49,300 at Branch ATM, Chembur
- 13-Feb 09:45 AM: Cash deposit ₹48,800 at Branch Counter, Ghatkopar
- 13-Feb 03:30 PM: Cash deposit ₹49,100 at Branch ATM, Vikhroli

TOTAL DEPOSITED: ₹4,42,800 across 9 transactions in 4 days
EACH TRANSACTION: Below ₹50,000 CTR reporting threshold

ACCOUNT ANALYSIS:
- No salary credit in last 6 months
- No business income or GST registration
- All deposits in cash (no NEFT/RTGS/UPI inflows)
- Immediately after last deposit: ₹4,38,000 transferred to crypto exchange wallet
- Different branch locations each time (geographic spreading)
        """,
        "additional_context": "Classic structuring pattern. All 9 deposits deliberately below ₹50,000 mandatory CTR reporting threshold. Different branch locations used to avoid teller recognition. Immediate transfer to crypto exchange post-aggregation."
    },
    {
        "name": "Scenario 3: Account Takeover Fraud",
        "customer_name": "Dr. Vikram Mehta",
        "account_number": "SB-7823-4412-9901",
        "analyst_name": "Kavya Reddy",
        "transactions": """
TRANSACTION PERIOD: 15-Feb-2026 (Single Day Event)
ACCOUNT TYPE: Savings Account | CUSTOMER SINCE: 2015 | OCCUPATION: Senior Physician
ACCOUNT BALANCE PRIOR: ₹28,45,000

SEQUENCE OF EVENTS:
- 15-Feb 02:14 AM: Login from new device (iPhone 15 Pro, Device ID: D-9921-XK)
  IP: 185.243.112.44 (VPN detected, Physical location: Eastern Europe)
  [Customer's registered device: Samsung Galaxy S22, Last login: 14-Feb from Mumbai]

- 15-Feb 02:16 AM: New beneficiary added — "Raghav Enterprises" 
  Account: 9934871200012 | Bank: YES Bank | IFSC: YESB0001234

- 15-Feb 02:17 AM: OTP-based authentication completed
  [OTP delivered to registered mobile — SIM swap suspected]

- 15-Feb 02:19 AM: IMPS Transfer ₹9,90,000 to Raghav Enterprises
  [Amount just below ₹10L RTGS mandatory limit]

- 15-Feb 02:23 AM: IMPS Transfer ₹9,85,000 to Raghav Enterprises
  
- 15-Feb 02:26 AM: IMPS Transfer ₹8,60,000 to Raghav Enterprises

TOTAL TRANSFERRED: ₹28,35,000 (99.6% of account balance) in 7 minutes

CUSTOMER CONTACT:
- Customer called bank at 09:30 AM on 15-Feb
- Confirmed he did NOT initiate any transactions
- Was asleep at time of transactions
- Reports his phone was acting strangely previous evening (possible SIM swap)

BENEFICIARY ACCOUNT STATUS:
- Raghav Enterprises account created 3 days ago
- Already flagged as mule account by 2 other banks in consortium
        """,
        "additional_context": "Customer confirmed transactions are unauthorized. SIM swap suspected. Beneficiary account is a known mule account flagged by fraud consortium. 3 rapid transfers totaling ₹28.35L in 7 minutes depleted 99.6% of account balance."
    }
]


def get_scenario(index: int) -> dict:
    """Get a demo scenario by index (0-based)."""
    if 0 <= index < len(DEMO_SCENARIOS):
        return DEMO_SCENARIOS[index]
    return DEMO_SCENARIOS[0]


def get_all_scenario_names() -> list:
    """Get list of scenario names for display."""
    return [s["name"] for s in DEMO_SCENARIOS]
