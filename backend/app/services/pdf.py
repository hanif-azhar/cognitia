from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
from typing import Literal

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..models import Distortion, Emotion, Entry, TherapistFeedback, WinningMoment
from ..schemas.analytics import AnalyticsSummary, DistortionFrequency, EmotionTrendPoint

Lang = Literal["en", "id"]

# Therapist-whiteboard palette (same hex as frontend)
COLOR_TRIANGLE = colors.HexColor("#A855F7")
COLOR_SQUARE = colors.HexColor("#3B82F6")
COLOR_CIRCLE = colors.HexColor("#EF4444")
COLOR_INK = colors.HexColor("#2A2A33")
COLOR_MUTED = colors.HexColor("#6B7280")
COLOR_RULE = colors.HexColor("#E5E7EB")
COLOR_REFRAME = colors.HexColor("#10B981")


I18N: dict[str, dict[Lang, str]] = {
    "app_name": {"en": "Cognitia", "id": "Cognitia"},
    "single_title": {"en": "CBT Journal Entry", "id": "Catatan CBT"},
    "insights_title": {"en": "Insights Report", "id": "Laporan Wawasan"},
    "generated": {"en": "Generated", "id": "Dibuat"},
    "entry_date": {"en": "Entry date", "id": "Tanggal catatan"},
    "consequences": {"en": "Consequences (Circle)", "id": "Konsekuensi (Lingkaran)"},
    "activating": {"en": "Activating Event (Triangle)", "id": "Peristiwa Pemicu (Segitiga)"},
    "belief": {"en": "Belief (Square)", "id": "Pikiran (Kotak)"},
    "emotions": {"en": "Emotions", "id": "Emosi"},
    "intensity": {"en": "Intensity", "id": "Intensitas"},
    "behavior": {"en": "Behavior", "id": "Perilaku"},
    "situation": {"en": "Situation", "id": "Situasi"},
    "location": {"en": "Location", "id": "Lokasi"},
    "people": {"en": "People involved", "id": "Orang yang terlibat"},
    "automatic_thought": {"en": "Automatic thought", "id": "Pikiran otomatis"},
    "distortions": {"en": "Cognitive distortions", "id": "Distorsi kognitif"},
    "testing_title": {"en": "Testing the thought", "id": "Menguji pikiran"},
    "evidence_for": {"en": "Evidence for the belief", "id": "Bukti yang mendukung"},
    "evidence_against": {"en": "Evidence against the belief", "id": "Bukti yang melawan"},
    "reality_test": {"en": "Reality test", "id": "Uji realitas"},
    "pragmatic_check": {"en": "Pragmatic check", "id": "Cek pragmatis"},
    "alternative_action": {"en": "Alternative action", "id": "Tindakan alternatif"},
    "reframed_thought": {"en": "Reframed thought", "id": "Pikiran yang dibingkai ulang"},
    "complete": {"en": "Complete", "id": "Selesai"},
    "draft": {"en": "Draft", "id": "Draf"},
    "none": {"en": "—", "id": "—"},
    "footer": {
        "en": "Private journal — for personal reflection and therapy support.",
        "id": "Jurnal pribadi — untuk refleksi diri dan pendamping terapi.",
    },
    "summary": {"en": "Summary", "id": "Ringkasan"},
    "total_entries": {"en": "Total entries", "id": "Total catatan"},
    "completed_entries": {"en": "Completed", "id": "Selesai"},
    "reframe_rate": {"en": "Reframe rate", "id": "Tingkat reframe"},
    "average_intensity": {"en": "Average intensity", "id": "Intensitas rata-rata"},
    "current_streak": {"en": "Current streak", "id": "Streak saat ini"},
    "longest_streak": {"en": "Longest streak", "id": "Streak terpanjang"},
    "days": {"en": "days", "id": "hari"},
    "top_distortions": {"en": "Top distortions", "id": "Distorsi teratas"},
    "top_emotions": {"en": "Top emotions", "id": "Emosi teratas"},
    "distortion_frequency": {"en": "Distortion frequency", "id": "Frekuensi distorsi"},
    "no_data": {"en": "Not enough data yet.", "id": "Datanya belum cukup."},
    "count": {"en": "count", "id": "jumlah"},
    "session_summary_title": {
        "en": "Session Summary",
        "id": "Ringkasan Sesi",
    },
    "session_period": {"en": "Period", "id": "Periode"},
    "session_intro": {
        "en": "Prepared for review with a mental health professional.",
        "id": "Disusun untuk ditinjau bersama tenaga kesehatan mental.",
    },
    "entries_in_period": {
        "en": "Completed entries in this period",
        "id": "Catatan selesai pada periode ini",
    },
    "wins_in_period": {
        "en": "Winning moments in this period",
        "id": "Momen kemenangan pada periode ini",
    },
    "feedback_in_period": {
        "en": "Therapist feedback in this period",
        "id": "Masukan terapis pada periode ini",
    },
    "no_entries": {
        "en": "No completed entries in this period.",
        "id": "Tidak ada catatan selesai pada periode ini.",
    },
    "no_wins": {
        "en": "No wins logged in this period.",
        "id": "Tidak ada kemenangan tercatat pada periode ini.",
    },
    "no_feedback": {
        "en": "No therapist feedback in this period.",
        "id": "Tidak ada masukan terapis pada periode ini.",
    },
    "for_reviewer": {
        "en": "Cognitia · Session summary for therapist review.",
        "id": "Cognitia · Ringkasan sesi untuk peninjauan terapis.",
    },
}


