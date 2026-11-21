"""Questions about the public regulator PDFs in data/public/.

Labels are AI written from the document text (each carries the source sentence as `evidence`) and are NOT yet
reviewed by a human: they are flagged reviewed=False. Use scripts/review_labels.py to confirm or fix them.
"""

# (file, page, question, gold_answer, evidence sentence copied from the PDF text)
PUBLIC = [
    (
        "hec_plagiarism_policy.pdf",
        12,
        "Within how many days may a complainant appeal to the Syndicate under the HEC "
        "anti-plagiarism policy?",
        "30",
        "In case of disagreement, the complainant may file an appeal to the Syndicate within the next 30 days.",
    ),
    (
        "hec_plagiarism_policy.pdf",
        10,
        "After how many days of a university failing to take up a plagiarism case may "
        "HEC forward the complaint to the Chancellor?",
        "90",
        "In case of failure, on the part of the university/DAI, to take up the case as per the procedure, within 90 "
        "days, HEC may forward the complaint to the Chancellor of the university/DAI for information.",
    ),
    (
        "hec_institutional_affiliation_policy.pdf",
        7,
        "What is the minimum worth of tangible assets such as land and "
        "buildings a college must have on the ground under the HEC institutional affiliation policy?",
        "20",
        "The tangible assets in the form of land,buildings,etc.of the worth of not less than PKR 20.00 million shall "
        "be existent on the ground.",
    ),
    (
        "hec_institutional_affiliation_policy.pdf",
        5,
        "What minimum seating capacity must a college library have as a "
        "percentage of the total students for that shift?",
        "10",
        "That the library shall have a seating capacity for a minimum of 10% of the total number of students for that "
        "shift.",
    ),
    (
        "sbp_pr_housing_finance.pdf",
        6,
        "Above what amount must housing finance property be assessed by a valuator on "
        "the PBA approved panel?",
        "10",
        "Housing finance exceeding PKR 10 million shall be subject to assessment of the property by at least one "
        "valuator listed on the PBA-approved panel.",
    ),
    (
        "sbp_pr_housing_finance.pdf",
        6,
        "Up to what amount of housing finance may banks extend financing by marking a "
        "lien on the property in the land record authority records?",
        "5",
        "For housing finance up to PKR 5 million, banks and DFIs may extend financing by marking a lien on the property "
        "in the records of the relevant land-record authority.",
    ),
    (
        "sbp_pr_housing_finance.pdf",
        7,
        "After how many days overdue is housing finance classified as Substandard?",
        "180",
        "Substandard Mark-up/profit or principal overdue by 180 days or more from the due date.",
    ),
    (
        "sbp_pr_microfinance.pdf",
        14,
        "What is the maximum Loan to Value ratio under the microfinance bank prudential regulations?",
        "90",
        "Loan to Value (LTV) Ratio Loan to Value Ratio should not exceed 90%.",
    ),
    (
        "sbp_pr_microfinance.pdf",
        31,
        "Up to what percentage of CET1 capital is Tier 2 capital eligible for inclusion "
        "in the capital base of a microfinance bank?",
        "41.67",
        "Tier 2 Capital (T2): The total of Tier-2 capital shall be eligible up to a maximum of 41.67 percent of the "
        "CET1 capital (after all deductions mentioned at CET1) for inclusion in the capital base.",
    ),
    (
        "sbp_pr_microfinance.pdf",
        8,
        "What percentage of paid-up shares of a microfinance bank counts as sponsor shares?",
        "5",
        "Sponsor Shares means 5% or more paid-up shares of an MFB, acquired by a person individually or in concert with "
        "his/her family members, group companies, subsidiaries, and affiliates/associates.",
    ),
    (
        "sbp_pr_microfinance.pdf",
        40,
        "At what age may an existing President or CEO of a microfinance bank continue "
        "until the end of the current tenure?",
        "65",
        "Any existing President/CEO who has already attained the age of 65 years or attaining the age 65 years during "
        "his/her current term may continue as President till completion of the current tenure.",
    ),
    (
        "sbp_pr_sme_financing.pdf",
        9,
        "What is the limit on a clean facility to an SME borrower under the SBP SME financing regulations?",
        "10",
        "Regulation SME R-4: Limit on Clean Facility Banks & DFIs can take clean exposure (facilities extended based on "
        "cash flows of an SME secured solely against personal guarantees) of up to Rs 10 million on an SME borrower.",
    ),
    (
        "sbp_pr_sme_financing.pdf",
        13,
        "Up to what loan amount may banks use their own evaluating staff to value securities for SME loans?",
        "5",
        "Regulation SE R-5: Collateral Valuation For valuation of securities against loans up to Rs 5 million, banks & "
        "DFIs at their own discretion may either use the services of their own evaluating staff or the services of PBA "
        "approved",
    ),
    (
        "sbp_prudential_regs_ipf.pdf",
        13,
        "What is the aggregate investment limit in units of REIT as a percentage of the equity of a bank?",
        "15",
        "Aggregate investment limit in units of REIT shall be 15% of equity of the bank/DFI, exclusive of the above "
        "aggregate limits.",
    ),
    (
        "sbp_prudential_regs_ipf.pdf",
        4,
        "To what extent of their value are revaluation reserves on fixed assets "
        "included in reserves for Regulation R-1?",
        "50",
        "For the purpose of Regulation R-1, reserve shall also include revaluation reserves on account of fixed assets "
        "to the extent of 50% of their value.",
    ),
    (
        "sbp_prudential_regs_ipf.pdf",
        7,
        "What is the minimum retention period for stocks of a company, counted from "
        "the date of the last purchase?",
        "5",
        "If there are a series of purchases of stocks of a company, the minimum retention period of 5 years shall be "
        "counted from the date of the last purchase.",
    ),
    (
        "sbp_prudential_regs_ipf.pdf",
        22,
        "What risk weightage applies to exposure to banks rated AAA?",
        "25",
        "i) 25% weightage on exposure to banks/DFIs with AAA rating.",
    ),
    (
        "fbr_basic_concepts_income_tax.pdf",
        9,
        "In the FBR basic concepts guide, the rule does not apply where "
        "expenditure under a single account head does not exceed what amount?",
        "50,000",
        "However, this does not apply to the following: - Where expenditures under a single account head in aggregate "
        "does not exceed Rs.50,000;",
    ),
    (
        "fbr_obligation_to_file.pdf",
        5,
        "Below what age is an orphan exempt from filing a return solely for owning immovable property?",
        "25",
        "A widow, an orphan below the age of 25 years or a disabled person solely for the reason of owning immovable "
        "property",
    ),
]
