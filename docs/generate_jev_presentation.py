from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


OUTPUT_PATH = Path(__file__).with_name("jev_system_one_codeinsight.pptx")
PRESENTATION = Presentation()
PRESENTATION.slide_width = Inches(13.333)
PRESENTATION.slide_height = Inches(7.5)

NAVY = RGBColor(12, 24, 48)
TEAL = RGBColor(0, 173, 181)
CORAL = RGBColor(255, 107, 107)
INK = RGBColor(31, 41, 55)
MUTED = RGBColor(94, 109, 130)
PAPER = RGBColor(247, 250, 252)
WHITE = RGBColor(255, 255, 255)
PALE_TEAL = RGBColor(222, 247, 248)
PALE_CORAL = RGBColor(255, 235, 235)


def set_background(slide, color=PAPER):
    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = color


def add_text(slide, text, x, y, w, h, size=20, color=INK, bold=False,
             font="Aptos", align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return shape


def add_box(slide, x, y, w, h, fill, radius=True, line=None):
    shape_type = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def add_title(slide, title, eyebrow="CODEINSIGHT | JEV EXPLAINER"):
    add_text(slide, eyebrow, 0.7, 0.35, 6.4, 0.3, 11, TEAL, True)
    add_text(slide, title, 0.7, 0.72, 11.9, 0.58, 29, NAVY, True)
    add_box(slide, 0.7, 1.38, 1.1, 0.06, TEAL, False)


def add_footer(slide, number):
    add_text(slide, "CodeInsight", 0.7, 7.08, 2.0, 0.2, 10, MUTED, True)
    add_text(slide, f"{number:02d}", 12.05, 7.08, 0.55, 0.2, 10, MUTED, True, align=PP_ALIGN.RIGHT)


def add_bullet_list(slide, items, x=0.9, y=1.8, w=7.3, h=4.8, size=20):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    for index, item in enumerate(items):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = item
        paragraph.level = 0
        paragraph.space_after = Pt(17)
        paragraph.font.name = "Aptos"
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = INK
        paragraph.font.bold = False
        paragraph.bullet = True
    return shape


def add_code(slide, code, x, y, w, h):
    box = add_box(slide, x, y, w, h, NAVY, True)
    frame = box.text_frame
    frame.clear()
    frame.margin_left = Inches(0.25)
    frame.margin_right = Inches(0.25)
    frame.margin_top = Inches(0.18)
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.text = code
    paragraph.font.name = "Consolas"
    paragraph.font.size = Pt(14)
    paragraph.font.color.rgb = WHITE
    return box


def add_flow_card(slide, label, detail, x, y, color):
    card = add_box(slide, x, y, 2.65, 1.65, WHITE, True, color)
    add_text(slide, label, x + 0.2, y + 0.22, 2.25, 0.35, 18, color, True)
    add_text(slide, detail, x + 0.2, y + 0.68, 2.25, 0.62, 13, INK)
    return card


def add_arrow(slide, x, y):
    add_text(slide, ">", x, y, 0.35, 0.35, 25, TEAL, True, align=PP_ALIGN.CENTER)


def add_primitives_table(slide):
    rows, columns = 5, 4
    table_shape = slide.shapes.add_table(
        rows, columns, Inches(0.68), Inches(1.85), Inches(12.0), Inches(4.7)
    )
    table = table_shape.table
    widths = [2.05, 2.3, 3.0, 4.65]
    for index, width in enumerate(widths):
        table.columns[index].width = Inches(width)

    headers = ["Primitive / Class", "Core Purpose", "Output Provided", "Typical Use Case"]
    values = [
        ["TypeSafeClient", "API connector", "Network handler", "Initialize a connection to the Jev model API"],
        ["Choice", "Multi-class sorting", "Selected option + probabilities", "Intent routing, department triage, categorization"],
        ["Noul", "Binary check", "True/False probability (0.0 to 1.0)", "Safety guardrails, prompt injection detection, policy checks"],
        ["Score", "Rubric scaling", "Ordered level + continuous score", "Urgency detection, priority scoring, sentiment evaluation"],
    ]

    for column, header in enumerate(headers):
        cell = table.cell(0, column)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.text = header

    for row, value_row in enumerate(values, start=1):
        row_color = WHITE if row % 2 else PALE_TEAL
        for column, value in enumerate(value_row):
            cell = table.cell(row, column)
            cell.fill.solid()
            cell.fill.fore_color.rgb = row_color
            cell.text = value

    for row in range(rows):
        for column in range(columns):
            cell = table.cell(row, column)
            cell.margin_left = Inches(0.09)
            cell.margin_right = Inches(0.09)
            cell.margin_top = Inches(0.05)
            cell.margin_bottom = Inches(0.05)
            paragraph = cell.text_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.LEFT
            paragraph.font.name = "Aptos"
            paragraph.font.size = Pt(12 if row else 13)
            paragraph.font.bold = row == 0 or column == 0
            paragraph.font.color.rgb = WHITE if row == 0 else INK


def add_llm_comparison_table(slide):
    rows, columns = 7, 3
    table_shape = slide.shapes.add_table(
        rows, columns, Inches(0.62), Inches(1.72), Inches(12.1), Inches(4.95)
    )
    table = table_shape.table
    widths = [2.05, 5.0, 5.05]
    for index, width in enumerate(widths):
        table.columns[index].width = Inches(width)

    headers = ["Dimension", "Traditional LLM", "Jev (TypeSafe AI)"]
    values = [
        ["Primary purpose", "Creative, conversational, and explanatory text", "Structured decisions for application control"],
        ["Output style", "Free-form prose generated token by token", "Typed choices, scores, and probabilities"],
        ["Execution", "Generates a response before returning text", "Evaluates state against focused questions"],
        ["Best fit", "Open-ended questions, code, and conversation", "Safety checks, routing, classification, and scoring"],
        ["Confidence", "Expressed in generated text", "Decision-oriented values application code can inspect"],
        ["Relationship", "Produces the rich final answer", "Decides whether, where, or how to use an LLM"],
    ]

    for column, header in enumerate(headers):
        cell = table.cell(0, column)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.text = header

    for row, value_row in enumerate(values, start=1):
        row_color = WHITE if row % 2 else PALE_TEAL
        for column, value in enumerate(value_row):
            cell = table.cell(row, column)
            cell.fill.solid()
            cell.fill.fore_color.rgb = row_color
            cell.text = value

    for row in range(rows):
        for column in range(columns):
            cell = table.cell(row, column)
            cell.margin_left = Inches(0.1)
            cell.margin_right = Inches(0.1)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            paragraph = cell.text_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.LEFT
            paragraph.font.name = "Aptos"
            paragraph.font.size = Pt(10.5 if row else 12)
            paragraph.font.bold = row == 0 or column == 0
            paragraph.font.color.rgb = WHITE if row == 0 else INK


def title_slide():
    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide, NAVY)
    add_box(slide, 0.7, 0.75, 1.25, 0.08, TEAL, False)
    add_text(slide, "CODEINSIGHT PRESENTS", 0.7, 1.08, 5.3, 0.34, 13, TEAL, True)
    add_text(slide, "Jev: Fast AI Decisions\nBefore OpenAI", 0.7, 1.6, 8.8, 1.45, 39, WHITE, True)
    add_text(slide, "A practical System One architecture for safety, intent routing, and cost-aware AI apps.",
             0.75, 3.35, 7.8, 0.7, 19, RGBColor(205, 221, 235))
    add_box(slide, 9.25, 1.2, 2.85, 4.55, TEAL, True)
    add_text(slide, "INPUT", 9.65, 1.75, 2.05, 0.35, 15, NAVY, True, align=PP_ALIGN.CENTER)
    add_text(slide, "JEV", 9.55, 2.65, 2.25, 0.55, 30, WHITE, True, align=PP_ALIGN.CENTER)
    add_text(slide, "SAFETY\nINTENT\nURGENCY", 9.55, 3.45, 2.25, 1.1, 16, NAVY, True, align=PP_ALIGN.CENTER)
    add_text(slide, "OPENAI", 9.55, 5.05, 2.25, 0.35, 17, WHITE, True, align=PP_ALIGN.CENTER)
    add_text(slide, "youtube.com/@CodeInsight", 0.7, 6.78, 4.2, 0.25, 11, RGBColor(205, 221, 235))