def _tr(key: str, lang: Lang) -> str:
    return I18N[key][lang]


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "h1",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=COLOR_INK,
        spaceAfter=4,
    )
    meta = ParagraphStyle(
        "meta",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=COLOR_MUTED,
        spaceAfter=12,
    )
    section = ParagraphStyle(
        "section",
        parent=base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=COLOR_INK,
        spaceBefore=10,
        spaceAfter=4,
    )
    label = ParagraphStyle(
        "label",
        parent=base["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_MUTED,
        spaceAfter=2,
    )
    body = ParagraphStyle(
        "body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=COLOR_INK,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    quote = ParagraphStyle(
        "quote",
        parent=body,
        fontName="Helvetica-Oblique",
        textColor=COLOR_INK,
    )
    reframe = ParagraphStyle(
        "reframe",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=16,
        textColor=COLOR_REFRAME,
    )
    chip = ParagraphStyle(
        "chip",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=COLOR_INK,
    )
    return {
        "h1": h1,
        "meta": meta,
        "section": section,
        "label": label,
        "body": body,
        "quote": quote,
        "reframe": reframe,
        "chip": chip,
    }


class ShapeBadge(Flowable):
    """Small SVG-like geometric badge — circle / triangle / square."""

    def __init__(self, kind: Literal["circle", "triangle", "square"], size: float = 10):
        super().__init__()
        self.kind = kind
        self.size = size
        self.width = size
        self.height = size

    def draw(self) -> None:  # type: ignore[override]
        c = self.canv
        s = self.size
        if self.kind == "circle":
            c.setFillColor(COLOR_CIRCLE)
            c.setStrokeColor(COLOR_CIRCLE)
            c.circle(s / 2, s / 2, s / 2, fill=1, stroke=0)
        elif self.kind == "triangle":
            c.setFillColor(COLOR_TRIANGLE)
            c.setStrokeColor(COLOR_TRIANGLE)
            p = c.beginPath()
            p.moveTo(s / 2, s)
            p.lineTo(s, 0)
            p.lineTo(0, 0)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
        else:
            c.setFillColor(COLOR_SQUARE)
            c.setStrokeColor(COLOR_SQUARE)
            c.rect(0, 0, s, s, fill=1, stroke=0)


def _esc(text: str | None) -> str:
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _section_header(label: str, kind: str | None, styles: dict[str, ParagraphStyle]) -> Flowable:
    if kind:
        tbl = Table(
            [[ShapeBadge(kind, 10), Paragraph(_esc(label), styles["section"])]],
            colWidths=[14, None],
        )
        tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        return tbl
    return Paragraph(_esc(label), styles["section"])


def _label_value(label: str, value: str | None, styles: dict[str, ParagraphStyle], style_key: str = "body") -> list[Flowable]:
    if not value:
        return []
    return [
        Paragraph(_esc(label).upper(), styles["label"]),
        Paragraph(_esc(value).replace("\n", "<br/>"), styles[style_key]),
        Spacer(1, 4),
    ]


def _chips(items: list[str]) -> Flowable:
    if not items:
        return Spacer(1, 0)
    rows = [[Paragraph(f"<font size='9'>{_esc(s)}</font>", getSampleStyleSheet()["BodyText"]) for s in items]]
    tbl = Table(rows, colWidths=[None] * len(items))
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F4F6")),
                ("BOX", (0, 0), (-1, -1), 0.4, COLOR_RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return tbl


def _draw_footer(canvas, doc, footer_text: str) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COLOR_MUTED)
    canvas.drawString(20 * mm, 12 * mm, footer_text)
    canvas.drawRightString(
        A4[0] - 20 * mm, 12 * mm, f"{_tr('app_name', 'en')}  ·  {canvas.getPageNumber()}"
    )
    canvas.restoreState()


def _build_doc(buf: BytesIO, footer_text: str) -> SimpleDocTemplate:
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="Cognitia",
        author="Cognitia",
    )
    doc._footer_text = footer_text  # type: ignore[attr-defined]
    return doc


