# resume1.py (ATS-friendly content) — single-page tweaks
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import Flowable, KeepTogether
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
import os

# Pillow for image repair
try:
    from PIL import Image as PILImage, UnidentifiedImageError
except Exception as e:
    raise RuntimeError("Pillow is required. Install with: pip3 install Pillow") from e

# ---------- Image repair helper ----------
def repair_image_if_needed(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with PILImage.open(path) as im:
            im.load()
        return path
    except (UnidentifiedImageError, OSError) as e:
        print("Image appears broken, attempting repair:", path, "->", repr(e))
        try:
            with PILImage.open(path) as im:
                if im.mode in ("RGBA", "LA"):
                    cleaned = im.convert("RGBA")
                else:
                    cleaned = im.convert("RGB")
                fixed_path = os.path.splitext(path)[0] + "_fixed.png"
                cleaned.save(fixed_path, format="PNG")
                print("Saved repaired copy to:", fixed_path)
                return fixed_path
        except Exception as e2:
            print("Automatic repair failed for", path, "->", repr(e2))
            return None

# ---------- Skills badge flowable (unchanged) ----------
class SkillsBlockA(Flowable):
    def __init__(self, skills, max_width, font_name="Helvetica", font_size=12.1,
                 padding_x=10, padding_y=5, gap_x=8, gap_y=8, bg_color=colors.HexColor("#B0B4BB")):
        super().__init__()
        self.skills = skills
        self.max_width = max_width
        self.font_name = font_name
        self.font_size = font_size
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.gap_x = gap_x
        self.gap_y = gap_y
        self.bg_color = bg_color
        self.text_color = colors.white
        self.lines = []
        self.total_height = 0

    def wrap(self, availWidth, availHeight):
        self.lines = []
        line = []
        line_width = 0
        line_height = 0
        self.total_height = 0
        for skill in self.skills:
            text_w = stringWidth(skill, self.font_name, self.font_size)
            w = text_w + 2 * self.padding_x
            h = self.font_size + 2 * self.padding_y

            if line and (line_width + w > self.max_width):
                self.lines.append((line, line_height))
                self.total_height += line_height + self.gap_y
                line = []
                line_width = 0
                line_height = 0

            line.append((skill, w, h))
            line_width += w + self.gap_x
            line_height = max(line_height, h)

        if line:
            self.lines.append((line, line_height))
            self.total_height += line_height

        return (self.max_width, self.total_height + 4)

    def draw(self):
        y_top = self.total_height
        for (line, lh) in self.lines:
            x = 0
            for (skill, w, h) in line:
                self.canv.setFillColor(self.bg_color)
                radius = min(10, h/2)
                self.canv.roundRect(x, y_top - h, w, h, radius=radius, fill=1, stroke=0)
                self.canv.setFillColor(self.text_color)
                self.canv.setFont(self.font_name, self.font_size)
                text_x = x + self.padding_x
                text_y = y_top - h + self.padding_y + (self.font_size * 0.2)
                self.canv.drawString(text_x, text_y, skill)
                x += w + self.gap_x
            y_top -= lh + self.gap_y

# ---------- PDF Setup ----------
doc = BaseDocTemplate("resume_optionA.pdf", pagesize=A4,
                      leftMargin=0.8*cm, rightMargin=0.8*cm,
                      topMargin=0.8*cm, bottomMargin=0.8*cm)
width, height = A4

# Colors & styles
dark_blue = colors.HexColor("#2E4053")
light_blue = colors.HexColor("#D6EAF8")
accent_blue = colors.HexColor("#2874A6")
white = colors.white
gray = colors.HexColor("#555555")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Name", fontSize=26.62, textColor=white, leading=26*1.21, spaceAfter=6, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="Role", fontSize=21.78, textColor=light_blue, leading=14*1.21, spaceAfter=6))
styles.add(ParagraphStyle(name="HeaderText", fontSize=10.89, textColor=white, leading=12*1.21))
styles.add(ParagraphStyle(name="Heading", fontSize=15.73, textColor=accent_blue, leading=16*1.21, spaceAfter=4, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="SubHeading", fontSize=12.1, textColor=gray, leading=13*1.21, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="Body", fontSize=10.89, textColor=colors.black, leading=12*1.21))
styles.add(ParagraphStyle(name="MyItalic", fontSize=10.89, textColor=accent_blue, leading=11*1.21, fontName="Helvetica-Oblique"))

# ---------- Section heading helper ----------
_section_initials = {
    "EDUCATION": "E",
    "WORK EXPERIENCE": "W",
    "SKILLS": "S",
    "PERSONAL PROJECTS": "P",
    "CERTIFICATES": "C",
    "LANGUAGES": "L",
    "INTERESTS": "I",
}

from reportlab.platypus import Table, TableStyle

def section_heading(title, icon_path=None, icon_size=16, heading_style=None):
    if heading_style is None:
        heading_style = styles["Heading"]

    img_cell = None
    if icon_path:
        usable = repair_image_if_needed(icon_path)
        if usable:
            try:
                img_cell = Image(usable, width=icon_size, height=icon_size)
            except Exception as e:
                print("ICON LOAD ERROR (when creating Image flowable):", usable, "->", repr(e))
                img_cell = None
        else:
            print("ICON NOT FOUND / UNUSABLE:", icon_path)

    if img_cell is None:
        initial_key = title.replace(" ", "_").upper()
        initial = _section_initials.get(initial_key, title[:1].upper())
        from reportlab.lib.styles import ParagraphStyle
        badge_style = ParagraphStyle(name="badge", fontName="Helvetica-Bold", fontSize=max(8, icon_size-6),
                                     alignment=1, textColor=colors.white, leading=icon_size-2)
        badge_para = Paragraph(initial, badge_style)
        badge_tbl = Table([[badge_para]], colWidths=[icon_size], rowHeights=[icon_size])
        badge_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), colors.HexColor("#2874A6")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("INNERGRID", (0,0), (-1,-1), 0, colors.white),
            ("BOX", (0,0), (-1,-1), 0, colors.white),
        ]))
        img_cell = badge_tbl

    para = Paragraph(title, heading_style)
    tbl = Table([[img_cell, para]], colWidths=[icon_size + 6, None])
    tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('RIGHTPADDING', (0,0), (0,0), 6),
        ('LEFTPADDING', (1,0), (1,0), 0),
        ('RIGHTPADDING', (1,0), (1,0), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    return tbl

# ---------- icon filenames ----------
icon_folder = "."
_raw_icons = {
    "EDUCATION": os.path.join(icon_folder, "icons8-graduation-cap-48.png"),
    "WORK EXPERIENCE": os.path.join(icon_folder, "icons8-briefcase-24.png"),
    "SKILLS": os.path.join(icon_folder, "icons8-personal-hotspot-24.png"),
    "PERSONAL PROJECTS": os.path.join(icon_folder, "icons8-personal-hotspot-24.png"),
    "CERTIFICATES": os.path.join(icon_folder, "icons8-certificate-48.png"),
    "LANGUAGES": os.path.join(icon_folder, "icons8-language-32.png"),
    "INTERESTS": os.path.join(icon_folder, "icons8-field-hockey-30.png"),
}

icons = {}
for k, p in _raw_icons.items():
    usable = repair_image_if_needed(p)
    icons[k] = usable if usable else p

def draw_header(canvas, doc):
    canvas.saveState()

    # smaller blue header (reduced from 160 → 120)
    header_h = 140
    canvas.setFillColor(dark_blue)
    canvas.rect(0, height - header_h, width, header_h, stroke=0, fill=1)

    # name & role (shifted up to match new header size)
    x_left = 20
    y_top = height - 30   # moved up (was -40)
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(x_left, y_top, "Arjun Singh")

    # role (moved closer to name)
    # canvas.setFont("Helvetica", 14)
    # canvas.setFillColor(light_blue)
    # canvas.drawString(x_left, y_top - 20, "")

    # summary text start position (moved up)
    summary_text = (
    "Fresher Python Developer with an M.Sc. in Information Technology and a strong foundation in Python, FastAPI, MySQL, and backend development. Built academic and "
    "personal projects involving REST APIs, CRUD operations, and database integration. Seeking an entry-level Python Developer role to apply and expand technical skills."
    )
    max_width = width / 2 - 60
    words = summary_text.split(" ")
    line, lines = "", []
    for word in words:
        test = (line + " " + word).strip()
        if stringWidth(test, "Helvetica", 9) < max_width:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    text_y = y_top - 26  # moved up a bit
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(white)
    for l in lines:
        canvas.drawString(x_left, text_y, l)
        text_y -= 12

    # contact icons (shifted up to match header height)
        # contact icons and text (flush-right)
    font_name = "Helvetica"
    font_size = 9
    canvas.setFont(font_name, font_size)
    canvas.setFillColor(white)

    contact_texts = [
        "askumpawat9351@gmail.com",
        "9351134011",
        "Udaipur, Rajasthan, India",
        "linkedin.com/in/rarjun07",
        "github.com/rarjun07"
    ]

    contact_icons_raw = [
        os.path.join(icon_folder, "icons8-email-24.png"),
        os.path.join(icon_folder, "icons8-phone-30.png"),
        os.path.join(icon_folder, "icons8-location-24.png"),
        os.path.join(icon_folder, "icons8-linkedin-30.png"),
        os.path.join(icon_folder, "icons8-github-30.png"),
    ]

    contact_icons = [repair_image_if_needed(p) or p for p in contact_icons_raw]

    # --- IMPORTANT: define icon_size BEFORE using it ---
    icon_size = 14
    gap_between_icon_and_text = 6
    right_margin = doc.rightMargin or (0.8 * cm)
    icon_x = width - right_margin - icon_size - 6
    right_text_x = icon_x - gap_between_icon_and_text
    line_height = 14

    y = height - 35

    for idx, text in enumerate(contact_texts):

        # draw text baseline
        canvas.drawRightString(right_text_x, y, text)

        # get ascent/descent for vertical centering
        ascent = pdfmetrics.getAscent(font_name) * font_size / 1000.0
        descent = pdfmetrics.getDescent(font_name) * font_size / 1000.0

        # compute visual text center
        text_center_y = y + (ascent + descent) / 2.0

        # compute correct icon Y
        icon_y = text_center_y - (icon_size / 2.0)

        icon_path = contact_icons[idx]
        if icon_path and os.path.exists(icon_path):
            try:
                img = ImageReader(icon_path)
                canvas.drawImage(
                    img, icon_x, icon_y,
                    width=icon_size, height=icon_size,
                    mask='auto', preserveAspectRatio=True, anchor='c'
                )
            except:
                # fallback placeholder if icon fails
                canvas.setFillColor(colors.HexColor("#444444"))
                canvas.rect(icon_x, icon_y, icon_size, icon_size, fill=1, stroke=0)
                canvas.setFillColor(white)

        y -= line_height



    canvas.restoreState()


# ---------- Frames & Template ----------
frame_left = Frame(doc.leftMargin - 10, doc.bottomMargin, width/2 - 1*cm, height - 180, id='left')
frame_right = Frame(width/2 + 0.3*cm, doc.bottomMargin, width/2 - 1*cm, height - 180, id='right')
template = PageTemplate(id='TwoCol', frames=[frame_left, frame_right], onPage=draw_header)
doc.addPageTemplates([template])

# ---------- Build content ----------
elements = []

# LEFT column
elements.append(section_heading("EDUCATION", icons.get("EDUCATION")))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Master of Science (M.Sc) — Information Technology</b><br/>Mohanlal Sukhadia University<br/><font color='#2874A6'>12/2023 - 11/2025</font>", styles["Body"]))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Bachelor of Science (B.Sc) — PCM</b><br/>Mohanlal Sukhadia University<br/><font color='#2874A6'>07/2020 - 08/2023</font>", styles["Body"]))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Senior Secondary — Science (PCM)</b><br/>Board of Secondary Education, Rajasthan<br/><font color='#2874A6'>07/2018 - 05/2019</font>", styles["Body"]))
elements.append(Spacer(1, 12))

