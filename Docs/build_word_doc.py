import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = docx.Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("ELEC281 Mini Challenge: Design Stage & Circuit Specification")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("Interactive Digital LED Hourglass with Accessibility & Dual-Sided Interface\nModule: ELEC281 - Applied Electronic Skills and Engineering Practice | Box 34")
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 1: Executive Summary & CDIO Alignment
    h1 = doc.add_heading("1. Executive Summary & CDIO Alignment", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    p = doc.add_paragraph(
        "This engineering design specification fulfills the Design Stage deliverable for the ELEC281 Mini Challenge (Digital Hourglass). "
        "The project transforms the traditional passive hourglass into a smart, accessible timer featuring: "
        "(1) A front visual display with sand particle physics simulated on two cascaded 8x8 LED matrices; "
        "(2) A rear 4-in-1 LED matrix displaying accurate numerical countdowns (MM:SS); "
        "(3) A 4x4 matrix keypad enabling custom user duration setting; "
        "(4) An auditory feedback loop powered by a passive buzzer, designed specifically for blind/visually-impaired users."
    )
    p.paragraph_format.space_after = Pt(8)

    # Section 2: Traceability & Consistency Verification
    h2 = doc.add_heading("2. Engineering Consistency & Traceability Matrix", level=1)
    h2.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    p_trace = doc.add_paragraph(
        "To guarantee 100% feasibility during the Implementation Stage, all hardware connections, software parameters, "
        "and architectural flows have been cross-verified against the operational source code (DigitalHourglass_Core.ino) "
        "and physical circuit schematics. Table 1 outlines this exact parity."
    )
    p_trace.paragraph_format.space_after = Pt(8)

    # Table 1: Consistency Matrix
    headers = ["System Function", "Hardware Component", "Arduino R4 Pin / Bus", "Code Identifier in .ino", "Validation Status"]
    table_data = [
        ["Visual Front (Top Sand)", "MAX7219 8x8 Matrix (#0)", "Pin 11 (DIN), 10 (CS), 13 (CLK)", "lc.setLed(0, ...), DIN_PIN=11", "Verified Match"],
        ["Visual Front (Bottom Sand)", "MAX7219 8x8 Matrix (#1)", "SPI Daisy-Chain (DOUT->DIN)", "lc.setLed(1, ...), NUM_MATRICES=6", "Verified Match"],
        ["Visual Rear (Digital MM:SS)", "MAX7219 4-in-1 Matrix (#2..5)", "SPI Daisy-Chain (DOUT->DIN)", "drawDigit(2..5, ...)", "Verified Match"],
        ["Tilt / Flip Sensing", "ICM20948 9DOF IMU", "I2C: SDA, SCL (3.3V Rail)", "icm.begin_I2C(), icm_accel->getEvent()", "Verified Match"],
        ["Auditory Accessibility", "Passive Buzzer Module", "Pin 9 (PWM) & GND", "BUZZER_PIN=9, tone(9, freq)", "Verified Match"],
        ["Keypad Row Pins (1..4)", "4x4 Membrane Keypad", "Pins 2, 3, 4, 5", "byte rowPins[4] = {2, 3, 4, 5}", "Verified Match"],
        ["Keypad Col Pins (5..8)", "4x4 Membrane Keypad", "Pins 6, 7, 8, 12", "byte colPins[4] = {6, 7, 8, 12}", "Verified Match"],
        ["Non-blocking Scheduler", "MCU Hardware Timer", "Internal System Millis", "currentMillis - lastDropTime >= dropInterval", "Verified Match"]
    ]

    table = doc.add_table(rows=len(table_data) + 1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    for i, title in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = title
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            r.font.size = Pt(9.5)

    # Data Rows
    for row_idx, row_content in enumerate(table_data):
        bg = "F4F6F9" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_content):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = cell_value
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            if col_idx in [2, 3, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.size = Pt(9)
                if col_idx == 4:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0x00, 0x88, 0x33)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 3: High-Level Hardware Flow Diagram
    h3 = doc.add_heading("3. High-Level Hardware Flow Diagram (Architecture)", level=1)
    h3.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    p_hw = doc.add_paragraph(
        "The hardware architecture separates the system into distinct functional subsystems: Power Distribution, "
        "Input/Sensing, Main Processing Unit, and Multi-modal Feedback. Crucially, the 5V power bus drives the high-current "
        "display matrices, while the 3.3V low-dropout regulator powers the sensitive inertial motion sensor."
    )
    p_hw.paragraph_format.space_after = Pt(8)

    # ASCII Box Architecture for Word Document
    hw_flow_box = doc.add_paragraph()
    hw_flow_box.paragraph_format.left_indent = Inches(0.2)
    hw_flow_box.paragraph_format.space_after = Pt(8)
    r_code = hw_flow_box.add_run(
        "+---------------------------------------------------------------------------------------------------+\n"
        "|                                    HIGH-LEVEL HARDWARE FLOW                                       |\n"
        "+---------------------------------------------------------------------------------------------------+\n"
        "|                                                                                                   |\n"
        "|  [POWER SOURCE] ===> USB 5V ===> Arduino Uno R4 WiFi (R7FA4M1 @ 48MHz)                            |\n"
        "|                                       |                  |                                        |\n"
        "|                                 (3.3V Rail)          (5V Rail)                                    |\n"
        "|                                       |                  |                                        |\n"
        "|  [INPUT SUBSYSTEM]                    v                  v            [OUTPUT SUBSYSTEM]          |\n"
        "|  +--------------------+       +---------------+   +---------------+   +------------------------+  |\n"
        "|  | 4x4 Keypad         | ====> | ICM20948 IMU  |   | Display Bus   |   | Front 2x MAX7219       |  |\n"
        "|  | (8x GPIO Pins 2..8)|       | (I2C: SDA/SCL)|   | (5V & GND)    |   | (Hourglass Sand Sim)   |  |\n"
        "|  +--------------------+       +---------------+   +---------------+   +------------------------+  |\n"
        "|            |                          |                  |                        ^               |\n"
        "|            | (Key Strobe)             | (Orientation)    | (Power)                | (SPI DOUT)    |\n"
        "|            v                          v                  v                        |               |\n"
        "|  +----------------------------------------------------------------+       +--------------------+  |\n"
        "|  |                     ARDUINO UNO R4 CENTRAL CONTROLLER          | ====> | Rear 4-in-1 Matrix |  |\n"
        "|  |           (Non-blocking FSM & Particle Physics Engine)         | (SPI) | (MM:SS Countdown)  |  |\n"
        "|  +----------------------------------------------------------------+       +--------------------+  |\n"
        "|                                       |                                                           |\n"
        "|                                (PWM Pin 9 @ tone)                                                 |\n"
        "|                                       v                                                           |\n"
        "|                               +-------------------+                                               |\n"
        "|                               |  Passive Buzzer   | (Blind-friendly auditory cues:                |\n"
        "|                               |  (Sound Feedback) |  Key clicks, 2x flip beep, alarm loop)        |\n"
        "|                               +-------------------+                                               |\n"
        "+---------------------------------------------------------------------------------------------------+"
    )
    r_code.font.name = 'Courier New'
    r_code.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 4: High-Level Software Flow Diagram
    h4 = doc.add_heading("4. High-Level Software Flow Diagram (FSM)", level=1)
    h4.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    p_sw = doc.add_paragraph(
        "The firmware is structured around an event-driven Finite State Machine (FSM). "
        "All timing loops operate on delta-time comparisons using millis(), completely avoiding delay() calls. "
        "This ensures that physical flips and keyboard interrupts are detected instantaneously regardless of display refresh cycles."
    )
    p_sw.paragraph_format.space_after = Pt(8)

    sw_flow_box = doc.add_paragraph()
    sw_flow_box.paragraph_format.left_indent = Inches(0.2)
    sw_flow_box.paragraph_format.space_after = Pt(8)
    r_sw = sw_flow_box.add_run(
        "+---------------------------------------------------------------------------------------------------+\n"
        "|                             FINITE STATE MACHINE (FSM) SOFTWARE FLOW                              |\n"
        "+---------------------------------------------------------------------------------------------------+\n"
        "|                                                                                                   |\n"
        "|  [1. BOOT_INIT]                                                                                   |\n"
        "|    - Initialize Serial (115200 bps), SPI Bus, I2C Bus, Keypad pins                               |\n"
        "|    - Wake and clear 6x MAX7219 matrices, play startup chime: tone(9, 1000, 200)                   |\n"
        "|    - Load default duration: totalTimeMs = 300,000ms (5 mins)                                      |\n"
        "|                           |                                                                       |\n"
        "|                           v                                                                       |\n"
        "|  [2. IDLE_READY / SETTING MODE]                                                                   |\n"
        "|    - Rear display shows configured time (default '0500')                                          |\n"
        "|    - If '0'-'9' pressed: Left-shift buffer, chirp tone(9, 2000, 50), update rear display          |\n"
        "|    - If 'C' pressed: Clear buffer to '0000', chirp tone(9, 1000, 100)                             |\n"
        "|    - If '#' pressed: Commit duration, calculate dropInterval = totalTimeMs / 64, tone(1500, 200) |\n"
        "|                           |                                                                       |\n"
        "|                           | (Event: IMU Accel Z Inversion > 5.0 or < -5.0 m/s^2)                 |\n"
        "|                           v                                                                       |\n"
        "|  [3. TIMING_ACTIVE (RUNNING)]                                                                     |\n"
        "|    - Play double confirmation beep: tone(1200Hz) x2 for accessible blind feedback                |\n"
        "|    - Map active top matrix (0 or 1) and bottom matrix                                             |\n"
        "|    - Every loop: non-blocking check:                                                              |\n"
        "|        * Check millis() - lastDropTime >= dropInterval: topSand--, bottomSand++                   |\n"
        "|        * Update rear display with remaining MM:SS                                                 |\n"
        "|        * Poll IMU: if user flips 180 deg mid-way -> reorient matrices, double-beep, restart timer |\n"
        "|                           |                                                                       |\n"
        "|                           | (Condition: elapsed >= totalTimeMs && topSand == 0)                   |\n"
        "|                           v                                                                       |\n"
        "|  [4. ALARM_DONE]                                                                                  |\n"
        "|    - Rear display locks to '0000'                                                                 |\n"
        "|    - Trigger non-blocking pulsed alarm: tone(9, 800) toggling every 500ms                        |\n"
        "|    - Await flip: Physical 180 deg inversion silences buzzer and seamlessly starts next timer cycle|\n"
        "+---------------------------------------------------------------------------------------------------+"
    )
    r_sw.font.name = 'Courier New'
    r_sw.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 5: Implementation Circuit Diagram Specification
    h5 = doc.add_heading("5. Implementation Stage: Circuit Schematic & Pin Assignment", level=1)
    h5.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    p_circ = doc.add_paragraph(
        "Below is the complete electrical interconnection schedule for constructing the prototype. "
        "Strict compliance with voltage rails (5V for displays, 3.3V for IMU) is mandatory to prevent component damage."
    )
    p_circ.paragraph_format.space_after = Pt(8)

    pin_headers = ["Subsystem", "Module Pin", "Arduino Uno R4 Pin", "Wire / Connection Type", "Electrical Note"]
    pin_data = [
        ["Power Bus", "VCC (Displays)", "5V", "Red Jumper Wire", "Direct 5V supply (high current)"],
        ["Power Bus", "GND (All)", "GND", "Black Jumper Wire", "Common ground reference"],
        ["Sensor Power", "VCC (IMU)", "3.3V", "Orange Jumper Wire", "Regulated 3.3V logic supply"],
        ["Visual SPI", "DIN (Matrix #0)", "Pin 11 (MOSI)", "Yellow Jumper Wire", "High-speed SPI Data"],
        ["Visual SPI", "CS (Matrix #0)", "Pin 10 (SS)", "Green Jumper Wire", "Active-Low Chip Select"],
        ["Visual SPI", "CLK (Matrix #0)", "Pin 13 (SCK)", "Blue Jumper Wire", "SPI Clock Line"],
        ["Display Cascade", "DOUT (#0) -> DIN (#1)", "Inter-matrix", "Direct Jumper", "SPI Cascade Stage 1"],
        ["Display Cascade", "DOUT (#1) -> DIN (#2)", "Inter-matrix", "Direct Jumper", "SPI Cascade Stage 2"],
        ["I2C IMU", "SDA (IMU)", "SDA (or A4)", "Purple Jumper Wire", "I2C Serial Data (pullup)"],
        ["I2C IMU", "SCL (IMU)", "SCL (or A5)", "White Jumper Wire", "I2C Serial Clock"],
        ["Auditory", "SIG (Buzzer)", "Pin 9 (PWM)", "Gray Jumper Wire", "Square wave audio signal"],
        ["Keypad Rows", "Pins 1..4", "Pins 2, 3, 4, 5", "Ribbon Cable Left", "Internal pullup scanned"],
        ["Keypad Cols", "Pins 5..8", "Pins 6, 7, 8, 12", "Ribbon Cable Right", "Strobe outputs"]
    ]

    t_pin = doc.add_table(rows=len(pin_data) + 1, cols=5)
    t_pin.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_pin.autofit = False

    for i, title in enumerate(pin_headers):
        cell = t_pin.cell(0, i)
        cell.text = title
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            r.font.size = Pt(9.5)

    for row_idx, row_content in enumerate(pin_data):
        bg = "F4F6F9" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_content):
            cell = t_pin.cell(row_idx + 1, col_idx)
            cell.text = cell_value
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
            p = cell.paragraphs[0]
            if col_idx in [1, 2]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # Conclusion Sign-off
    p_sign = doc.add_paragraph()
    p_sign.add_run("Design Stage Sign-off: ").font.bold = True
    p_sign.add_run("Hardware, software, and circuit specifications are validated and ready for laboratory prototype assembly.\nBox 34 Project Team - ELEC281")
    p_sign.paragraph_format.space_after = Pt(12)

    output_path = r"c:\Users\94632\Desktop\hourglass\Docs\ELEC281_Design_Stage_Report_EN.docx"
    doc.save(output_path)
    print(f"Word document saved successfully to {output_path}")

if __name__ == "__main__":
    create_report()