def render_entry_pdf(
    entry: Entry,
    distortions: list[Distortion],
    emotions: list[Emotion],
    lang: Lang | None = None,
) -> bytes:
    L: Lang = lang or (entry.language if entry.language in ("en", "id") else "en")  # type: ignore[assignment]
    styles = _styles()
    buf = BytesIO()
    footer = _tr("footer", L)
    doc = _build_doc(buf, footer)

    distortion_names = [(d.name_id if L == "id" else d.name_en) for d in distortions]
    emotion_names = [(e.name_id if L == "id" else e.name_en) for e in emotions]

    story: list[Flowable] = []
    story.append(Paragraph(_esc(_tr("single_title", L)), styles["h1"]))
    meta_bits = [
        f"{_tr('entry_date', L)}: {entry.entry_date.isoformat()}",
        f"{_tr('generated', L)}: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        _tr("complete", L) if entry.is_complete else _tr("draft", L),
    ]
    story.append(Paragraph(" · ".join(_esc(m) for m in meta_bits), styles["meta"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE, spaceAfter=6))

    # C — Consequences
    story.append(_section_header(_tr("consequences", L), "circle", styles))
    if emotion_names:
        story.append(_chips(emotion_names))
        story.append(Spacer(1, 4))
    story.extend(_label_value(_tr("intensity", L), f"{entry.emotion_intensity}/10", styles))
    story.extend(_label_value(_tr("behavior", L), entry.behavior, styles))

    # A — Activating event
    story.append(_section_header(_tr("activating", L), "triangle", styles))
    story.extend(_label_value(_tr("situation", L), entry.situation, styles))
    if entry.location:
        story.extend(_label_value(_tr("location", L), entry.location, styles))
    if entry.people_involved:
        story.extend(_label_value(_tr("people", L), entry.people_involved, styles))

    # B — Belief
    story.append(_section_header(_tr("belief", L), "square", styles))
    if entry.automatic_thought:
        story.append(
            Paragraph(f"&ldquo;{_esc(entry.automatic_thought)}&rdquo;", styles["quote"])
        )
        story.append(Spacer(1, 4))
    if distortion_names:
        story.append(Paragraph(_esc(_tr("distortions", L)).upper(), styles["label"]))
        story.append(_chips(distortion_names))
        story.append(Spacer(1, 6))

    # Testing
    has_testing = any(
        [
            entry.evidence_for,
            entry.evidence_against,
            entry.reality_test_response,
            entry.pragmatic_check_response,
            entry.alternative_action,
        ]
    )
    if has_testing:
        story.append(_section_header(_tr("testing_title", L), None, styles))
        if entry.evidence_for or entry.evidence_against:
            row = [
                [
                    [
                        Paragraph(_esc(_tr("evidence_for", L)).upper(), styles["label"]),
                        Paragraph(_esc(entry.evidence_for or "—").replace("\n", "<br/>"), styles["body"]),
                    ],
                    [
                        Paragraph(_esc(_tr("evidence_against", L)).upper(), styles["label"]),
                        Paragraph(
                            _esc(entry.evidence_against or "—").replace("\n", "<br/>"),
                            styles["body"],
                        ),
                    ],
                ]
            ]
            tbl = Table(row, colWidths=[(A4[0] - 40 * mm) / 2 - 4] * 2)
            tbl.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ECFDF5")),
                        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#FFF1F2")),
                        ("BOX", (0, 0), (-1, -1), 0.4, COLOR_RULE),
                        ("INNERGRID", (0, 0), (-1, -1), 0.4, COLOR_RULE),
                    ]
                )
            )
            story.append(tbl)
            story.append(Spacer(1, 8))
        story.extend(_label_value(_tr("reality_test", L), entry.reality_test_response, styles))
        story.extend(_label_value(_tr("pragmatic_check", L), entry.pragmatic_check_response, styles))
        story.extend(_label_value(_tr("alternative_action", L), entry.alternative_action, styles))

    # Reframe
    if entry.reframed_thought:
        story.append(Spacer(1, 6))
        reframe_box = Table(
            [
                [
                    [
                        Paragraph(_esc(_tr("reframed_thought", L)).upper(), styles["label"]),
                        Paragraph(_esc(entry.reframed_thought).replace("\n", "<br/>"), styles["reframe"]),
                    ]
                ]
            ],
            colWidths=[A4[0] - 40 * mm],
        )
        reframe_box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, COLOR_REFRAME),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(KeepTogether(reframe_box))

    doc.build(
        story,
        onFirstPage=lambda c, d: _draw_footer(c, d, footer),
        onLaterPages=lambda c, d: _draw_footer(c, d, footer),
    )
    return buf.getvalue()