def content_slide(title, number, bullets, highlight_title, highlight_text, highlight_color=PALE_TEAL):
    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, title)
    add_bullet_list(slide, bullets)
    card = add_box(slide, 8.65, 1.9, 3.75, 3.85, highlight_color, True)
    add_text(slide, highlight_title, 8.98, 2.23, 3.05, 0.45, 19, NAVY, True)
    add_text(slide, highlight_text, 8.98, 2.92, 3.02, 2.3, 17, INK)
    add_footer(slide, number)
    return slide


def build_deck():
    title_slide()

    content_slide(
        "What is Jev? A decision engine", 2,
        [
            "Jev is not a chatbot. It evaluates input and returns a typed decision for application code.",
            "It can inspect a request once and answer focused questions such as safety, urgency, or routing.",
            "The output is a category, probability, or score rather than a generated paragraph.",
        ],
        "One-pass decision",
        "Input -> evaluate -> typed result\n\nDesigned for direct application control, not open-ended conversation.",
    )

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "The chatbot request flow")
    add_flow_card(slide, "1. USER", "A message arrives in Streamlit.", 0.75, 2.45, TEAL)
    add_arrow(slide, 3.5, 3.05)
    add_flow_card(slide, "2. JEV", "Evaluate safety, intent, and urgency in one call.", 3.9, 2.45, CORAL)
    add_arrow(slide, 6.65, 3.05)
    add_flow_card(slide, "3. ROUTE", "Block, fast-path a greeting, or continue.", 7.05, 2.45, TEAL)
    add_arrow(slide, 9.8, 3.05)
    add_flow_card(slide, "4. OPENAI", "Generate only when needed, using Jev context.", 10.2, 2.45, CORAL)
    add_text(slide, "One structured decision determines the rest of the request path.", 1.1, 5.25, 11.1, 0.45, 21, NAVY, True, align=PP_ALIGN.CENTER)
    add_footer(slide, 3)

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Jev SDK primitives at a glance")
    add_primitives_table(slide)
    add_footer(slide, 4)

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "One Jev call, three structured answers")
    add_code(slide, "jev_response = jev_client.system_one(\n"
                    "    state=user_message,\n"
                    "    questions={\n"
                    "        \"is_safe\": Noul(...),\n"
                    "        \"intent\": Choice(...),\n"
                    "        \"urgency\": Score(...),\n"
                    "    },\n"
                    ")", 0.85, 1.85, 6.1, 4.25)
    add_box(slide, 7.55, 1.85, 4.6, 4.25, PALE_CORAL, True)
    add_text(slide, "What comes back", 7.9, 2.2, 3.9, 0.4, 20, NAVY, True)
    add_text(slide, "safety probability\nintent choice + confidence\nurgency score", 7.9, 3.0, 3.65, 1.6, 21, INK)
    add_text(slide, "The app stores these values as telemetry and uses them for routing.", 7.9, 5.0, 3.65, 0.55, 14, MUTED)
    add_footer(slide, 5)

    content_slide(
        "Safety gate: block before OpenAI", 6,
        [
            "The chatbot treats a safety probability above 0.75 as a blocking condition.",
            "The request returns a policy message without sending the input to the OpenAI API.",
            "This is an application-level decision: tune the threshold using observed outcomes and your policy needs.",
        ],
        "Control logic",
        "if safety_prob > 0.75:\n    return blocked_reply\n\nOpenAI is not called on this path.",
        PALE_CORAL,
    )

    content_slide(
        "Jev and LLMs: two complementary roles", 7,
        [
            "Use Jev when the application needs a direct decision: safe or unsafe, urgent or not, and where to route a request.",
            "Use an LLM for open-ended questions, detailed explanations, creative work, code, and conversation.",
            "The best architecture combines them: Jev decides first; an LLM generates only when rich text adds value.",
        ],
        "Same query, different output",
        "Question: Is this urgent?\n\nJev -> score + route\nLLM -> written explanation\n\nJev is a sidekick, not a replacement.",
    )

    content_slide(
        "Telemetry makes the route visible", 8,
        [
            "Each assistant response exposes an expandable Jev telemetry panel in Streamlit.",
            "The panel shows safety risk, classified intent, classification confidence, and urgency score.",
            "Visible telemetry helps developers inspect routing behavior while testing the application.",
        ],
        "Telemetry fields",
        "safety_risk\nintent\nintent_confidence\nurgency",
    )

    content_slide(
        "Production notes: keep the guardrail honest", 9,
        [
            "Keep API keys in environment variables or Streamlit secrets, never in source control.",
            "Log decisions carefully and avoid writing sensitive user content to telemetry.",
            "Decide explicitly whether a Jev outage should block requests or use a fallback route.",
            "Validate pricing, latency, and model behavior against current provider documentation before publishing claims.",
        ],
        "Current app behavior",
        "The demo uses fallback values if Jev raises an exception. For higher-risk uses, consider fail-closed handling.",
        PALE_CORAL,
    )

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Reference: Jev and traditional LLMs")
    add_llm_comparison_table(slide)
    add_footer(slide, 10)

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Reference: decouple decisions from generation")
    add_flow_card(slide, "USER MESSAGE", "The user submits a request in Streamlit.", 0.75, 2.2, TEAL)
    add_arrow(slide, 3.5, 2.8)
    add_flow_card(slide, "JEV SYSTEM ONE", "Safety, intent, and urgency are evaluated.", 3.9, 2.2, CORAL)
    add_arrow(slide, 6.65, 2.8)
    add_flow_card(slide, "FAST PATH", "Unsafe or simple requests can be blocked or answered directly.", 7.05, 2.2, TEAL)
    add_text(slide, "Safe request requiring generation", 4.1, 4.5, 3.4, 0.3, 15, MUTED, True, align=PP_ALIGN.CENTER)
    add_text(slide, "v", 5.55, 4.82, 0.4, 0.3, 24, TEAL, True, align=PP_ALIGN.CENTER)
    add_flow_card(slide, "OPENAI", "Generate a detailed response only when it adds value.", 4.45, 5.15, CORAL)
    add_text(slide, "Decision-making stays separate from text generation.", 8.05, 5.55, 3.8, 0.5, 17, NAVY, True, align=PP_ALIGN.CENTER)
    add_footer(slide, 11)

    content_slide(
        "Reference: illustrative Jev token cost", 12,
        [
            "Example assumption: an evaluation sends approximately 350 input tokens, including user text and question instructions.",
            "Reference rate: $0.042 per one million input tokens; typed results do not require generated output text in this example.",
            "Always verify current pricing, token accounting, and service terms before using estimates in production planning.",
        ],
        "Illustrative calculation",
        "(350 / 1,000,000) x $0.042\n\n= $0.0000147 per evaluation",
        PALE_CORAL,
    )

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Five takeaways: Jev in one minute")
    takeaways = [
        ("1", "Decision engine, not a chatbot"),
        ("2", "Typed answers, zero fluff"),
        ("3", "One pass. One shot."),
        ("4", "Story vs. straight answer"),
        ("5", "Sidekick, not a successor"),
    ]
    for index, (number, message) in enumerate(takeaways):
        column = index % 2
        row = index // 2
        x = 0.9 + (column * 6.05)
        y = 1.8 + (row * 1.35)
        add_box(slide, x, y, 5.45, 0.92, PALE_TEAL if index % 2 == 0 else PALE_CORAL, True)
        add_text(slide, number, x + 0.18, y + 0.17, 0.48, 0.42, 21, NAVY, True, align=PP_ALIGN.CENTER)
        add_text(slide, message, x + 0.8, y + 0.16, 4.35, 0.44, 20, INK, True)
    add_text(slide, "Built for real-world use cases: safety, routing, triage, and prioritization.",
             0.9, 6.15, 11.4, 0.32, 16, MUTED, True, align=PP_ALIGN.CENTER)
    add_footer(slide, 13)

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Video talking points: the fuller explanation")
    talking_points = [
        ("WHAT IS JEV?", "A decision engine that gives application code a direct signal, not a chatbot response."),
        ("WHAT DOES IT DO?", "Returns typed values such as a choice, probability, or score: structured results, zero fluff."),
        ("HOW DOES IT DO IT?", "One system_one() evaluation receives the state and focused questions, then returns results."),
        ("JEV VS. LLM", "An LLM writes the story. Jev gives the operational signal behind the next application action."),
        ("WILL IT REPLACE LLMS?", "No. Jev is the sidekick for safety and routing; the LLM remains the voice for rich generation."),
    ]
    for index, (heading, detail) in enumerate(talking_points):
        y = 1.62 + (index * 0.96)
        fill = PALE_TEAL if index % 2 == 0 else PALE_CORAL
        add_box(slide, 0.75, y, 11.85, 0.74, fill, True)
        add_text(slide, heading, 1.0, y + 0.12, 2.35, 0.34, 13, NAVY, True)
        add_text(slide, detail, 3.18, y + 0.11, 8.95, 0.38, 14, INK)
    add_text(slide, "Built for real-world use cases. Different strengths, bigger possibilities.",
             0.85, 6.55, 11.55, 0.28, 14, MUTED, True, align=PP_ALIGN.CENTER)
    add_footer(slide, 14)

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide)
    add_title(slide, "Same query, two worlds")
    add_box(slide, 4.5, 1.57, 4.3, 0.56, PALE_CORAL, True)
    add_text(slide, 'User query: "Is this urgent?"', 4.72, 1.68, 3.86, 0.25, 17, NAVY, True, align=PP_ALIGN.CENTER)
    add_box(slide, 0.75, 2.32, 5.65, 3.55, PALE_CORAL, True)
    add_text(slide, "LLM WORLD", 1.05, 2.62, 5.05, 0.33, 21, NAVY, True, align=PP_ALIGN.CENTER)
    add_text(slide, "Context + prompt\n      |\nGenerated text response\n\nGreat for explaining, writing,\nand open-ended questions.\n\nMore generated text can mean\nmore tokens, time, and cost.",
             1.25, 3.12, 4.65, 2.2, 16, INK, align=PP_ALIGN.CENTER)
    add_box(slide, 6.95, 2.32, 5.65, 3.55, PALE_TEAL, True)
    add_text(slide, "JEV WORLD", 7.25, 2.62, 5.05, 0.33, 21, NAVY, True, align=PP_ALIGN.CENTER)
    add_text(slide, "State + focused questions\n      |\nConfidence: 0.92\nRoute: Finance\nTyped decision: done\n\nFast signal for routing and\napplication control.",
             7.45, 3.12, 4.65, 2.2, 16, INK, align=PP_ALIGN.CENTER)
    add_text(slide, "SAME QUESTION. DIFFERENT SPEED. DIFFERENT COST.",
             0.8, 6.18, 11.7, 0.34, 19, NAVY, True, align=PP_ALIGN.CENTER)
    add_text(slide, "Illustrative comparison: observed latency and cost depend on the model, prompt, and workload.",
             0.9, 6.58, 11.5, 0.22, 11, MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, 15)

    slide = PRESENTATION.slides.add_slide(PRESENTATION.slide_layouts[6])
    set_background(slide, NAVY)
    add_box(slide, 0.75, 0.9, 1.25, 0.08, TEAL, False)
    add_text(slide, "BUILD SMARTER AI FLOWS", 0.75, 1.3, 4.3, 0.35, 14, TEAL, True)
    add_text(slide, "Use fast decisions\nbefore slow generation.", 0.75, 1.9, 8.4, 1.25, 35, WHITE, True)
    add_text(slide, "Jev gives your application structured signals for safety, routing, and control.",
             0.75, 3.55, 8.0, 0.55, 19, RGBColor(205, 221, 235))
    add_box(slide, 0.75, 5.05, 4.6, 0.72, TEAL, True)
    add_text(slide, "Subscribe: CodeInsight", 1.05, 5.22, 4.0, 0.28, 19, NAVY, True, align=PP_ALIGN.CENTER)
    add_text(slide, "Next: add your demo screen recording and repository link.", 0.75, 6.35, 7.4, 0.3, 13, RGBColor(205, 221, 235))
    add_text(slide, "16", 12.05, 7.08, 0.55, 0.2, 10, RGBColor(205, 221, 235), True, align=PP_ALIGN.RIGHT)

    if len(PRESENTATION.slides) != 16:
        raise RuntimeError(f"Expected 16 slides, generated {len(PRESENTATION.slides)}")
    PRESENTATION.save(str(OUTPUT_PATH))
    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    build_deck()