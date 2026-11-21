"""Generate the synthetic Northwind Bank policy library and a question set with known ground truth.

Every answer is a value written into a document by this script, so labels are correct by construction.
Run:  uv run python scripts/make_corpus.py
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
OUT = Path(__file__).resolve().parents[1] / "data"
CORPUS = OUT / "corpus"
rng = random.Random(7)

DOCS: dict[str, dict] = {}  # id -> {title, access, fmt, scanned, sections: {heading: [fact]}, tables: [...]}
FACTS: list[dict] = []


def doc(doc_id, title, access, fmt, scanned=False):
    DOCS[doc_id] = dict(
        title=title, access=access, fmt=fmt, scanned=scanned, sections=defaultdict(list), tables=[]
    )


def fact(doc_id, section, statement, question, answer, role_lang="en"):
    f = dict(
        doc=doc_id, section=section, statement=statement, question=question, answer=answer, lang=role_lang
    )
    DOCS[doc_id]["sections"][section].append(f)
    FACTS.append(f)


def pkr(n):
    return f"{n:,}"


# ---------------- HR leave policy (internal, docx)
doc("hr_leave_policy", "HR Leave Policy", "internal", "docx")
leave = {
    "annual": 21,
    "sick": 10,
    "casual": 8,
    "maternity": 90,
    "paternity": 7,
    "bereavement": 5,
    "Hajj": 30,
    "marriage": 3,
    "study": 12,
}
for i, (name, days) in enumerate(leave.items()):
    fact(
        "hr_leave_policy",
        f"{i + 1}. {name.capitalize()} leave",
        f"Permanent employees are entitled to {days} days of paid {name} leave.",
        f"How many days of paid {name} leave are permanent employees entitled to?",
        str(days),
    )
fact(
    "hr_leave_policy",
    "10. Applying for leave",
    "Leave requests must be submitted 3 working days in advance.",
    "How many working days in advance must leave requests be submitted?",
    "3",
)
fact(
    "hr_leave_policy",
    "11. Carry forward",
    "Unused annual leave can be carried forward up to 15 days.",
    "How many days of unused annual leave can be carried forward?",
    "15",
)
fact(
    "hr_leave_policy",
    "12. Medical certificates",
    "A medical certificate is required for sick leave longer than 2 consecutive days.",
    "After how many consecutive days of sick leave is a medical certificate required?",
    "2",
)

# ---------------- Code of conduct (public, pdf)
doc("code_of_conduct", "Code of Conduct", "public", "pdf")
for i, (s, q, a) in enumerate(
    [
        (
            "Employees must not accept gifts worth more than PKR 5,000 from any supplier.",
            "What is the maximum value of a gift an employee may accept from a supplier?",
            "5,000",
        ),
        (
            "Any breach of this code must be reported within 7 days of becoming aware of it.",
            "Within how many days must a breach of the code of conduct be reported?",
            "7",
        ),
        (
            "Conflict of interest declarations are renewed every January.",
            "In which month are conflict of interest declarations renewed?",
            "January",
        ),
        (
            "Every employee completes 4 hours of ethics training each year.",
            "How many hours of ethics training does each employee complete per year?",
            "4",
        ),
        (
            "The duty of confidentiality continues for 3 years after an employee leaves.",
            "For how many years after leaving does the duty of confidentiality continue?",
            "3",
        ),
        (
            "Political donations on behalf of the bank are not permitted.",
            "Are political donations on behalf of the bank permitted?",
            "not permitted",
        ),
        (
            "Insider trading concerns should be escalated to the Chief Compliance Officer.",
            "Who should insider trading concerns be escalated to?",
            "Chief Compliance Officer",
        ),
    ]
):
    fact("code_of_conduct", f"{i + 1}. Standards of conduct {i + 1}", s, q, a)

# ---------------- IT security (internal, pdf)
doc("it_security_policy", "IT Security Policy", "internal", "pdf")
for i, (s, q, a) in enumerate(
    [
        ("Passwords must be at least 14 characters long.", "What is the minimum password length?", "14"),
        ("Passwords must be changed every 90 days.", "How often must passwords be changed?", "90"),
        (
            "Multi factor authentication is mandatory for all VPN access.",
            "Which type of access requires multi factor authentication?",
            "VPN",
        ),
        (
            "A lost or stolen device must be reported within 2 hours.",
            "Within how many hours must a lost or stolen device be reported?",
            "2",
        ),
        (
            "Workstations lock automatically after 5 minutes of inactivity.",
            "After how many minutes of inactivity do workstations lock?",
            "5",
        ),
        ("Backups are retained for 35 days.", "For how many days are backups retained?", "35"),
        (
            "Critical security patches must be applied within 72 hours of release.",
            "Within how many hours must critical security patches be applied?",
            "72",
        ),
        (
            "USB mass storage is disabled on all corporate laptops.",
            "What is disabled on all corporate laptops?",
            "USB mass storage",
        ),
        (
            "Suspected phishing emails are forwarded to security@northwind.example.",
            "Where should suspected phishing emails be forwarded?",
            "security@northwind.example",
        ),
    ]
):
    fact("it_security_policy", f"{i + 1}. Security control {i + 1}", s, q, a)

# ---------------- Travel and expense (internal, pdf with table)
doc("travel_expense_policy", "Travel and Expense Policy", "internal", "pdf")
fact(
    "travel_expense_policy",
    "1. Receipts",
    "Receipts are required for any expense above PKR 1,500.",
    "Above what amount is a receipt required for an expense?",
    "1,500",
)
fact(
    "travel_expense_policy",
    "2. Claim deadline",
    "Expense claims must be filed within 14 days of travel.",
    "Within how many days of travel must expense claims be filed?",
    "14",
)
fact(
    "travel_expense_policy",
    "3. Air travel",
    "Air travel is economy class for flights under 4 hours.",
    "Up to how many hours of flight is economy class used?",
    "4",
)
head = ["Grade", "Hotel cap per night (PKR)", "Daily meal allowance (PKR)", "Mileage rate (PKR per km)"]
rows = [
    [
        f"Grade {g}",
        rng.randrange(8, 40) * 1000 + 500 * g,
        rng.randrange(15, 60) * 100 + 50 * g,
        rng.randrange(20, 45) + g,
    ]
    for g in range(1, 7)
]
DOCS["travel_expense_policy"]["tables"].append(("4. Allowances by grade", head, rows))
for r in rows:
    for ci, (col, qtxt) in enumerate([(1, "hotel cap per night"), (2, "daily meal allowance")]):
        if ci == 0 or r[0] in ("Grade 2", "Grade 4", "Grade 6"):
            FACTS.append(
                dict(
                    doc="travel_expense_policy",
                    section="4. Allowances by grade",
                    lang="en",
                    statement=f"Grade: {r[0]}; {head[col]}: {pkr(r[col])}",
                    question=f"What is the {qtxt} for {r[0]}?",
                    answer=pkr(r[col]),
                )
            )

# ---------------- Salary bands (hr_only, xlsx)
doc("salary_bands", "Salary Bands 2026", "hr_only", "xlsx")
head = ["Grade", "Minimum salary (PKR)", "Maximum salary (PKR)", "Annual bonus target (%)"]
rows = []
base = 90000
for g in range(1, 7):
    lo = base + rng.randrange(0, 9) * 1000
    rows.append([f"Grade {g}", lo, lo + rng.randrange(40, 90) * 1000, rng.choice([6, 8, 10, 12, 15, 18, 20])])
    base = lo * 2 - 30000
DOCS["salary_bands"]["tables"].append(("Bands", head, rows))
for r in rows:
    for col, qtxt in ((2, "maximum monthly salary"), (3, "annual bonus target percentage")):
        if col == 2 or r[0] in ("Grade 1", "Grade 3", "Grade 5"):
            FACTS.append(
                dict(
                    doc="salary_bands",
                    section="Bands",
                    lang="en",
                    statement=f"Grade: {r[0]}; {head[col]}: {pkr(r[col]) if col == 2 else r[col]}",
                    question=f"What is the {qtxt} for {r[0]}?",
                    answer=pkr(r[col]) if col == 2 else str(r[col]),
                )
            )

# ---------------- Compensation review (hr_only, docx)
doc("compensation_review_policy", "Compensation Review Policy", "hr_only", "docx")
for i, (s, q, a) in enumerate(
    [
        (
            "The annual increment budget for 2026 is 8 percent of payroll.",
            "What is the annual increment budget for 2026 as a percentage of payroll?",
            "8",
        ),
        (
            "Compensation reviews take place in April.",
            "In which month do compensation reviews take place?",
            "April",
        ),
        (
            "Performance is rated on a scale from 1 to 5, and a rating of 4 or above qualifies for promotion.",  # noqa: E501
            "What minimum performance rating qualifies an employee for promotion?",
            "4",
        ),
        (
            "Promotion requires a minimum tenure of 24 months in the current grade.",
            "What is the minimum tenure in months required for promotion?",
            "24",
        ),
        (
            "The probation period for new hires is 3 months.",
            "How long is the probation period for new hires?",
            "3",
        ),
        (
            "Retention bonuses are capped at 25 percent of annual base salary.",
            "What is the cap on retention bonuses as a percentage of base salary?",
            "25",
        ),
    ]
):
    fact("compensation_review_policy", f"{i + 1}. Compensation rule {i + 1}", s, q, a)

# ---------------- Finance approval matrix (finance_only, pdf table)
doc("finance_approval_matrix", "Finance Approval Matrix", "finance_only", "pdf")
head = ["Role", "Single transaction limit (PKR)", "Monthly limit (PKR)"]
rows = [
    ["Branch Manager", 500000, 5000000],
    ["Regional Head", 2500000, 20000000],
    ["Director Finance", 10000000, 80000000],
    ["CFO", 50000000, 300000000],
    ["CEO", 200000000, 900000000],
]
DOCS["finance_approval_matrix"]["tables"].append(("1. Approval limits by role", head, rows))
for r in rows:
    FACTS.append(
        dict(
            doc="finance_approval_matrix",
            section="1. Approval limits by role",
            lang="en",
            statement=f"Role: {r[0]}; {head[1]}: {pkr(r[1])}",
            question=f"What is the single transaction approval limit for the {r[0]}?",
            answer=pkr(r[1]),
        )
    )
    if r[0] in ("CFO", "Regional Head", "CEO"):
        FACTS.append(
            dict(
                doc="finance_approval_matrix",
                section="1. Approval limits by role",
                lang="en",
                statement=f"Role: {r[0]}; {head[2]}: {pkr(r[2])}",
                question=f"What is the monthly approval limit for the {r[0]}?",
                answer=pkr(r[2]),
            )
        )
fact(
    "finance_approval_matrix",
    "2. Dual approval",
    "Payments above PKR 100,000,000 need dual approval.",
    "Above what amount do payments need dual approval?",
    "100,000,000",
)

# ---------------- Treasury limits (finance_only, scanned pdf)
doc("treasury_limits", "Treasury Risk Limits", "finance_only", "pdf", scanned=True)
for i, (s, q, a) in enumerate(
    [
        (
            "The net open foreign exchange position limit is USD 2.5 million.",
            "What is the net open foreign exchange position limit?",
            "2.5",
        ),
        (
            "The single counterparty exposure limit is PKR 500 million.",
            "What is the single counterparty exposure limit?",
            "500",
        ),
        (
            "The treasury stop loss trigger is 2.5 percent of position value.",
            "What is the treasury stop loss trigger as a percentage of position value?",
            "2.5",
        ),
        (
            "The liquidity buffer must stay above 12 percent of deposits.",
            "What percentage of deposits must the liquidity buffer stay above?",
            "12",
        ),
        (
            "Limit breaches are reported to the Risk Committee within 1 business day.",
            "Within how many business days are limit breaches reported to the Risk Committee?",
            "1",
        ),
    ]
):
    fact("treasury_limits", f"{i + 1}. Treasury limit {i + 1}", s, q, a)

# ---------------- Branch operations manual (internal, scanned pdf)
doc("branch_operations_manual", "Branch Operations Manual", "internal", "pdf", scanned=True)
for i, (s, q, a) in enumerate(
    [
        ("The branch vault cash limit is PKR 25 million.", "What is the branch vault cash limit?", "25"),
        (
            "Dual control is required for cash movements above PKR 500,000.",
            "Above what amount is dual control required for cash movements?",
            "500,000",
        ),
        ("ATMs are replenished every 3 days.", "How often are ATMs replenished?", "3"),
        ("CCTV footage is retained for 90 days.", "For how many days is CCTV footage retained?", "90"),
        ("Branches open to customers at 09:00.", "At what time do branches open to customers?", "09:00"),
        (
            "Counterfeit notes must be reported to the branch manager the same day.",
            "Who must counterfeit notes be reported to?",
            "branch manager",
        ),
    ]
):
    fact("branch_operations_manual", f"{i + 1}. Branch rule {i + 1}", s, q, a)

# ---------------- Procurement (internal, html)
doc("procurement_policy", "Procurement Policy", "internal", "html")
for i, (s, q, a) in enumerate(
    [
        (
            "Purchases above PKR 250,000 require 3 competitive quotations.",
            "Above what amount are competitive quotations required?",
            "250,000",
        ),
        (
            "Purchases above PKR 2,000,000 must go to open tender.",
            "Above what amount must a purchase go to open tender?",
            "2,000,000",
        ),
        (
            "The bid evaluation committee has 5 members.",
            "How many members are on the bid evaluation committee?",
            "5",
        ),
        (
            "Approved vendors are re-evaluated every 12 months.",
            "How often are approved vendors re-evaluated, in months?",
            "12",
        ),
        (
            "Bids remain valid for 90 days from the closing date.",
            "For how many days do bids remain valid?",
            "90",
        ),
        (
            "Contracts above PKR 10,000,000 require legal review.",
            "Above what contract value is legal review required?",
            "10,000,000",
        ),
    ]
):
    fact("procurement_policy", f"{i + 1}. Procurement rule {i + 1}", s, q, a)

# ---------------- Whistleblower (public, Urdu txt)
doc("whistleblower_policy_ur", "وسل بلوور پالیسی", "public", "txt")
for i, (s, q, a) in enumerate(
    [
        (
            "کوئی بھی ملازم خلاف ورزی کی اطلاع ایتھکس ہاٹ لائن پر دے سکتا ہے۔ ہاٹ لائن نمبر 0800-55-100 ہے۔",
            "ایتھکس ہاٹ لائن کا نمبر کیا ہے؟",
            "0800-55-100",
        ),
        (
            "شکایت موصول ہونے کے 5 کام کے دنوں میں اس کی تصدیق کی جاتی ہے۔",
            "شکایت کی تصدیق کتنے کام کے دنوں میں کی جاتی ہے؟",
            "5",
        ),
        ("تحقیقات 45 دن میں مکمل کی جائیں گی۔", "تحقیقات کتنے دنوں میں مکمل کی جاتی ہیں؟", "45"),
        (
            "شکایت کنندہ کی شناخت 10 سال تک خفیہ رکھی جائے گی۔",
            "شکایت کنندہ کی شناخت کتنے سال تک خفیہ رکھی جاتی ہے؟",
            "10",
        ),
        (
            "انتقامی کارروائی کی شکایت 14 دن کے اندر کمیٹی کو دی جا سکتی ہے۔",
            "انتقامی کارروائی کی شکایت کتنے دن کے اندر کمیٹی کو دی جا سکتی ہے؟",
            "14",
        ),
        ("جھوٹی شکایت پر 3 ماہ کی معطلی ہو سکتی ہے۔", "جھوٹی شکایت پر کتنے ماہ کی معطلی ہو سکتی ہے؟", "3"),
        ("ہاٹ لائن 24 گھنٹے دستیاب رہتی ہے۔", "ہاٹ لائن کتنے گھنٹے دستیاب رہتی ہے؟", "24"),
    ]
):
    fact("whistleblower_policy_ur", f"{i + 1}. دفعہ {i + 1}", s, q, a, "ur")

# ---------------- Remote work (internal, html, mixed Urdu and English)
doc("remote_work_policy", "Remote Work Policy / ریموٹ ورک پالیسی", "internal", "html")
for i, (s, q, a, lg) in enumerate(
    [
        (
            "Employees may work remotely up to 2 days per week (ہفتے میں 2 دن).",
            "Remote work کے لیے ہفتے میں کتنے دن allowed ہیں؟",
            "2",
            "mixed",
        ),
        (
            "Core collaboration hours are 11:00 to 16:00 (بنیادی اوقات).",
            "Core collaboration hours کب سے شروع ہوتے ہیں؟",
            "11:00",
            "mixed",
        ),
        (
            "A monthly internet allowance of PKR 3,500 is paid to remote workers.",
            "What monthly internet allowance is paid to remote workers?",
            "3,500",
            "en",
        ),
        (
            "Equipment loans are repaid over 12 months.",
            "Over how many months are equipment loans repaid?",
            "12",
            "en",
        ),
        (
            "VPN use is mandatory when working remotely.",
            "What is mandatory when working remotely?",
            "VPN",
            "en",
        ),
        (
            "Manager approval for remote work is given within 3 working days.",
            "Within how many working days is manager approval for remote work given?",
            "3",
            "en",
        ),
    ]
):
    fact("remote_work_policy", f"{i + 1}. Remote rule {i + 1}", s, q, a, lg)

# ---------------- Board budget (finance_only, xlsx)
doc("board_budget_2026", "Board Budget 2026", "finance_only", "xlsx")
head = ["Department", "Budget 2026 (PKR million)", "Headcount"]
rows = [
    [d, rng.randrange(80, 900), rng.randrange(20, 400)]
    for d in [
        "Engineering",
        "Operations",
        "Human Resources",
        "Finance",
        "Marketing",
        "Legal",
        "Risk",
        "Compliance",
    ]
]
DOCS["board_budget_2026"]["tables"].append(("Budget", head, rows))
for r in rows:
    FACTS.append(
        dict(
            doc="board_budget_2026",
            section="Budget",
            lang="en",
            statement=f"Department: {r[0]}; {head[1]}: {r[1]}",
            question=f"What is the 2026 budget in PKR million for {r[0]}?",
            answer=str(r[1]),
        )
    )
    if r[0] in ("Engineering", "Risk", "Legal"):
        FACTS.append(
            dict(
                doc="board_budget_2026",
                section="Budget",
                lang="en",
                statement=f"Department: {r[0]}; {head[2]}: {r[2]}",
                question=f"What is the headcount of the {r[0]} department?",
                answer=str(r[2]),
            )
        )

# ---------------- Disciplinary procedure (hr_only, docx)
doc("disciplinary_procedure", "Disciplinary Procedure", "hr_only", "docx")
for i, (s, q, a) in enumerate(
    [
        (
            "A verbal warning remains valid for 6 months.",
            "How long does a verbal warning remain valid, in months?",
            "6",
        ),
        (
            "A written warning remains valid for 12 months.",
            "How long does a written warning remain valid, in months?",
            "12",
        ),
        (
            "Suspension with pay may not exceed 30 days.",
            "What is the maximum suspension with pay, in days?",
            "30",
        ),
        (
            "An appeal must be lodged within 7 days of the decision.",
            "Within how many days must a disciplinary appeal be lodged?",
            "7",
        ),
        (
            "The employee receives 3 days notice of a disciplinary hearing.",
            "How many days notice does an employee receive of a disciplinary hearing?",
            "3",
        ),
        (
            "Hearings are chaired by a director who is not in the employee's reporting line.",
            "Who chairs a disciplinary hearing?",
            "director",
        ),
    ]
):
    fact("disciplinary_procedure", f"{i + 1}. Disciplinary step {i + 1}", s, q, a)

# ---------------- Filler, so facts are not the only text on a page
FILLER = [
    "This section applies to all permanent staff unless stated otherwise.",
    "Managers are responsible for communicating these rules to their teams.",
    "Exceptions require written approval and are recorded for audit purposes.",
    "Questions about interpretation should be directed to the policy owner.",
    "This document is reviewed periodically and supersedes earlier versions.",
    "Staff are expected to read this policy as part of their induction.",
]

UNANSWERABLE = [
    "What is the dental insurance coverage limit for employees?",
    "Does the company provide gym memberships?",
    "What is the dress code on Fridays?",
    "How many days of sabbatical leave are available?",
    "How many days of adoption leave do employees get?",
    "What is the parking allowance for executives?",
    "What is the CEO's annual salary?",
    "Which cloud provider hosts the HR system?",
    "What is the stock option vesting schedule?",
    "How many days of leave are given for Eid holidays?",
    "What is the policy on pets in the office?",
    "Who is the head of the legal department?",
    "What is the maximum loan amount for staff housing loans?",
    "How many shares does the board hold in the bank?",
    "What interest rate is charged on staff car loans?",
    "What is the cafeteria menu this week?",
    "How many parking spaces does the head office have?",
    "What is the process for requesting a company car?",
    "When is the next annual general meeting?",
    "What is the maternity leave policy of the competitor bank?",
    "How long is the notice period for senior management?",
    "What is the minimum balance for a savings account?",
    "What are the rules for working from another country?",
    "How much is the overtime rate per hour?",
    "What is the bank's credit rating?",
    "کمپنی کی گاڑی کی پالیسی کیا ہے؟",
    "دفتر میں کھانے کا الاؤنس کتنا ہے؟",
    "ملازمین کو میڈیکل انشورنس کی حد کتنی ملتی ہے؟",
    "What is the password policy for customers of the mobile app?",
    "Which vendor supplies the ATM machines?",
]

ROLE_FOR = {"public": "employee", "internal": "employee", "hr_only": "hr", "finance_only": "finance"}


# ---------------- Rendering
def render_pdf(d_id, d, path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    ss = getSampleStyleSheet()
    story = [Paragraph(d["title"], ss["Title"]), Spacer(1, 8)]
    items = [(h, fs, None) for h, fs in d["sections"].items()] + [
        (h, None, (hd, rw)) for h, hd, rw in d["tables"]
    ]
    page_of = {}
    for n, (h, fs, tbl) in enumerate(items):
        if n and n % 2 == 0:
            story.append(PageBreak())
        story.append(Paragraph(h, ss["Heading2"]))
        for f in fs or []:
            story.append(Paragraph(f["statement"], ss["BodyText"]))
            story.append(Paragraph(rng.choice(FILLER), ss["BodyText"]))
            page_of[f["statement"]] = n // 2 + 1
        if tbl:
            t = Table([tbl[0]] + [[str(c) if not isinstance(c, int) else pkr(c) for c in r] for r in tbl[1]])
            t.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ]
                )
            )
            story += [t, Spacer(1, 8)]
            for f in FACTS:
                if f["doc"] == d_id and f["section"] == h:
                    page_of[f["statement"]] = n // 2 + 1
    SimpleDocTemplate(str(path), pagesize=A4).build(story)
    return page_of


def make_scanned(src, dst):
    """Rasterise a digital PDF into an image only, slightly rotated and noisy PDF (a simulated scan)."""
    import io

    import fitz
    import numpy as np
    from PIL import Image

    out, gen = fitz.open(), np.random.default_rng(3)
    for page in fitz.open(src):
        img = (
            Image.open(io.BytesIO(page.get_pixmap(dpi=130).tobytes("png")))
            .convert("L")
            .rotate(0.6, expand=False, fillcolor=255)
        )
        arr = np.clip(np.asarray(img, dtype=np.float32) + gen.normal(0, 9, (img.height, img.width)), 0, 255)
        buf = io.BytesIO()
        Image.fromarray(arr.astype("uint8")).save(buf, "JPEG", quality=70)
        p = out.new_page(width=page.rect.width, height=page.rect.height)
        p.insert_image(p.rect, stream=buf.getvalue())
    out.save(dst)


def render_docx(d, path):
    import docx

    document = docx.Document()
    document.add_heading(d["title"], 0)
    for h, fs in d["sections"].items():
        document.add_heading(h, 1)
        for f in fs:
            document.add_paragraph(f["statement"])
            document.add_paragraph(rng.choice(FILLER))
    for h, hd, rw in d["tables"]:
        document.add_heading(h, 1)
        t = document.add_table(rows=1, cols=len(hd))
        for i, c in enumerate(hd):
            t.rows[0].cells[i].text = c
        for r in rw:
            cells = t.add_row().cells
            for i, c in enumerate(r):
                cells[i].text = str(c)
    document.save(path)


def render_xlsx(d, path):
    import openpyxl

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for h, hd, rw in d["tables"]:
        ws = wb.create_sheet(h)
        ws.append(hd)
        for r in rw:
            ws.append(r)
    wb.save(path)


def render_html(d, path):
    parts = [f"<html><body><h1>{d['title']}</h1>"]
    for h, fs in d["sections"].items():
        parts.append(f"<h2>{h}</h2>")
        for f in fs:
            parts.append(f"<p>{f['statement']}</p><p>{rng.choice(FILLER)}</p>")
    path.write_text("".join(parts) + "</body></html>", encoding="utf-8")


def render_txt(d, path):
    lines = [f"# {d['title']}"]
    for h, fs in d["sections"].items():
        lines.append(f"## {h}")
        lines += [f["statement"] for f in fs]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    import tempfile

    CORPUS.mkdir(parents=True, exist_ok=True)
    manifest, page_map = [], {}
    for d_id, d in DOCS.items():
        fmt = d["fmt"]
        path = CORPUS / f"{d_id}.{fmt}"
        if fmt == "pdf":
            tmp = Path(tempfile.mkdtemp()) / "t.pdf" if d["scanned"] else path
            page_map.update(render_pdf(d_id, d, tmp))
            if d["scanned"]:
                make_scanned(tmp, path)
        else:
            {"docx": render_docx, "xlsx": render_xlsx, "html": render_html, "txt": render_txt}[fmt](d, path)
        manifest.append(
            dict(
                doc_id=d_id,
                file=path.name,
                path=f"corpus/{path.name}",
                title=d["title"],
                access_level=d["access"],
                fmt=fmt,
                scanned=d["scanned"],
            )
        )
    questions = []

    def cat(f):
        d = DOCS[f["doc"]]
        if f["lang"] == "ur":
            return "urdu"
        if f["lang"] == "mixed":
            return "mixed"
        if d["scanned"]:
            return "scanned"
        return "table" if f["section"] in {t[0] for t in d["tables"]} else "text"

    for n, f in enumerate(FACTS):
        access = DOCS[f["doc"]]["access"]
        base = dict(
            gold_doc=f["doc"],
            gold_page=page_map.get(f["statement"], 1),
            gold_answer=f["answer"],
            evidence=f["statement"],
            label_source="script_from_facts",
        )
        questions.append(
            dict(
                id=f"a{n:03d}",
                question=f["question"],
                category=cat(f),
                role=ROLE_FOR[access],
                answerable=True,
                **base,
            )
        )
        if access in ("hr_only", "finance_only"):  # the same question asked by someone without access
            questions.append(
                dict(
                    id=f"r{n:03d}",
                    question=f["question"],
                    category="restricted",
                    role="employee",
                    answerable=False,
                    forbidden_doc=f["doc"],
                    **base,
                )
            )
    for n, q in enumerate(UNANSWERABLE):
        questions.append(
            dict(
                id=f"u{n:03d}",
                question=q,
                category="unanswerable",
                role="employee",
                answerable=False,
                label_source="hand_written",
            )
        )
    import fitz
    from public_questions import PUBLIC

    for f in sorted((OUT / "public").glob("*.pdf")):
        scanned = sum(len(p.get_text()) for p in fitz.open(f)) < 100
        manifest.append(
            dict(
                doc_id=f.stem,
                file=f.name,
                path=f"public/{f.name}",
                title=f.stem.replace("_", " "),
                access_level="public",
                fmt="pdf",
                scanned=scanned,
            )
        )
    scanned_docs = {m["doc_id"] for m in manifest if m["scanned"]}
    for n, (fn, page, q, ans, ev) in enumerate(PUBLIC):
        questions.append(
            dict(
                id=f"p{n:03d}",
                question=q,
                category="public_scanned" if fn[:-4] in scanned_docs else "public",
                role="employee",
                answerable=True,
                gold_doc=fn[:-4],
                gold_page=page,
                gold_answer=ans,
                evidence=ev,
                label_source="ai_written_from_text",
                reviewed=False,
            )
        )
    order = sorted(q["id"] for q in questions)
    random.Random(11).shuffle(order)
    split = {qid: ("val" if i < 0.4 * len(order) else "test") for i, qid in enumerate(order)}
    for q in questions:
        q["split"] = split[q["id"]]
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (OUT / "questions.json").write_text(json.dumps(questions, indent=1, ensure_ascii=False), encoding="utf-8")
    by = defaultdict(int)
    for q in questions:
        by[q["category"]] += 1
    print(f"{len(manifest)} documents, {len(questions)} questions", dict(by))


if __name__ == "__main__":
    main()