def render_insights_pdf(
    summary: AnalyticsSummary,
    distortion_freq: list[DistortionFrequency],
    emotion_trend: list[EmotionTrendPoint],
    period_from: date | None,
    period_to: date | None,
    lang: Lang = "en",
) -> bytes:
    styles = _styles()
    buf = BytesIO()
    footer = _tr("footer", lang)
    doc = _build_doc(buf, footer)

    story: list[Flowable] = []
    story.append(Paragraph(_esc(_tr("insights_title", lang)), styles["h1"]))
    period = ""
    if period_from or period_to:
        f = period_from.isoformat() if period_from else ""
        t = period_to.isoformat() if period_to else ""
        period = f" · {f} → {t}"
    story.append(
        Paragraph(
            f"{_tr('generated', lang)}: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}{period}",
            styles["meta"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE, spaceAfter=10))

    # Summary tiles
    reframe_pct = f"{round((summary.reframe_rate or 0) * 100)}%"
    avg = f"{summary.average_intensity:.1f}/10" if summary.total_entries else "—"
    tiles = [
        [
            _stat(_tr("total_entries", lang), str(summary.total_entries), styles),
            _stat(_tr("completed_entries", lang), str(summary.completed_entries), styles),
            _stat(_tr("reframe_rate", lang), reframe_pct, styles),
        ],
        [
            _stat(_tr("average_intensity", lang), avg, styles),
            _stat(
                _tr("current_streak", lang),
                f"{summary.streak.current_streak} {_tr('days', lang)}",
                styles,
            ),
            _stat(
                _tr("longest_streak", lang),
                f"{summary.streak.longest_streak} {_tr('days', lang)}",
                styles,
            ),
        ],
    ]
    col_w = (A4[0] - 40 * mm) / 3
    tile_tbl = Table(tiles, colWidths=[col_w, col_w, col_w])
    tile_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
                ("BOX", (0, 0), (-1, -1), 0.4, COLOR_RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, COLOR_RULE),
            ]
        )
    )
    story.append(tile_tbl)
    story.append(Spacer(1, 14))

    # Distortion frequency table + bars
    story.append(Paragraph(_esc(_tr("distortion_frequency", lang)), styles["section"]))
    if not distortion_freq:
        story.append(Paragraph(_esc(_tr("no_data", lang)), styles["body"]))
    else:
        max_count = max(d.count for d in distortion_freq) or 1
        rows: list[list] = [
            [
                Paragraph(f"<b>{_esc(_tr('top_distortions', lang))}</b>", styles["body"]),
                Paragraph(f"<b>{_esc(_tr('count', lang))}</b>", styles["body"]),
                Paragraph("", styles["body"]),
            ]
        ]
        for d in distortion_freq:
            name = d.name_id if lang == "id" else d.name_en
            bar = _BarFlowable(d.count, max_count, width=70, height=8, color=COLOR_SQUARE)
            rows.append([Paragraph(_esc(name), styles["body"]), Paragraph(str(d.count), styles["body"]), bar])
        tbl = Table(rows, colWidths=[(A4[0] - 40 * mm) - 110, 30, 80])
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, COLOR_RULE),
                    ("LINEBELOW", (0, -1), (-1, -1), 0.3, COLOR_RULE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(tbl)

    story.append(Spacer(1, 14))

    # Top emotions
    if summary.top_emotions:
        story.append(Paragraph(_esc(_tr("top_emotions", lang)), styles["section"]))
        max_count = max(e.count for e in summary.top_emotions) or 1
        rows = [
            [
                Paragraph(f"<b>{_esc(_tr('top_emotions', lang))}</b>", styles["body"]),
                Paragraph(f"<b>{_esc(_tr('count', lang))}</b>", styles["body"]),
                Paragraph(f"<b>{_esc(_tr('average_intensity', lang))}</b>", styles["body"]),
                Paragraph("", styles["body"]),
            ]
        ]
        for e in summary.top_emotions:
            name = e.name_id if lang == "id" else e.name_en
            bar = _BarFlowable(e.count, max_count, width=70, height=8, color=COLOR_CIRCLE)
            rows.append(
                [
                    Paragraph(_esc(name), styles["body"]),
                    Paragraph(str(e.count), styles["body"]),
                    Paragraph(f"{e.avg_intensity:.1f}/10", styles["body"]),
                    bar,
                ]
            )
        tbl = Table(rows, colWidths=[(A4[0] - 40 * mm) - 180, 40, 60, 80])
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, COLOR_RULE),
                    ("LINEBELOW", (0, -1), (-1, -1), 0.3, COLOR_RULE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(tbl)

    doc.build(
        story,
        onFirstPage=lambda c, d: _draw_footer(c, d, footer),
        onLaterPages=lambda c, d: _draw_footer(c, d, footer),
    )
    return buf.getvalue()


def _stat(label: str, value: str, styles: dict[str, ParagraphStyle]) -> list[Flowable]:
    return [
        Paragraph(_esc(label).upper(), styles["label"]),
        Paragraph(
            f"<font size='17' color='#2A2A33'><b>{_esc(value)}</b></font>",
            styles["body"],
        ),
    ]


class _BarFlowable(Flowable):
    def __init__(self, value: float, max_value: float, width: float, height: float, color):
        super().__init__()
        self.value = max(0.0, value)
        self.max_value = max(0.0001, max_value)
        self.width = width
        self.height = height
        self.color = color

    def draw(self) -> None:  # type: ignore[override]
        c = self.canv
        c.setFillColor(colors.HexColor("#F3F4F6"))
        c.setStrokeColor(COLOR_RULE)
        c.roundRect(0, 0, self.width, self.height, 2, fill=1, stroke=0)
        fill_w = self.width * (self.value / self.max_value)
        c.setFillColor(self.color)
        c.roundRect(0, 0, max(2, fill_w), self.height, 2, fill=1, stroke=0)


def render_session_summary_pdf(
    summary: AnalyticsSummary,
    distortion_freq: list[DistortionFrequency],
    period_from: date,
    period_to: date,
    entries: list[Entry],
    entry_distortion_map: dict[str, list[Distortion]],
    entry_emotion_map: dict[str, list[Emotion]],
    wins: list[WinningMoment],
    feedback_items: list[tuple[TherapistFeedback, Entry]],
    lang: Lang = "en",
) -> bytes:
    styles = _styles()
    buf = BytesIO()
    footer = _tr("for_reviewer", lang)
    doc = _build_doc(buf, footer)

    story: list[Flowable] = []

    # Header
    story.append(Paragraph(_esc(_tr("session_summary_title", lang)), styles["h1"]))
    period_str = f"{period_from.isoformat()} → {period_to.isoformat()}"
    story.append(
        Paragraph(
            f"{_tr('session_period', lang)}: {period_str}  ·  "
            f"{_tr('generated', lang)}: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            styles["meta"],
        )
    )
    story.append(Paragraph(_esc(_tr("session_intro", lang)), styles["meta"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE, spaceAfter=10))

    # Summary tiles
    reframe_pct = f"{round((summary.reframe_rate or 0) * 100)}%"
    tiles = [
        [
            _stat(_tr("total_entries", lang), str(summary.total_entries), styles),
            _stat(_tr("completed_entries", lang), str(summary.completed_entries), styles),
            _stat(_tr("reframe_rate", lang), reframe_pct, styles),
            _stat(
                _tr("current_streak", lang),
                f"{summary.streak.current_streak} {_tr('days', lang)}",
                styles,
            ),
        ]
    ]
    col_w = (A4[0] - 40 * mm) / 4
    tile_tbl = Table(tiles, colWidths=[col_w] * 4)
    tile_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
                ("BOX", (0, 0), (-1, -1), 0.4, COLOR_RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, COLOR_RULE),
            ]
        )
    )
    story.append(tile_tbl)
    story.append(Spacer(1, 14))

    # Top distortions
    story.append(Paragraph(_esc(_tr("top_distortions", lang)), styles["section"]))
    if not distortion_freq:
        story.append(Paragraph(_esc(_tr("no_data", lang)), styles["body"]))
    else:
        max_count = max(d.count for d in distortion_freq) or 1
        rows: list[list] = []
        for d in distortion_freq[:3]:
            name = d.name_id if lang == "id" else d.name_en
            bar = _BarFlowable(d.count, max_count, width=80, height=8, color=COLOR_SQUARE)
            rows.append([Paragraph(_esc(name), styles["body"]), Paragraph(str(d.count), styles["body"]), bar])
        tbl = Table(rows, colWidths=[(A4[0] - 40 * mm) - 120, 30, 90])
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.3, COLOR_RULE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(tbl)

    story.append(Spacer(1, 12))

    # Top emotions
    if summary.top_emotions:
        story.append(Paragraph(_esc(_tr("top_emotions", lang)), styles["section"]))
        max_count = max(e.count for e in summary.top_emotions) or 1
        rows = []
        for e in summary.top_emotions[:3]:
            name = e.name_id if lang == "id" else e.name_en
            bar = _BarFlowable(e.count, max_count, width=80, height=8, color=COLOR_CIRCLE)
            rows.append(
                [
                    Paragraph(_esc(name), styles["body"]),
                    Paragraph(str(e.count), styles["body"]),
                    Paragraph(f"{e.avg_intensity:.1f}/10", styles["body"]),
                    bar,
                ]
            )
        tbl = Table(rows, colWidths=[(A4[0] - 40 * mm) - 190, 40, 60, 90])
        tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.3, COLOR_RULE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(tbl)

    story.append(Spacer(1, 14))

    # Entries
    story.append(Paragraph(_esc(_tr("entries_in_period", lang)), styles["section"]))
    if not entries:
        story.append(Paragraph(_esc(_tr("no_entries", lang)), styles["body"]))
    else:
        for e in entries:
            distortions = entry_distortion_map.get(e.id, [])
            emotions = entry_emotion_map.get(e.id, [])
            distortion_names = [(d.name_id if lang == "id" else d.name_en) for d in distortions]
            emotion_names = [(em.name_id if lang == "id" else em.name_en) for em in emotions]
            story.append(_entry_card(e, distortion_names, emotion_names, styles, lang))
            story.append(Spacer(1, 8))

    story.append(Spacer(1, 6))

    # Winning moments
    story.append(Paragraph(_esc(_tr("wins_in_period", lang)), styles["section"]))
    if not wins:
        story.append(Paragraph(_esc(_tr("no_wins", lang)), styles["body"]))
    else:
        for w in wins:
            head = f"<b>{w.moment_date.isoformat()}</b>"
            if w.tag:
                head += f"  ·  <font color='#6B7280'>{_esc(w.tag)}</font>"
            story.append(Paragraph(head, styles["body"]))
            story.append(Paragraph(_esc(w.text).replace("\n", "<br/>"), styles["body"]))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 6))

    # Therapist feedback
    story.append(Paragraph(_esc(_tr("feedback_in_period", lang)), styles["section"]))
    if not feedback_items:
        story.append(Paragraph(_esc(_tr("no_feedback", lang)), styles["body"]))
    else:
        for fb, entry in feedback_items:
            head = (
                f"<b>{_esc(fb.author_name)}</b>  ·  "
                f"<font color='#6B7280'>{fb.created_at.date().isoformat()} · "
                f"{_tr('entry_date', lang)} {entry.entry_date.isoformat()}</font>"
            )
            story.append(Paragraph(head, styles["body"]))
            story.append(Paragraph(_esc(fb.note).replace("\n", "<br/>"), styles["body"]))
            story.append(Spacer(1, 6))

    doc.build(
        story,
        onFirstPage=lambda c, d: _draw_footer(c, d, footer),
        onLaterPages=lambda c, d: _draw_footer(c, d, footer),
    )
    return buf.getvalue()


