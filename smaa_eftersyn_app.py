"""
smaa_eftersyn_app.py - Små-materiel eftersynsrapport

Standalone Streamlit app with the same startup/confirmation flow used in the
main eftersyn app, but producing a Små-materiel style report.
"""

import os
from datetime import datetime

import fitz
import streamlit as st


LOCKED_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = LOCKED_BASE_DIR
SAVE_DIR = os.path.join(LOCKED_BASE_DIR, "Eftersynsrapporter")
TEMPLATE_PDF = os.path.join(APP_DIR, "Små-materiel_eftersyn_template2.pdf")
ICON_OK = os.path.join(APP_DIR, "Green check mark.jpg")
ICON_FEJL = os.path.join(APP_DIR, "Red X.jpg")
ICON_NR = os.path.join(APP_DIR, "Pink diamond.png")
# Per-icon scaling inside each status cell. 1.00 fills the full box.
ICON_SCALE_OK = 0.92
ICON_SCALE_FEJL = 0.90
ICON_SCALE_NR = 0.92
ICON_OFFSET_FEJL_X = -2.0
ICON_OFFSET_FEJL_Y = 0.0
ICON_OFFSET_NR_X = -11.0
ICON_OFFSET_NR_Y = 0.0
BLUE = (0.0, 0.2, 0.55)
RED = (0.85, 0.0, 0.0)
PINK = (0.95, 0.75, 0.82)
BLACK = (0.0, 0.0, 0.0)

OPTIONS = ["OK", "ikke relevant", "Fejl"]
DISPOSAL_OPTIONS = [
    "Bortskaffet",
    "Genanvendt / sorteret",
    "Returneret til leverandør",
    "Midlertidigt oplagret",
]

CHECK_ITEMS = [
    "Mekaniske dele",
    "Sikkerhedsudstyr",
    "Betjeningsanordninger",
    "Hydraulik og pneumatik",
    "Kæder og remme",
    "Smøring og vedligehold",
    "Bremser (hvis relevant)",
    "Oliestand",
    "Unormale lyder og vibrationer",
    "Dokumenteret i Trace Tool",
    "Påsætning af label for måned og år er sket",
]


def _safe_slug(text: str) -> str:
    keep = []
    for ch in str(text):
        if ch.isalnum() or ch in ("-", "_"):
            keep.append(ch)
        elif ch.isspace():
            keep.append("_")
    slug = "".join(keep).strip("_")
    return slug or "ukendt"


def _init_state() -> None:
    default_technician = str(st.session_state.get("user", "")).strip()
    defaults = {
        "sm_phase": 0,
        "sm_eq": {
            "firma": "Nordic Maskin & Rail P/S",
            "adresse": "Krumtappen 5, 6580 Vamdrup",
            "maskin_nr": "",
            "fabrikat": "",
            "model": "",
            "serie_nr": "",
            "aargang": "",
            "timetaeller": "",
        },
        "sm_technician": default_technician,
        "sm_answers": ["OK"] * len(CHECK_ITEMS),
        "sm_comments": [""] * len(CHECK_ITEMS),
        "sm_other_comment": "",
        "sm_discard": "Nej",
        "sm_discard_reason": "",
        "sm_disposal_action": "",
        "sm_saved": False,
        "sm_saved_path": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _missing_fejl_comments(answers: list[str], comments: list[str]) -> list[str]:
    missing = []
    for idx, ans in enumerate(answers):
        if ans != "Fejl":
            continue
        if str(comments[idx]).strip():
            continue
        missing.append(CHECK_ITEMS[idx])
    return missing


def _clear_rect(page: fitz.Page, rect: fitz.Rect) -> None:
    page.add_redact_annot(rect, fill=(1, 1, 1))


def _clear_text_occurrences(page: fitz.Page, terms: list[str], pad: float = 1.2) -> None:
    for term in terms:
        if not term:
            continue
        for rect in page.search_for(term):
            expanded = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)
            _clear_rect(page, expanded)


def _fit_text_to_width(text: str, max_width: float, fontname: str, fontsize: float) -> str:
    value = str(text or "").strip()
    while value and fitz.get_text_length(value, fontname=fontname, fontsize=fontsize) > max_width:
        value = value[:-1]
    return value