elements.append(section_heading("WORK EXPERIENCE", icons.get("WORK EXPERIENCE")))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Intern — iOS Developer</b><br/>MLSU Career Incubation Center & Technical Solutions Hub (RUSA Project)<br/><font color='#2874A6'>06/2025 - 08/2025</font>", styles["Body"]))
elements.append(Paragraph(
    "<br/>• Developed and maintained SwiftUI applications using MVVM architecture and reusable components.<br/>"
    "• Integrated Firebase Firestore, async/await, and QR/ISBN scanning to enhance application functionality.<br/>"
    "• Collaborated with mentors to test, debug, and deliver stable mobile application features.<br/>",
    styles["Body"]
))

# smaller spacer to reclaim vertical space
elements.append(Spacer(1, 8))

# ========== SKILLS BLOCK (unchanged content, tighter chips) ==========
right_col_width = width/2 - 1*cm
inner_max = right_col_width - 10

elements.append(section_heading("SKILLS", icons.get("SKILLS")))
elements.append(Spacer(1, 6))
elements.append(Paragraph("<b>Programming Languages:</b>", styles["Body"]))
elements.append(Spacer(1, 3))
prog_langs = ["Python", "MySQL", "Swift", "SwiftUI", "HTML", "CSS", "JavaScript", "Java",]