def _entry_card(
    entry: Entry,
    distortion_names: list[str],
    emotion_names: list[str],
    styles: dict[str, ParagraphStyle],
    lang: Lang,
) -> Flowable:
    inner: list[Flowable] = []
    head = (
        f"<b>{entry.entry_date.isoformat()}</b>"
        f"  ·  <font color='#6B7280'>{_tr('intensity', lang)} {entry.emotion_intensity}/10</font>"
    )
    inner.append(Paragraph(head, styles["body"]))
    if emotion_names:
        inner.append(_chips(emotion_names))
        inner.append(Spacer(1, 4))
    if entry.situation:
        inner.append(Paragraph(_esc(_tr("situation", lang)).upper(), styles["label"]))
        inner.append(Paragraph(_esc(entry.situation).replace("\n", "<br/>"), styles["body"]))
    if entry.automatic_thought:
        inner.append(Paragraph(_esc(_tr("automatic_thought", lang)).upper(), styles["label"]))
        inner.append(
            Paragraph(f"&ldquo;{_esc(entry.automatic_thought)}&rdquo;", styles["quote"])
        )
    if distortion_names:
        inner.append(Paragraph(_esc(_tr("distortions", lang)).upper(), styles["label"]))
        inner.append(_chips(distortion_names))
        inner.append(Spacer(1, 4))
    if entry.reframed_thought:
        inner.append(Paragraph(_esc(_tr("reframed_thought", lang)).upper(), styles["label"]))
        inner.append(Paragraph(_esc(entry.reframed_thought).replace("\n", "<br/>"), styles["reframe"]))

    tbl = Table([[inner]], colWidths=[A4[0] - 40 * mm])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
                ("BOX", (0, 0), (-1, -1), 0.4, COLOR_RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return KeepTogether(tbl)


def slugify_filename(s: str | None, fallback: str) -> str:
    if not s:
        return fallback
    cleaned = "".join(c if c.isalnum() or c in "-_" else "-" for c in s.strip())[:60]
    return cleaned or fallback