def _is_within_dir(path: str, base_dir: str) -> bool:
    abs_path = os.path.abspath(path)
    abs_base = os.path.abspath(base_dir)
    try:
        return os.path.commonpath([abs_path, abs_base]) == abs_base
    except ValueError:
        return False


def _scaled_rect(rect: fitz.Rect, scale: float) -> fitz.Rect:
    if scale <= 0:
        return fitz.Rect(rect)
    cx = (rect.x0 + rect.x1) / 2
    cy = (rect.y0 + rect.y1) / 2
    half_w = (rect.width * scale) / 2
    half_h = (rect.height * scale) / 2
    return fitz.Rect(cx - half_w, cy - half_h, cx + half_w, cy + half_h)


def _scaled_rect_xy(rect: fitz.Rect, scale_x: float, scale_y: float) -> fitz.Rect:
    cx = (rect.x0 + rect.x1) / 2
    cy = (rect.y0 + rect.y1) / 2
    half_w = (rect.width * scale_x) / 2
    half_h = (rect.height * scale_y) / 2
    return fitz.Rect(cx - half_w, cy - half_h, cx + half_w, cy + half_h)


def _offset_rect(rect: fitz.Rect, dx: float = 0.0, dy: float = 0.0) -> fitz.Rect:
    return fitz.Rect(rect.x0 + dx, rect.y0 + dy, rect.x1 + dx, rect.y1 + dy)


def _write_page_number(page: fitz.Page, value: str) -> None:
    # Template page 1 already prints "Side: 1/"; the "/" ends at x≈559, text at y≈754-762.
    # We only need to write the final digit right after the "/" in black bold-italic.
    last_digit = str(value).strip()[-1]
    page_no_rect = fitz.Rect(559, 750, 578, 765)
    page.draw_rect(page_no_rect, color=None, fill=(1, 1, 1), overlay=True)
    page.insert_text((560, 762), last_digit, fontsize=10.6, fontname="hebi", color=BLACK)


def _mark_disposal_action_checkbox(page: fitz.Page, action: str) -> None:
    boxes = {
        "Bortskaffet": fitz.Rect(183, 376, 191, 384),
        "Genanvendt / sorteret": fitz.Rect(322, 376, 330, 384),
        "Returneret til leverandør": fitz.Rect(179, 394, 187, 402),
        "Midlertidigt oplagret": fitz.Rect(322, 394, 330, 402),
    }
    box = boxes.get(str(action or "").strip())
    if not box:
        return
    # Draw an X in the selected checkbox.
    inset = 1.2
    page.draw_line((box.x0 + inset, box.y0 + inset), (box.x1 - inset, box.y1 - inset), color=BLUE, width=1.0, overlay=True)
    page.draw_line((box.x0 + inset, box.y1 - inset), (box.x1 - inset, box.y0 + inset), color=BLUE, width=1.0, overlay=True)