elements.append(SkillsBlockA(prog_langs, max_width=inner_max,
                             font_size=8.2, padding_x=8, padding_y=3, gap_x=8, gap_y=6,
                             bg_color=colors.HexColor("#BFC4C9")))
elements.append(Spacer(1, 6))

elements.append(Paragraph("<b>Frameworks &amp; Tools:</b>", styles["Body"]))
elements.append(Spacer(1, 3))
fw_tools = ["Xcode", "FastAPI", "Firebase", "Supabase", "MVVM"]
elements.append(SkillsBlockA(fw_tools, max_width=inner_max,
                             font_size=8.2, padding_x=8, padding_y=3, gap_x=8, gap_y=6,
                             bg_color=colors.HexColor("#BFC4C9")))
elements.append(Spacer(1, 6))

elements.append(Paragraph("<b>Databases:</b>", styles["Body"]))
elements.append(Spacer(1, 3))
db_skills = ["MySQL", "SQL Server", "Firestore", "Supabase Database"]
elements.append(SkillsBlockA(db_skills, max_width=inner_max,
                             font_size=8.2, padding_x=8, padding_y=3, gap_x=8, gap_y=6,
                             bg_color=colors.HexColor("#BFC4C9")))
elements.append(Spacer(1, 6))

elements.append(Paragraph("<b>Core CS:</b>", styles["Body"]))
elements.append(Spacer(1, 3))
core_cs = ["OOP", "CRUD Operations", "API Development", "Database Design", "Data Structures & Algorithms"]
elements.append(SkillsBlockA(core_cs, max_width=inner_max,
                             font_size=8.2, padding_x=8, padding_y=3, gap_x=8, gap_y=6,
                             bg_color=colors.HexColor("#BFC4C9")))
