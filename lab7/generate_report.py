import os
import sys
import html
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 810, "PES University - Software Engineering Lab (Lab 7: Fuzz Testing)")
            self.drawRightString(559, 810, "PES2UG25CS809 | Ibrahim Khaleel")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 804, 559, 804)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 38, 559, 38)
        self.drawString(36, 26, "Department of Computer Science & Engineering | Section D")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 26, page_str)
        self.restoreState()

def format_code(code_text):
    escaped = html.escape(code_text.strip())
    escaped = escaped.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    escaped = escaped.replace("  ", "&nbsp;&nbsp;")
    return escaped.replace("\n", "<br/>")

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_block_style = ParagraphStyle(
        'Code_Block_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=7,
        leading=8.8,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderPadding=4,
        spaceBefore=2,
        spaceAfter=4
    )

    caption_style = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569'),
        alignment=1, # Center
        spaceBefore=3,
        spaceAfter=7
    )

    story = []

    # Title & Metadata Card
    story.append(Paragraph("LAB 7: FUZZ TESTING FOR INPUT VALIDATION BUGS", title_style))
    story.append(Paragraph("Software Engineering Lab Report — Automated Property-Based Testing with Hypothesis", subtitle_style))
    
    meta_data = [
        [
            Paragraph("<b>Student Name:</b> Ibrahim Khaleel", body_style),
            Paragraph("<b>Course:</b> Software Engineering Lab (SE)", body_style)
        ],
        [
            Paragraph("<b>SRN:</b> PES2UG25CS809", body_style),
            Paragraph("<b>Topic:</b> Property-Based Fuzz Testing (Hypothesis)", body_style)
        ],
        [
            Paragraph("<b>Section / Sem:</b> Section D, 5th Sem", body_style),
            Paragraph("<b>Module Assigned:</b> L6_L7_58 (Restaurant Bill Parser)", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 263])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # Section 1: Objective & Overview
    story.append(Paragraph("1. Objective & Learning Outcomes", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3B82F6'), spaceBefore=1, spaceAfter=5))
    
    story.append(Paragraph(
        "<b>Lab Objective:</b> To explore fuzz testing as an automated security and quality assurance technique by discovering, analyzing, and resolving input validation vulnerabilities in a Python application module using the Hypothesis property-based testing framework.",
        body_style
    ))
    
    outcomes = [
        "<b>Understand Fuzzing Methodology:</b> Comprehend how feeding pseudo-random, malformed, and non-canonical data uncovers unforeseen edge cases and crash conditions.",
        "<b>Property-Based Testing with Hypothesis:</b> Formulate behavioral invariants and domain constraints using <code>@given</code> decorators and strategy generators (<code>st.text()</code>, <code>st.integers()</code>, <code>st.one_of()</code>).",
        "<b>Test-Case Shrinking Analysis:</b> Leverage Hypothesis's automated shrinking engine to isolate minimal reproducible counterexamples for each failure.",
        "<b>Defensive Programming:</b> Implement defensive guards (type validation, boundaries, sanitization, zero-division guards) ensuring the module never experiences unhandled exceptions."
    ]
    for oc in outcomes:
        story.append(Paragraph(f"• {oc}", bullet_style))
    story.append(Spacer(1, 6))

    # Section 2: Fuzz Testing Concepts
    story.append(Paragraph("2. Conceptual Overview: Traditional Unit Testing vs. Property Fuzzing", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3B82F6'), spaceBefore=1, spaceAfter=5))
    story.append(Paragraph(
        "Traditional unit tests test <i>known knowns</i> — scenarios developer intuition anticipates. However, software in production encounters unexpected character sets, boundary values, whitespace anomalies, and data-type mismatches. Hypothesis tests <i>properties</i> (invariants that must hold across thousands of randomly generated inputs). When a property fails, Hypothesis systematically simplifies the input to the simplest failing case.",
        body_style
    ))

    comp_data = [
        [
            Paragraph("<b>Aspect</b>", body_style),
            Paragraph("<b>Traditional Unit Testing</b>", body_style),
            Paragraph("<b>Hypothesis Property-Based Fuzzing</b>", body_style)
        ],
        [
            Paragraph("<b>Input Selection</b>", body_style),
            Paragraph("Hardcoded exemplary inputs (e.g., '100,200', '1200/4')", body_style),
            Paragraph("Automated generation of thousands of randomized permutations", body_style)
        ],
        [
            Paragraph("<b>Coverage Scope</b>", body_style),
            Paragraph("Covers happy paths and anticipated boundary values", body_style),
            Paragraph("Surfaces bizarre edge cases (Unicode spaces, empty delimiters, negative numbers, extreme integers)", body_style)
        ],
        [
            Paragraph("<b>Debugging Aid</b>", body_style),
            Paragraph("Reports assertion failure on arbitrary hardcoded sample", body_style),
            Paragraph("Automated shrinking algorithm finds smallest reproducible trigger", body_style)
        ]
    ]
    comp_table = Table(comp_data, colWidths=[100, 205, 218])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 8))

    # Page Break for Screenshots & Execution Steps
    story.append(PageBreak())

    story.append(Paragraph("3. Step-by-Step Lab Execution & Screenshots", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3B82F6'), spaceBefore=1, spaceAfter=5))
    
    # Step 2 / SS1
    story.append(Paragraph("<b>Step 2: Initial Run of Buggy Module (Screenshot SS1)</b>", h2_style))
    story.append(Paragraph(
        "The baseline application <code>restaurant_bill_parser.py</code> was executed using standard well-formed inputs. Under ideal inputs (<code>paneer tikka</code>, <code>250,100,240</code>, and <code>1200/4</code>), the program functions correctly because it assumes inputs are always clean and valid. However, it lacks defensive checks for types, empty fields, or edge cases.",
        body_style
    ))
    
    ss_dir = r"L6_L7_58_restaurant_bill\screenshort"
    img1_path = os.path.join(ss_dir, "image.png")
    if os.path.exists(img1_path):
        story.append(Image(img1_path, width=490, height=144))
        story.append(Paragraph("Figure 1 (SS1): Baseline execution of buggy <code>restaurant_bill_parser.py</code> with standard inputs.", caption_style))
    story.append(Spacer(1, 4))

    # Step 4 / SS2
    story.append(Paragraph("<b>Step 3 & 4: Hypothesis Fuzz Testing Exposing Application Bugs (Screenshot SS2)</b>", h2_style))
    story.append(Paragraph(
        "A comprehensive property-based fuzz test suite was created in <code>test_restaurant_bill_parser.py</code> using Hypothesis strategies (<code>st.text()</code>, <code>st.integers()</code>, <code>st.one_of()</code>, <code>st.sampled_from()</code>). When executed via <code>python -m pytest test_restaurant_bill_parser.py -v</code> on the unhardened module, Hypothesis rapidly identified <b>7 distinct critical failures</b> across all three functions.",
        body_style
    ))
    
    img2_path = os.path.join(ss_dir, "image2.png")
    if os.path.exists(img2_path):
        story.append(Image(img2_path, width=490, height=119))
        story.append(Paragraph("Figure 2 (SS2 - Part A): Verbose pytest output showing 7 failing tests on the unhardened module.", caption_style))

    img1_sub_path = os.path.join(ss_dir, "image1.png")
    if os.path.exists(img1_sub_path):
        story.append(Image(img1_sub_path, width=490, height=105))
        story.append(Paragraph("Figure 3 (SS2 - Part B): Short test summary confirming unhandled <code>AttributeError</code>, unhandled negative cases, and missing exceptions (7 failed, 8 passed in 6.89s).", caption_style))
    
    story.append(PageBreak())

    # Step 5 / SS3
    story.append(Paragraph("<b>Step 5: Execution of Fixed & Hardened Module (Screenshot SS3)</b>", h2_style))
    story.append(Paragraph(
        "The application script was refactored with comprehensive defensive validation: type enforcement via <code>isinstance(..., str)</code>, whitespace/marker stripping checks, empty string rejections, non-negative integer assertions, and split token format verification. Running <code>python restaurant_bill_parser.py</code> confirmed that the application preserves full functionality on valid user inputs while gaining resilience against corrupt inputs.",
        body_style
    ))
    img3_path = os.path.join(ss_dir, "image3.png")
    if os.path.exists(img3_path):
        story.append(Image(img3_path, width=490, height=141))
        story.append(Paragraph("Figure 4 (SS3): Interactive run of the hardened <code>restaurant_bill_parser.py</code> demonstrating normal operation.", caption_style))
    story.append(Spacer(1, 4))

    # Step 6 / SS4
    story.append(Paragraph("<b>Step 6: Re-Running Hypothesis Fuzz Suite on Fixed Module (Screenshot SS4)</b>", h2_style))
    story.append(Paragraph(
        "The Hypothesis test suite was re-run against the hardened module using <code>python -m pytest test_restaurant_bill_parser.py -v</code>. All <b>15 property-based tests passed completely</b> (100% pass rate in 1.70 seconds), confirming that the module now handles all arbitrary, extreme, and malformed inputs deterministically without crashing.",
        body_style
    ))
    img4_path = os.path.join(ss_dir, "image4.png")
    if os.path.exists(img4_path):
        story.append(Image(img4_path, width=490, height=215))
        story.append(Paragraph("Figure 5 (SS4): Pytest execution report confirming all 15 property-based fuzz tests PASSED on the fixed module.", caption_style))
    story.append(Spacer(1, 8))

    # Page Break for Analysis & Reflection
    story.append(PageBreak())

    # Section 4: Bug Analysis Table
    story.append(Paragraph("4. Vulnerability & Edge Case Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3B82F6'), spaceBefore=1, spaceAfter=5))
    story.append(Paragraph(
        "Fuzzing uncovered 6 fundamental vulnerabilities in the unhardened codebase. Below is a structured analysis of each bug, its root cause, the minimal failing counterexample found by Hypothesis shrinking, and the defensive fix applied:",
        body_style
    ))

    bug_table_data = [
        [
            Paragraph("<b>Target Function</b>", body_style),
            Paragraph("<b>Vulnerability Uncovered</b>", body_style),
            Paragraph("<b>Shrunk Counterexample</b>", body_style),
            Paragraph("<b>Defensive Fix Implemented</b>", body_style)
        ],
        [
            Paragraph("<code>clean_dish_name</code>", body_style),
            Paragraph("Unhandled <code>NoneType</code> or non-string object caused <code>AttributeError: 'NoneType' object has no attribute 'strip'</code>.", body_style),
            Paragraph("<code>name=None</code>", body_style),
            Paragraph("Added <code>if not isinstance(name, str): raise TypeError(...)</code>", body_style)
        ],
        [
            Paragraph("<code>clean_dish_name</code>", body_style),
            Paragraph("Empty string or strings containing only marker characters (<code>*</code>, <code>#</code>, <code>~</code>) returned empty string instead of rejecting.", body_style),
            Paragraph("<code>name=''</code><br/><code>name='*#~'</code>", body_style),
            Paragraph("Checked <code>if not name: raise ValueError('Dish name cannot be empty')</code> after sanitization.", body_style)
        ],
        [
            Paragraph("<code>parse_item_prices</code>", body_style),
            Paragraph("Missing type check crashed on non-string input. Negative numbers were parsed without raising errors.", body_style),
            Paragraph("<code>text=None</code><br/><code>text='-1'</code>", body_style),
            Paragraph("Enforced string type check; verified <code>if value &lt; 0: raise ValueError(...)</code>.", body_style)
        ],
        [
            Paragraph("<code>parse_item_prices</code>", body_style),
            Paragraph("Malformed lists with adjacent commas or trailing commas caused <code>ValueError: invalid literal for int() with base 10: ''</code>.", body_style),
            Paragraph("<code>text='100,,200'</code>", body_style),
            Paragraph("Trimmed whitespace and explicitly checked <code>if not price: raise ValueError(...)</code>.", body_style)
        ],
        [
            Paragraph("<code>split_amount</code>", body_style),
            Paragraph("Zero diners caused unhandled <code>ZeroDivisionError</code>; negative diners or bill totals resulted in mathematically nonsensical splits.", body_style),
            Paragraph("<code>text='1200/0'</code><br/><code>text='-500/2'</code>", body_style),
            Paragraph("Validated <code>total &gt;= 0</code> and strictly required <code>people &gt; 0</code>; raised <code>ValueError</code>.", body_style)
        ],
        [
            Paragraph("<code>split_amount</code>", body_style),
            Paragraph("Missing or multiple slash delimiters caused <code>ValueError: not enough values to unpack</code>.", body_style),
            Paragraph("<code>text='1200/4/2'</code><br/><code>text='1200'</code>", body_style),
            Paragraph("Verified <code>len(parts) == 2</code> before attempting integer conversion.", body_style)
        ]
    ]
    bug_table = Table(bug_table_data, colWidths=[90, 150, 95, 188])
    bug_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(bug_table)
    story.append(Spacer(1, 8))

    # Section 5: Answers to Reflection Questions
    story.append(Paragraph("5. Answers to Lab Reflection Questions", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3B82F6'), spaceBefore=1, spaceAfter=5))
    
    q1 = "<b>Q1: What are the primary differences between traditional example-based unit testing and property-based fuzz testing?</b>"
    a1 = "<i>Answer:</i> Traditional unit testing relies on specific hardcoded input/output pairs designed according to the engineer's assumptions. It verifies that known cases work as expected. In contrast, property-based fuzz testing specifies general invariants (e.g., 'the function must never crash regardless of input', 'the output list must have non-negative integers') and generates hundreds of pseudo-random, edge-case, and boundary inputs. It excels at discovering 'unknown unknowns' that human test authors rarely consider, such as empty delimiters, extreme numeric boundaries, and non-ASCII character inputs."
    story.append(Paragraph(q1, body_style))
    story.append(Paragraph(a1, body_style))
    story.append(Spacer(1, 3))

    q2 = "<b>Q2: How does Hypothesis test-case minimization (shrinking) assist developers in debugging?</b>"
    a2 = "<i>Answer:</i> When a randomized test fails on an unwieldy input (e.g., an 80-character string with complex Unicode characters), finding the root cause manually is difficult. Hypothesis automatically executes a shrinking algorithm, systematically reducing the input complexity (removing characters, zeroing numbers) while re-evaluating the test until it identifies the minimal reproducible counterexample (e.g., shrinking to <code>None</code>, <code>''</code>, or <code>0</code>). This directly isolates the exact boundary condition causing the crash."
    story.append(Paragraph(q2, body_style))
    story.append(Paragraph(a2, body_style))
    story.append(Spacer(1, 3))

    q3 = "<b>Q3: Why is defensive programming essential for software security and system reliability?</b>"
    a3 = "<i>Answer:</i> In production systems, unexpected or malformed user inputs can lead to uncaught exceptions, Denial of Service (DoS) crashes, or security exploits (such as buffer corruption or injection attacks). By adopting defensive programming—explicitly checking input data types, stripping and validating strings, bounding numeric ranges, and handling exceptional cases gracefully—the application establishes robust failure boundaries and prevents application downtime."
    story.append(Paragraph(q3, body_style))
    story.append(Paragraph(a3, body_style))

    # Page Break for Code Appendices
    story.append(PageBreak())

    # Section 6: Source Code
    story.append(Paragraph("6. Source Code Appendices", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3B82F6'), spaceBefore=1, spaceAfter=5))
    
    story.append(Paragraph("<b>Appendix A: Fixed Application Script (<code>restaurant_bill_parser.py</code> / <code>processor.py</code>)</b>", h2_style))
    story.append(Paragraph("The complete hardened application module code is divided into functional components below:", body_style))

    dish_func = """def clean_dish_name(name):
    \"\"\"Removes chef's-special markers and title-cases the dish name. Rejects invalid types and empty dish names.\"\"\"
    if not isinstance(name, str):
        raise TypeError("Dish name must be a string")
    name = name.strip()
    for ch in ['*', '#', '~']:
        name = name.replace(ch, '')
    name = name.strip()
    if not name:
        raise ValueError("Dish name cannot be empty")
    return name.title()"""

    price_func = """def parse_item_prices(text):
    \"\"\"Parses comma-separated prices into a list of non-negative integers.\"\"\"
    if not isinstance(text, str):
        raise TypeError("Prices must be provided as a string")
    if not text.strip():
        raise ValueError("Price list cannot be empty")
    prices = []
    for price in text.split(','):
        price = price.strip()
        if not price:
            raise ValueError("Price cannot be empty")
        try:
            value = int(price)
        except ValueError:
            raise ValueError("Prices must be valid whole numbers")
        if value < 0:
            raise ValueError("Prices cannot be negative")
        prices.append(value)
    return prices"""

    split_func = """def split_amount(text):
    \"\"\"Splits TOTAL/PEOPLE and calculates each person's share.\"\"\"
    if not isinstance(text, str):
        raise TypeError("Bill details must be a string")
    parts = text.split('/')
    if len(parts) != 2:
        raise ValueError("Format must be TOTAL/PEOPLE")
    try:
        total = int(parts[0].strip())
        people = int(parts[1].strip())
    except ValueError:
        raise ValueError("Total and people must be whole numbers")
    if total < 0:
        raise ValueError("Total cannot be negative")
    if people <= 0:
        raise ValueError("Number of people must be positive")
    return total // people"""

    main_func = """def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    print("Dish name:", clean_dish_name(value))

    print("\\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    print("Item prices:", parse_item_prices(value))

    print("\\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    print("Each person pays:", split_amount(value))

if __name__ == "__main__":
    main()"""

    story.append(Paragraph("<b>A.1 Dish Name Sanitizer Function:</b>", h3_style))
    story.append(Paragraph(format_code(dish_func), code_block_style))

    story.append(Paragraph("<b>A.2 Price List Parser Function:</b>", h3_style))
    story.append(Paragraph(format_code(price_func), code_block_style))

    story.append(Paragraph("<b>A.3 Bill Split Calculation Function:</b>", h3_style))
    story.append(Paragraph(format_code(split_func), code_block_style))

    story.append(Paragraph("<b>A.4 Main Execution Routine:</b>", h3_style))
    story.append(Paragraph(format_code(main_func), code_block_style))

    story.append(PageBreak())

    # Appendix B: Test Suite
    story.append(Paragraph("<b>Appendix B: Updated Hypothesis Test Suite (<code>test_restaurant_bill_parser.py</code> / <code>test_processor.py</code>)</b>", h2_style))
    story.append(Paragraph("The complete 15 property-based fuzz tests developed using Hypothesis are partitioned by test target below:", body_style))

    test_imports = """import pytest
from hypothesis import given, strategies as st
from restaurant_bill_parser import clean_dish_name, parse_item_prices, split_amount"""
    story.append(Paragraph("<b>B.1 Test Suite Setup & Module Imports:</b>", h3_style))
    story.append(Paragraph(format_code(test_imports), code_block_style))

    test_dish = """# TEST 1: clean_dish_name()
@given(st.text(min_size=1).filter(lambda s: bool(s.strip().replace('*', '').replace('#', '').replace('~', '').strip())))
def test_clean_dish_name_removes_special_characters(name):
    result = clean_dish_name(name)
    expected = name.strip()
    for ch in ['*', '#', '~']:
        expected = expected.replace(ch, '')
    assert result == expected.title()

@given(st.one_of(st.none(), st.integers(), st.floats(), st.lists(st.integers())))
def test_clean_dish_name_rejects_invalid_types(name):
    with pytest.raises(TypeError):
        clean_dish_name(name)

@given(st.sampled_from(["", " ", "*", "#", "~", "*#~"]))
def test_clean_dish_name_rejects_empty_names(name):
    with pytest.raises(ValueError):
        clean_dish_name(name)"""
    story.append(Paragraph("<b>B.2 Property Tests for <code>clean_dish_name</code>:</b>", h3_style))
    story.append(Paragraph(format_code(test_dish), code_block_style))

    test_price = """# TEST 2: parse_item_prices()
@given(st.lists(st.integers(min_value=0, max_value=100000), min_size=1, max_size=20))
def test_parse_item_prices_valid_inputs(prices):
    text = ",".join(map(str, prices))
    assert parse_item_prices(text) == prices

@given(st.lists(st.integers(min_value=0, max_value=100000), min_size=1, max_size=10))
def test_parse_item_prices_handles_whitespace(prices):
    text = ", ".join(map(str, prices))
    assert parse_item_prices(text) == prices

@given(st.text().filter(lambda s: not s.strip().isdigit()))
def test_parse_item_prices_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_item_prices("100," + value)

@given(st.integers(max_value=-1))
def test_parse_item_prices_rejects_negative_prices(price):
    with pytest.raises(ValueError):
        parse_item_prices(str(price))

def test_parse_item_prices_rejects_empty_input():
    with pytest.raises(ValueError):
        parse_item_prices("")

def test_parse_item_prices_rejects_empty_elements():
    with pytest.raises(ValueError):
        parse_item_prices("100,,200")

def test_parse_item_prices_rejects_invalid_types():
    with pytest.raises(TypeError):
        parse_item_prices(None)"""
    story.append(Paragraph("<b>B.3 Property Tests for <code>parse_item_prices</code>:</b>", h3_style))
    story.append(Paragraph(format_code(test_price), code_block_style))

    test_split = """# TEST 3: split_amount()
@given(st.integers(min_value=0, max_value=1000000), st.integers(min_value=1, max_value=10000))
def test_split_amount_valid_inputs(total, people):
    text = f"{total}/{people}"
    assert split_amount(text) == total // people

@given(st.integers(max_value=-1))
def test_split_amount_rejects_negative_total(total):
    with pytest.raises(ValueError):
        split_amount(f"{total}/4")

@given(st.integers(max_value=0))
def test_split_amount_rejects_zero_or_negative_people(people):
    with pytest.raises(ValueError):
        split_amount(f"1200/{people}")

@given(st.sampled_from(["", "1200", "/4", "1200/", "1200/4/2", "abc/4", "1200/abc"]))
def test_split_amount_rejects_invalid_formats(text):
    with pytest.raises(ValueError):
        split_amount(text)

def test_split_amount_rejects_invalid_types():
    with pytest.raises(TypeError):
        split_amount(None)"""
    story.append(Paragraph("<b>B.4 Property Tests for <code>split_amount</code>:</b>", h3_style))
    story.append(Paragraph(format_code(test_split), code_block_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF at {filename} successfully.")

if __name__ == "__main__":
    out_dir = r"C:\Users\ik090\.gemini\antigravity\brain\dc28f6ae-fdfb-470b-8382-eceb4fa72dc8"
    out_file = os.path.join(out_dir, "PES2UG25CS809_IbrahimKhaleel_LAB7.pdf")
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    build_pdf(out_file)