def _draw_small_report(
    path_out: str,
    eq: dict,
    tech: str,
    answers: list[str],
    comments: list[str],
    other_comment: str,
    discard: str,
    discard_reason: str,
    disposal_action: str,
) -> None:
    if not _is_within_dir(path_out, SAVE_DIR):
        raise ValueError(f"Rapport må kun gemmes i: {SAVE_DIR}")
    if not os.path.exists(TEMPLATE_PDF):
        raise FileNotFoundError(f"Template mangler: {TEMPLATE_PDF}")
    for icon_path in (ICON_OK, ICON_FEJL, ICON_NR):
        if not os.path.exists(icon_path):
            raise FileNotFoundError(f"Status ikon mangler: {icon_path}")

    doc = fitz.open(TEMPLATE_PDF)
    discard_is_yes = str(discard).strip().lower() == "ja"
    if not discard_is_yes and doc.page_count > 1:
        doc.delete_page(1)

    page = doc[0]



    row_bands = [
        (209, 249),
        (249, 290),
        (290, 331),
        (331, 371),
        (371, 411),
        (411, 449),
        (449, 490),
        (490, 529),
        (529, 564),
        (564, 603),
        (603, 643),
    ]


    type_text = " / ".join(x for x in [eq.get("fabrikat", ""), eq.get("model", "")] if str(x).strip())

    for idx, ans in enumerate(answers):
        y0, y1 = row_bands[idx]
        # Dedicated status columns under header symbols (OK / Fejl / ikke relevant).
        ok_box = fitz.Rect(221, y0 + 9, 245, y1 - 9)
        fejl_box = fitz.Rect(250, y0 + 9, 280, y1 - 9)
        nr_box = fitz.Rect(289, y0 + 9, 319, y1 - 9)

        if ans == "OK":
            clear_ok = fitz.Rect(ok_box.x0 + 1, ok_box.y0 + 1, ok_box.x1 - 1, ok_box.y1 - 1)
            page.draw_rect(clear_ok, color=None, fill=(1, 1, 1), overlay=True)
            page.insert_image(_scaled_rect(ok_box, ICON_SCALE_OK), filename=ICON_OK, keep_proportion=True, overlay=True)
        elif ans == "Fejl":
            fejl_target = _scaled_rect_xy(fejl_box, scale_x=0.72, scale_y=ICON_SCALE_FEJL)
            page.insert_image(
                _offset_rect(fejl_target, ICON_OFFSET_FEJL_X, ICON_OFFSET_FEJL_Y),
                filename=ICON_FEJL,
                keep_proportion=True,
                overlay=True,
            )
        elif ans == "ikke relevant":
            nr_target = _scaled_rect_xy(nr_box, scale_x=0.72, scale_y=ICON_SCALE_NR)
            page.insert_image(
                _offset_rect(nr_target, ICON_OFFSET_NR_X, ICON_OFFSET_NR_Y),
                filename=ICON_NR,
                keep_proportion=True,
                overlay=True,
            )

        comment = str(comments[idx] or "").strip()
        if comment:
            page.insert_text((320, y0 + 12), comment[:20], fontsize=8, fontname="helv", color=BLUE)

    # Other comments
    other_text = str(other_comment or "").strip()[:30]
    page.insert_text((40, 670), other_text, fontsize=9, fontname="helv", color=BLUE)

    discard_value = "JA" if discard_is_yes else "NEJ"
    discard_rect = fitz.Rect(529, 647, 566, 661)
    discard_value = _fit_text_to_width(discard_value, discard_rect.width - 4, "helv", 10.0)
    discard_x = discard_rect.x0 + ((discard_rect.width - fitz.get_text_length(discard_value, fontname="helv", fontsize=10.0)) / 2)
    page.insert_text((discard_x, 658), discard_value, fontsize=10.0, fontname="helv", color=BLUE)

    # Bottom row values only (labels are part of the template)
    page.insert_text((145, 720), datetime.now().strftime("%d-%m-%Y"), fontsize=10.5, fontname="helv", color=BLUE)
    tech_rect = fitz.Rect(408, 708, 562, 729)
    tech_value = _fit_text_to_width(str(tech or "").strip(), tech_rect.width - 8, "helv", 9.8)
    page.insert_textbox(
        tech_rect,
        tech_value,
        fontsize=9.8,
        fontname="helv",
        color=BLUE,
        align=fitz.TEXT_ALIGN_LEFT,
    )

    page.insert_text((34, 150), type_text or "-", fontsize=14, fontname="helv", color=BLUE)
    page.insert_text((442, 150), str(eq.get("maskin_nr", "") or "-"), fontsize=14, fontname="helv", color=BLUE)
    _write_page_number(page, "1/2" if discard_is_yes else "1/1")

    if discard_is_yes and doc.page_count > 1:
        page2 = doc[1]
        page2.insert_text((36, 150), type_text or "-", fontsize=13.5, fontname="helv", color=BLUE)
        page2.insert_text((447, 150), str(eq.get("maskin_nr", "") or "-"), fontsize=13.5, fontname="helv", color=BLUE)
        _mark_disposal_action_checkbox(page2, disposal_action)
        reason_rect = fitz.Rect(42, 214, 552, 289)
        page2.insert_textbox(
            reason_rect,
            str(discard_reason or "").strip(),
            fontsize=10,
            fontname="helv",
            color=BLUE,
            align=fitz.TEXT_ALIGN_LEFT,
        )
        if other_comment.strip():
            remarks_rect = fitz.Rect(42, 632, 552, 648)
            page2.insert_textbox(
                remarks_rect,
                str(other_comment).strip(),
                fontsize=9.5,
                fontname="helv",
                color=BLUE,
                align=fitz.TEXT_ALIGN_LEFT,
            )
        date_box_rect = fitz.Rect(176, 685, 317, 709)
        mech_box_rect = fitz.Rect(468, 685, 592, 709)
        page2.insert_textbox(
            date_box_rect,
            datetime.now().strftime("%d-%m-%Y"),
            fontsize=10.2,
            fontname="helv",
            color=BLUE,
            align=fitz.TEXT_ALIGN_LEFT,
        )
        page2.insert_textbox(
            mech_box_rect,
            str(tech or "").strip()[:22],
            fontsize=10.2,
            fontname="helv",
            color=BLUE,
            align=fitz.TEXT_ALIGN_LEFT,
        )

    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    doc.save(path_out)
    doc.close()


