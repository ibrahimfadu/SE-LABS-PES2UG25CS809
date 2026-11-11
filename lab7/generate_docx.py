import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_docx(output_path):
    doc = Document()

    # Set Margins to 0.7 inches
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Title
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_title = title_p.add_run("LAB 7: FUZZ TESTING FOR INPUT VALIDATION BUGS")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 58, 138)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(12)
    run_sub = sub_p.add_run("Software Engineering Lab Report — Automated Property-Based Testing with Hypothesis")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(37, 99, 235)

    # Metadata Table
    table = doc.add_table(rows=3, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Student Name: Ibrahim Khaleel", "Course: Software Engineering Lab (SE)"),
        ("SRN: PES2UG25CS809", "Topic: Property-Based Fuzz Testing (Hypothesis)"),
        ("Section / Sem: Section D, 5th Sem", "Module Assigned: L6_L7_58 (Restaurant Bill Parser)")
    ]
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.text = meta_info[r_idx][c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 1. Objective
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(10)
    h1.paragraph_format.space_after = Pt(4)
    r1 = h1.add_run("1. Objective & Learning Outcomes")
    r1.font.name = "Calibri"
    r1.font.size = Pt(13)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(30, 58, 138)

    p_obj = doc.add_paragraph()
    p_obj.paragraph_format.space_after = Pt(4)
    r_obj = p_obj.add_run("Lab Objective: To explore fuzz testing as an automated security and quality assurance technique by discovering, analyzing, and resolving input validation vulnerabilities in a Python application module using the Hypothesis property-based testing framework.")
    r_obj.font.name = "Calibri"
    r_obj.font.size = Pt(10)

    bullets = [
        "Understand Fuzzing Methodology: Comprehend how feeding pseudo-random, malformed, and non-canonical data uncovers unforeseen edge cases and crash conditions.",
        "Property-Based Testing with Hypothesis: Formulate behavioral invariants and domain constraints using @given decorators and strategy generators (st.text(), st.integers(), st.one_of()).",
        "Test-Case Shrinking Analysis: Leverage Hypothesis's automated shrinking engine to isolate minimal reproducible counterexamples for each failure.",
        "Defensive Programming: Implement defensive guards (type validation, boundaries, sanitization, zero-division guards) ensuring the module never experiences unhandled exceptions."
    ]
    for b in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r = bp.add_run(b)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)

    # 2. Screenshots
    doc.add_page_break()
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(4)
    r2 = h2.add_run("2. Laboratory Execution Screenshots")
    r2.font.name = "Calibri"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(30, 58, 138)

    ss_dir = r"L6_L7_58_restaurant_bill\screenshort"

    # SS1
    p_ss1 = doc.add_paragraph()
    r_ss1 = p_ss1.add_run("Step 2 (SS1): Initial Execution of Buggy Module (restaurant_bill_parser.py)")
    r_ss1.font.name = "Calibri"
    r_ss1.font.size = Pt(11)
    r_ss1.font.bold = True
    r_ss1.font.color.rgb = RGBColor(37, 99, 235)

    img1 = os.path.join(ss_dir, "image.png")
    if os.path.exists(img1):
        doc.add_picture(img1, width=Inches(6.8))
        cap = doc.add_paragraph("Figure 1 (SS1): Baseline run of buggy restaurant_bill_parser.py on typical inputs.")
        cap.paragraph_format.space_after = Pt(10)
        cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.size = Pt(8.5)
        cap.runs[0].font.italic = True

    # SS2
    p_ss2 = doc.add_paragraph()
    r_ss2 = p_ss2.add_run("Step 3 & 4 (SS2): Hypothesis Fuzz Testing Exposing Application Bugs (7 Failed)")
    r_ss2.font.name = "Calibri"
    r_ss2.font.size = Pt(11)
    r_ss2.font.bold = True
    r_ss2.font.color.rgb = RGBColor(37, 99, 235)

    img2 = os.path.join(ss_dir, "image2.png")
    if os.path.exists(img2):
        doc.add_picture(img2, width=Inches(6.8))
        cap2 = doc.add_paragraph("Figure 2 (SS2 - Part A): Verbose pytest output showing 7 failing tests on the unhardened module.")
        cap2.paragraph_format.space_after = Pt(6)
        cap2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap2.runs[0].font.size = Pt(8.5)
        cap2.runs[0].font.italic = True

    img1_sub = os.path.join(ss_dir, "image1.png")
    if os.path.exists(img1_sub):
        doc.add_picture(img1_sub, width=Inches(6.8))
        cap3 = doc.add_paragraph("Figure 3 (SS2 - Part B): Short summary of unhandled exceptions (AttributeError, ZeroDivisionError).")
        cap3.paragraph_format.space_after = Pt(10)
        cap3.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap3.runs[0].font.size = Pt(8.5)
        cap3.runs[0].font.italic = True

    doc.add_page_break()

    # SS3
    p_ss3 = doc.add_paragraph()
    r_ss3 = p_ss3.add_run("Step 5 (SS3): Execution of Fixed & Hardened Module")
    r_ss3.font.name = "Calibri"
    r_ss3.font.size = Pt(11)
    r_ss3.font.bold = True
    r_ss3.font.color.rgb = RGBColor(37, 99, 235)

    img3 = os.path.join(ss_dir, "image3.png")
    if os.path.exists(img3):
        doc.add_picture(img3, width=Inches(6.8))
        cap4 = doc.add_paragraph("Figure 4 (SS3): Interactive run of the hardened restaurant_bill_parser.py.")
        cap4.paragraph_format.space_after = Pt(10)
        cap4.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap4.runs[0].font.size = Pt(8.5)
        cap4.runs[0].font.italic = True

    # SS4
    p_ss4 = doc.add_paragraph()
    r_ss4 = p_ss4.add_run("Step 6 (SS4): Re-Running Hypothesis Fuzz Suite on Fixed Module (15 Passed)")
    r_ss4.font.name = "Calibri"
    r_ss4.font.size = Pt(11)
    r_ss4.font.bold = True
    r_ss4.font.color.rgb = RGBColor(37, 99, 235)

    img4 = os.path.join(ss_dir, "image4.png")
    if os.path.exists(img4):
        doc.add_picture(img4, width=Inches(6.8))
        cap5 = doc.add_paragraph("Figure 5 (SS4): Pytest execution report confirming all 15 property-based fuzz tests PASSED on the fixed module.")
        cap5.paragraph_format.space_after = Pt(10)
        cap5.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap5.runs[0].font.size = Pt(8.5)
        cap5.runs[0].font.italic = True

    # 3. Bug Analysis
    doc.add_page_break()
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(4)
    r3 = h3.add_run("3. Vulnerability & Edge Case Analysis")
    r3.font.name = "Calibri"
    r3.font.size = Pt(13)
    r3.font.bold = True
    r3.font.color.rgb = RGBColor(30, 58, 138)

    bug_table = doc.add_table(rows=7, cols=4)
    bug_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Target Function", "Vulnerability Uncovered", "Shrunk Counterexample", "Defensive Fix Implemented"]
    for i, h in enumerate(headers):
        cell = bug_table.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, "EFF6FF")
        p = cell.paragraphs[0]
        p.runs[0].font.name = "Calibri"
        p.runs[0].font.size = Pt(9)
        p.runs[0].font.bold = True

    bug_data = [
        ("clean_dish_name", "Unhandled NoneType or non-string object caused AttributeError: 'NoneType' object has no attribute 'strip'.", "name=None", "Added if not isinstance(name, str): raise TypeError(...)"),
        ("clean_dish_name", "Empty string or strings containing only marker characters (*, #, ~) returned empty string instead of rejecting.", "name=''\nname='*#~'", "Checked if not name: raise ValueError('Dish name cannot be empty') after sanitization."),
        ("parse_item_prices", "Missing type check crashed on non-string input. Negative numbers were parsed without raising errors.", "text=None\ntext='-1'", "Enforced string type check; verified if value < 0: raise ValueError(...)."),
        ("parse_item_prices", "Malformed lists with adjacent commas or trailing commas caused ValueError: invalid literal for int() with base 10: ''.", "text='100,,200'", "Trimmed whitespace and explicitly checked if not price: raise ValueError(...)."),
        ("split_amount", "Zero diners caused unhandled ZeroDivisionError; negative diners or bill totals resulted in mathematically nonsensical splits.", "text='1200/0'\ntext='-500/2'", "Validated total >= 0 and strictly required people > 0; raised ValueError."),
        ("split_amount", "Missing or multiple slash delimiters caused ValueError: not enough values to unpack.", "text='1200/4/2'\ntext='1200'", "Verified len(parts) == 2 before attempting integer conversion.")
    ]

    for r_idx, b_row in enumerate(bug_data, start=1):
        for c_idx, text in enumerate(b_row):
            cell = bug_table.rows[r_idx].cells[c_idx]
            cell.text = text
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(8.5)
            set_cell_background(cell, "F8FAFC" if r_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, top=40, bottom=40, left=60, right=60)

    # 4. Reflection Questions
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(10)
    h4.paragraph_format.space_after = Pt(4)
    r4 = h4.add_run("4. Answers to Lab Reflection Questions")
    r4.font.name = "Calibri"
    r4.font.size = Pt(13)
    r4.font.bold = True
    r4.font.color.rgb = RGBColor(30, 58, 138)

    q_a = [
        ("Q1: What are the primary differences between traditional example-based unit testing and property-based fuzz testing?",
         "Answer: Traditional unit testing relies on specific hardcoded input/output pairs designed according to the engineer's assumptions. It verifies that known cases work as expected. In contrast, property-based fuzz testing specifies general invariants (e.g., 'the function must never crash regardless of input', 'the output list must have non-negative integers') and generates hundreds of pseudo-random, edge-case, and boundary inputs. It excels at discovering 'unknown unknowns' that human test authors rarely consider, such as empty delimiters, extreme numeric boundaries, and non-ASCII character inputs."),
        ("Q2: How does Hypothesis test-case minimization (shrinking) assist developers in debugging?",
         "Answer: When a randomized test fails on an unwieldy input (e.g., an 80-character string with complex Unicode characters), finding the root cause manually is difficult. Hypothesis automatically executes a shrinking algorithm, systematically reducing the input complexity (removing characters, zeroing numbers) while re-evaluating the test until it identifies the minimal reproducible counterexample (e.g., shrinking to None, '', or 0). This directly isolates the exact boundary condition causing the crash."),
        ("Q3: Why is defensive programming essential for software security and system reliability?",
         "Answer: In production systems, unexpected or malformed user inputs can lead to uncaught exceptions, Denial of Service (DoS) crashes, or security exploits (such as buffer corruption or injection attacks). By adopting defensive programming—explicitly checking input data types, stripping and validating strings, bounding numeric ranges, and handling exceptional cases gracefully—the application establishes robust failure boundaries and prevents application downtime.")
    ]

    for q, a in q_a:
        pq = doc.add_paragraph()
        pq.paragraph_format.space_before = Pt(4)
        pq.paragraph_format.space_after = Pt(1)
        rq = pq.add_run(q)
        rq.font.name = "Calibri"
        rq.font.size = Pt(10)
        rq.font.bold = True

        pa = doc.add_paragraph()
        pa.paragraph_format.space_before = Pt(0)
        pa.paragraph_format.space_after = Pt(4)
        ra = pa.add_run(a)
        ra.font.name = "Calibri"
        ra.font.size = Pt(9.5)
        ra.font.italic = True

    # 5. Code
    doc.add_page_break()
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(10)
    h5.paragraph_format.space_after = Pt(4)
    r5 = h5.add_run("5. Source Code")
    r5.font.name = "Calibri"
    r5.font.size = Pt(13)
    r5.font.bold = True
    r5.font.color.rgb = RGBColor(30, 58, 138)

    h_app = doc.add_paragraph()
    r_app = h_app.add_run("Appendix A: Fixed Application Script (restaurant_bill_parser.py / processor.py)")
    r_app.font.name = "Calibri"
    r_app.font.size = Pt(11)
    r_app.font.bold = True
    r_app.font.color.rgb = RGBColor(37, 99, 235)

    with open(r"L6_L7_58_restaurant_bill\LAB7\restaurant_bill_parser.py", "r", encoding="utf-8") as f:
        app_code = f.read()

    p_code1 = doc.add_paragraph()
    p_code1.paragraph_format.space_before = Pt(2)
    p_code1.paragraph_format.space_after = Pt(8)
    r_c1 = p_code1.add_run(app_code)
    r_c1.font.name = "Consolas"
    r_c1.font.size = Pt(8)

    doc.add_page_break()
    h_test = doc.add_paragraph()
    r_test = h_test.add_run("Appendix B: Updated Hypothesis Test Suite (test_restaurant_bill_parser.py / test_processor.py)")
    r_test.font.name = "Calibri"
    r_test.font.size = Pt(11)
    r_test.font.bold = True
    r_test.font.color.rgb = RGBColor(37, 99, 235)

    with open(r"L6_L7_58_restaurant_bill\LAB7\test_restaurant_bill_parser.py", "r", encoding="utf-8") as f:
        test_code = f.read()

    p_code2 = doc.add_paragraph()
    p_code2.paragraph_format.space_before = Pt(2)
    p_code2.paragraph_format.space_after = Pt(8)
    r_c2 = p_code2.add_run(test_code)
    r_c2.font.name = "Consolas"
    r_c2.font.size = Pt(8)

    doc.save(output_path)
    print(f"Generated DOCX at {output_path} successfully.")

if __name__ == "__main__":
    generate_docx(r"d:\CLG\SE\SE-LABS-PES2UG25CS809\lab7\PES2UG25CS809_IbrahimKhaleel_LAB7.docx")
    generate_docx(r"d:\CLG\SE\SE-LABS-PES2UG25CS809\lab7\PES2UG25CS809.docx")
    generate_docx(r"d:\CLG\SE\SE-LABS-PES2UG25CS809\lab7\L6_L7_58_restaurant_bill\LAB7\PES2UG25CS809_IbrahimKhaleel_LAB7.docx")
    generate_docx(r"d:\CLG\SE\SE-LABS-PES2UG25CS809\lab7\L6_L7_58_restaurant_bill\LAB7\PES2UG25CS809.docx")