elements.append(Spacer(1, 10))
# ========== END SKILLS BLOCK ==========

# RIGHT column continues - PROJECTS

elements.append(section_heading("PERSONAL PROJECTS", icons.get("PERSONAL PROJECTS")))
elements.append(Spacer(1, 6))


# Student Management API
elements.append(Paragraph(
    "<b>Project 1: Student Management API | FastAPI, SQLAlchemy, SQLite</b>",
    styles["SubHeading"]
))
elements.append(Paragraph(
    "• Built a RESTful API using FastAPI for managing student records.<br/>"
    "• Implemented CRUD operations (Create, Read, Update, Delete).<br/>"
    "• Used SQLAlchemy ORM for database interactions.<br/>"
    "• Created API endpoints for adding, updating, retrieving, and deleting student data.<br/>"
    "• Used Pydantic models for request validation and response serialization.",
    styles["Body"]
))
elements.append(Spacer(1, 8))

# MotoCare
elements.append(Paragraph(
    "<b>Project 2: MotoCare – Smart Vehicle Service System | SwiftUI, Firebase, Supabase</b>",
    styles["SubHeading"]
))
elements.append(Paragraph(
    "• Developed a vehicle service management app with service booking, maintenance tracking, and real-time data synchronization using SwiftUI, Firebase, and Supabase.",
    styles["Body"]
))
elements.append(Spacer(1, 8))


# CERTIFICATES
elements.append(section_heading("CERTIFICATES", icons.get("CERTIFICATES")))
elements.append(Spacer(1, 6))
certificates = [
    ("iOS Mobile App Development — MLSU Career Incubation Centre & Technical Solutions Hub (RUSA)", "2025"),
    ("Python Programming — Infosys", "June 2025"),
    ("Database Management System — Infosys", "June 2025"),
    ("Python Using AI Workshop — AI FOR TECHIES", "May 2025")
]
for title, provider in certificates:
    elements.append(Paragraph("• " + title + " — " + provider, styles["Body"]))
    # slightly smaller per-item spacer
    elements.append(Spacer(1, 2))

# small spacer to pull next section up
elements.append(Spacer(1, 2))


elements.append(section_heading("LANGUAGES", icons.get("LANGUAGES")))
elements.append(Spacer(1, 4))
elements.append(Paragraph("<b>•Hindi</b> — Native<br/><b>•English</b> — Conversational", styles["Body"]))
elements.append(Spacer(1, 4))

elements.append(section_heading("INTERESTS", icons.get("INTERESTS")))
elements.append(Spacer(1, 4))
elements.append(Paragraph("Cricket, Self-learning, App Development", styles["Body"]))
# final small spacer
elements.append(Spacer(1, 4))

# ---------- Build PDF ----------
doc.build(elements)
print("✅ ATS-optimized resume created as 'resume_optionA.pdf'")