st.set_page_config(
    page_title="Små-materiel eftersyn",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        div[data-testid="stButton"] > button {
            min-height: 3.2rem;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 10px;
        }
        div[role="radiogroup"] {
            flex-wrap: nowrap !important;
            white-space: nowrap !important;
            gap: 0.8rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

_init_state()
ss = st.session_state

eq = ss.sm_eq
fab = eq.get("fabrikat", "")
mod = eq.get("model", "")
mnr = eq.get("maskin_nr", "")
mech = ss.sm_technician or "?"
if fab or mod or mnr:
    parts = " / ".join(filter(None, [fab, mod, mnr]))
    st.caption(f"🔧 {parts} - Mekaniker: {mech}")


if ss.sm_phase == 0:
    st.title("Små-materiel eftersyn")
    st.subheader("Bekræft udstyr og mekaniker")
    st.info(
        "Udfyld felterne nedenfor (forhåndsudfyldt fra QR-scan) "
        "og indtast dit navn for at starte eftersynet."
    )

    with st.form("sm_setup"):
        c1, c2 = st.columns(2)
        maskin_nr = c1.text_input("Maskin nr.", value=eq["maskin_nr"])
        fabrikat = c2.text_input("Fabrikat", value=eq["fabrikat"])
        model = c1.text_input("Model", value=eq["model"])
        serie_nr = c2.text_input("Serie / mærkat nr.", value=eq["serie_nr"])
        aargang = c1.text_input("Årgang", value=eq["aargang"])
        timetaeller = c2.text_input("Timetæller (H)", value=eq["timetaeller"])
        technician = st.text_input(
            "Mekaniker - dit navn",
            value=ss.sm_technician or str(st.session_state.get("user", "")),
        )
        started = st.form_submit_button(
            "▶️  Start Små-materiel eftersyn",
            use_container_width=True,
            type="primary",
        )

    if started:
        if not technician.strip():
            st.error("Angiv dit navn som mekaniker.")
        else:
            ss.sm_eq.update(
                maskin_nr=maskin_nr,
                fabrikat=fabrikat,
                model=model,
                serie_nr=serie_nr,
                aargang=aargang,
                timetaeller=timetaeller,
            )
            ss.sm_technician = technician.strip()
            ss.sm_answers = ["OK"] * len(CHECK_ITEMS)
            ss.sm_comments = [""] * len(CHECK_ITEMS)
            ss.sm_phase = 1
            st.rerun()


elif ss.sm_phase == 1:
    st.title("Små-materiel eftersyn - samlet tabel")
    st.caption("Alle punkter starter som OK. Vælg ikke relevant eller Fejl ved behov.")

    for idx, item in enumerate(CHECK_ITEMS):
        st.markdown(f"**{item}**")
        c1, c2 = st.columns([3, 2])
        current = ss.sm_answers[idx] if ss.sm_answers[idx] in OPTIONS else "OK"
        default_ix = OPTIONS.index(current)
        ss.sm_answers[idx] = c1.radio(
            f"Status_{idx}",
            options=OPTIONS,
            index=default_ix,
            key=f"sm_status_{idx}",
            horizontal=True,
            label_visibility="collapsed",
        )
        ss.sm_comments[idx] = c2.text_area(
            f"Bemærkning_{idx}",
            value=ss.sm_comments[idx],
            key=f"sm_comment_{idx}",
            placeholder="Bemærkning...",
            height=80,
            label_visibility="collapsed",
        )
        st.divider()

    ss.sm_other_comment = st.text_area(
        "Andre bemærkninger",
        value=ss.sm_other_comment,
        placeholder="Skriv eventuelle samlede bemærkninger her...",
        height=120,
    )
    ss.sm_discard = st.radio(
        "Skal den kasseres?",
        options=["Nej", "Ja"],
        index=0 if ss.sm_discard == "Nej" else 1,
        horizontal=True,
    )
    if ss.sm_discard == "Ja":
        st.info(
            "Vælg én miljøhåndtering for det kasserede udstyr. "
            "Valget markeres i kasseringsrapporten under 'Håndtering af kasseret materiale'."
        )
        current_action = ss.sm_disposal_action if ss.sm_disposal_action in DISPOSAL_OPTIONS else DISPOSAL_OPTIONS[0]
        ss.sm_disposal_action = st.radio(
            "Miljøhåndtering (vælg én)",
            options=DISPOSAL_OPTIONS,
            index=DISPOSAL_OPTIONS.index(current_action),
            horizontal=False,
        )
        ss.sm_discard_reason = st.text_area(
            "Årsag til kassering",
            value=ss.sm_discard_reason,
            placeholder="Kort forklaring på hvorfor kassation foretages...",
            height=120,
        )
    else:
        ss.sm_discard_reason = ""
        ss.sm_disposal_action = ""

    c_back, c_save = st.columns(2)
    if c_back.button("⬅️ Tilbage", use_container_width=True):
        ss.sm_phase = 0
        st.rerun()

    if c_save.button("💾 Gem eftersynsrapport", use_container_width=True, type="primary"):
        missing = _missing_fejl_comments(ss.sm_answers, ss.sm_comments)
        if missing:
            st.error(
                "Kommentar er obligatorisk for alle punkter markeret som Fejl. "
                "Tilføj kommentar før du gemmer."
            )
            st.warning("Mangler kommentar ved: " + ", ".join(missing))
        elif ss.sm_discard == "Ja" and not str(ss.sm_discard_reason).strip():
            st.error("Angiv årsag til kassering før du gemmer rapporten.")
        elif ss.sm_discard == "Ja" and not str(ss.sm_disposal_action).strip():
            st.error("Vælg miljøhåndtering (Bortskaffet / Genanvendt / Returneret / Midlertidigt oplagret) før du gemmer.")
        else:
            ident = _safe_slug(eq.get("maskin_nr") or eq.get("serie_nr") or "ukendt")
            today = datetime.now().strftime("%Y%m%d")
            filename = f"Små-materiel_eftersyn_{ident}_{today}.pdf"
            out_path = os.path.join(SAVE_DIR, filename)
            if not _is_within_dir(out_path, SAVE_DIR):
                st.error(f"Rapport må kun gemmes i: {SAVE_DIR}")
                st.stop()
            try:
                _draw_small_report(
                    out_path,
                    eq=ss.sm_eq,
                    tech=ss.sm_technician,
                    answers=ss.sm_answers,
                    comments=ss.sm_comments,
                    other_comment=ss.sm_other_comment,
                    discard=ss.sm_discard,
                    discard_reason=ss.sm_discard_reason,
                    disposal_action=ss.sm_disposal_action,
                )
                ss.sm_saved = True
                ss.sm_saved_path = out_path
            except Exception as exc:
                st.error(f"Kunne ikke generere rapport: {exc}")

    if ss.sm_saved and ss.sm_saved_path:
        st.success(f"Rapport gemt: {ss.sm_saved_path}")
