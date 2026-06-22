
import io
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SwimWearable Dashboard",
    page_icon="🏊‍♀️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(50, 180, 255, 0.18), transparent 35%),
        radial-gradient(circle at top right, rgba(0, 204, 177, 0.14), transparent 30%),
        linear-gradient(180deg, #F6FBFF 0%, #EEF7FB 45%, #F9FCFF 100%);
}

.main-title {
    font-size: 44px;
    font-weight: 800;
    color: #06283D;
    margin-bottom: 0px;
    letter-spacing: -1.2px;
}

.subtitle {
    font-size: 17px;
    color: #486575;
    margin-top: 4px;
    margin-bottom: 28px;
}

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: #06283D;
    margin-top: 12px;
    margin-bottom: 8px;
}

.kpi-card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(110, 180, 210, 0.35);
    border-radius: 22px;
    padding: 18px 18px 16px 18px;
    box-shadow: 0 12px 35px rgba(8, 55, 82, 0.08);
    min-height: 118px;
}

.kpi-label {
    color: #607988;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.kpi-value {
    color: #06283D;
    font-size: 34px;
    font-weight: 800;
    line-height: 1.05;
}

.kpi-unit {
    color: #6D8795;
    font-size: 14px;
    font-weight: 600;
    margin-left: 4px;
}

.kpi-note {
    color: #8095A0;
    font-size: 12px;
    margin-top: 8px;
}

.info-box {
    background: rgba(255, 255, 255, 0.76);
    border: 1px solid rgba(95, 165, 195, 0.35);
    border-left: 5px solid #0088CC;
    border-radius: 18px;
    padding: 16px 18px;
    color: #244657;
    box-shadow: 0 10px 25px rgba(8, 55, 82, 0.06);
}

.metric-pill {
    display: inline-block;
    background: #E7F7FF;
    color: #006C9E;
    border: 1px solid #B8E7FA;
    border-radius: 999px;
    padding: 5px 10px;
    margin: 3px 5px 3px 0px;
    font-size: 12px;
    font-weight: 700;
}

div[data-testid="stMetricValue"] {
    color: #06283D;
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F1FAFF 100%);
}

.plot-container {
    border-radius: 20px;
}



.hero-card {
    position: relative;
    background: linear-gradient(135deg, rgba(4,42,63,.98), rgba(0,119,182,.92));
    border-radius: 30px;
    padding: 34px 36px;
    margin-bottom: 24px;
    box-shadow: 0 22px 55px rgba(4,42,63,.18);
    overflow: hidden;
}
.hero-card:before {
    content: "";
    position: absolute;
    right: -80px;
    top: -100px;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    background: rgba(32,214,197,.22);
}
.hero-card:after {
    content: "";
    position: absolute;
    right: 130px;
    bottom: -120px;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    background: rgba(255,255,255,.10);
}
.hero-title {
    position: relative;
    z-index: 2;
    color: white;
    font-size: 48px;
    font-weight: 900;
    letter-spacing: -1.5px;
    line-height: 1.02;
    margin-bottom: 10px;
}
.hero-subtitle {
    position: relative;
    z-index: 2;
    color: rgba(255,255,255,.82);
    font-size: 17px;
    max-width: 880px;
    margin-bottom: 18px;
}
.hero-pill {
    position: relative;
    z-index: 2;
    display: inline-block;
    color: white;
    background: rgba(255,255,255,.14);
    border: 1px solid rgba(255,255,255,.24);
    border-radius: 999px;
    padding: 7px 11px;
    font-size: 12px;
    font-weight: 800;
    margin: 4px 6px 4px 0;
}
.glass-card {
    background: rgba(255,255,255,.82);
    border: 1px solid rgba(0,119,182,.14);
    border-radius: 24px;
    padding: 18px 20px;
    box-shadow: 0 14px 38px rgba(4,42,63,.08);
    backdrop-filter: blur(12px);
}
.good-box {
    background: rgba(234,255,250,.94);
    border: 1px solid rgba(32,214,197,.28);
    border-left: 5px solid #20D6C5;
    border-radius: 18px;
    padding: 15px 17px;
    color: #164A43;
    margin: 10px 0;
}
.warning-box {
    background: rgba(255,250,235,.94);
    border: 1px solid rgba(246,174,45,.30);
    border-left: 5px solid #F6AE2D;
    border-radius: 18px;
    padding: 15px 17px;
    color: #5B4A1F;
    margin: 10px 0;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
# ============================================================

CANONICAL_COLUMNS = [
    "time_s",
    "HR",
    "SpO2",
    "accel_dynamic",
    "total_strokes",
    "lap_strokes",
    "stroke_rate_spm",
    "breaths",
    "breath_right",
    "breath_left",
    "glide_time_s",
    "lap_velocity_m_s",
    "distance_per_stroke_m",
    "lap_number",
    "turn_detected",
    "turn_duration_s",
]

COLUMN_UNITS = {
    "time_s": "s",
    "HR": "bpm",
    "SpO2": "%",
    "accel_dynamic": "g",
    "total_strokes": "count",
    "lap_strokes": "count",
    "stroke_rate_spm": "strokes/min",
    "breaths": "count",
    "breath_right": "count",
    "breath_left": "count",
    "glide_time_s": "s",
    "lap_velocity_m_s": "m/s",
    "distance_per_stroke_m": "m/stroke",
    "lap_number": "count",
    "turn_detected": "0/1",
    "turn_duration_s": "s",
}

DISPLAY_NAMES = {
    "time_s": "Time",
    "HR": "Heart rate",
    "SpO2": "SpO₂",
    "accel_dynamic": "Dynamic acceleration",
    "total_strokes": "Total strokes",
    "lap_strokes": "Lap strokes",
    "stroke_rate_spm": "Stroke rate",
    "breaths": "Breaths",
    "breath_right": "Right breaths",
    "breath_left": "Left breaths",
    "glide_time_s": "Glide time",
    "lap_velocity_m_s": "Lap velocity",
    "distance_per_stroke_m": "Distance per stroke",
    "lap_number": "Lap number",
    "turn_detected": "Turn detected",
    "turn_duration_s": "Turn duration",
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def normalize_key(name: str) -> str:
    """Normalize column names with or without units."""
    name = str(name).strip()
    name = re.sub(r"\[.*?\]", "", name)
    name = name.replace("%", "percent")
    name = name.replace("/", "_")
    name = name.replace("-", "_")
    name = name.replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_").lower()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map flexible Arduino/CSV/Excel headers to canonical app columns."""
    aliases = {
        "time_s": "time_s",
        "time": "time_s",
        "hr": "HR",
        "heart_rate": "HR",
        "heart_rate_bpm": "HR",
        "hr_bpm": "HR",
        "spo2": "SpO2",
        "spo2_percent": "SpO2",
        "accel_dynamic": "accel_dynamic",
        "dynamic_acceleration": "accel_dynamic",
        "total_strokes": "total_strokes",
        "lap_strokes": "lap_strokes",
        "stroke_rate_spm": "stroke_rate_spm",
        "stroke_rate": "stroke_rate_spm",
        "breaths": "breaths",
        "breath_right": "breath_right",
        "right_breaths": "breath_right",
        "breath_left": "breath_left",
        "left_breaths": "breath_left",
        "glide_time_s": "glide_time_s",
        "glide_time": "glide_time_s",
        "lap_velocity_m_s": "lap_velocity_m_s",
        "lap_velocity": "lap_velocity_m_s",
        "distance_per_stroke_m": "distance_per_stroke_m",
        "distance_per_stroke": "distance_per_stroke_m",
        "lap_number": "lap_number",
        "turn_detected": "turn_detected",
        "turn_duration_s": "turn_duration_s",
        "turn_duration": "turn_duration_s",
    }

    rename = {}
    for col in df.columns:
        key = normalize_key(col)
        if key in aliases:
            rename[col] = aliases[key]

    df = df.rename(columns=rename)

    # Keep only known columns when present, but do not fail if some are missing.
    available = [c for c in CANONICAL_COLUMNS if c in df.columns]
    df = df[available].copy()

    for col in available:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "time_s" in df.columns:
        df = df.dropna(subset=["time_s"])
        df = df.sort_values("time_s").reset_index(drop=True)

    # Fill counters forward only after numeric conversion.
    counter_cols = [
        "total_strokes",
        "lap_strokes",
        "breaths",
        "breath_right",
        "breath_left",
        "lap_number",
        "turn_detected",
    ]
    for col in counter_cols:
        if col in df.columns:
            df[col] = df[col].ffill().fillna(0)

    return df


def find_header_line(raw_text: str) -> str:
    """If the CSV contains serial debug lines, cut the file from the real header."""
    lines = raw_text.splitlines()
    for i, line in enumerate(lines):
        normalized = line.replace(" ", "").lower()
        if "time_s" in normalized and "hr" in normalized and "spo2" in normalized:
            return "\n".join(lines[i:])
    return raw_text


@st.cache_data(show_spinner=False)
def load_data_from_bytes(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    suffix = Path(file_name).suffix.lower()

    if suffix in [".xlsx", ".xls"]:
        sheets = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        # Prefer the sheet that contains time_s.
        selected = None
        for _, sheet_df in sheets.items():
            cols = [normalize_key(c) for c in sheet_df.columns]
            if "time_s" in cols or "time" in cols:
                selected = sheet_df
                break
        if selected is None:
            selected = next(iter(sheets.values()))
        df = selected

    else:
        raw = file_bytes.decode("utf-8", errors="ignore")
        raw = find_header_line(raw)
        df = pd.read_csv(io.StringIO(raw))

    return standardize_columns(df)


def load_demo_if_available() -> pd.DataFrame | None:
    for candidate in ["prova1.xlsx", "SWIM00.CSV", "swim_data.csv"]:
        path = Path(candidate)
        if path.exists():
            return load_data_from_bytes(path.name, path.read_bytes())
    return None


def safe_last(df: pd.DataFrame, col: str, default=0):
    if col not in df.columns or df.empty:
        return default
    valid = df[col].dropna()
    if valid.empty:
        return default
    return valid.iloc[-1]


def safe_mean_positive(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return np.nan
    values = df.loc[df[col] > 0, col]
    if values.empty:
        return np.nan
    return values.mean()


def safe_max(df: pd.DataFrame, col: str, default=0):
    if col not in df.columns or df.empty:
        return default
    return df[col].max()


def fmt_value(value, decimals=1, empty="—"):
    if value is None or pd.isna(value):
        return empty
    if isinstance(value, (int, np.integer)) or float(value).is_integer():
        return f"{int(value)}"
    return f"{float(value):.{decimals}f}"


def kpi_card(label: str, value, unit: str = "", note: str = "", decimals: int = 1):
    value_text = fmt_value(value, decimals=decimals)
    st.markdown(
        f"""
<div class="kpi-card">
  <div class="kpi-label">{label}</div>
  <div>
    <span class="kpi-value">{value_text}</span>
    <span class="kpi-unit">{unit}</span>
  </div>
  <div class="kpi-note">{note}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def add_event_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "total_strokes" in df.columns:
        df["stroke_event"] = df["total_strokes"].diff().fillna(df["total_strokes"]).gt(0)
    else:
        df["stroke_event"] = False

    if "breaths" in df.columns:
        df["breath_event"] = df["breaths"].diff().fillna(df["breaths"]).gt(0)
    else:
        df["breath_event"] = False

    if "turn_detected" in df.columns:
        df["turn_event"] = df["turn_detected"].fillna(0).eq(1)
    else:
        df["turn_event"] = False

    if "glide_time_s" in df.columns:
        df["glide_event"] = df["glide_time_s"].diff().fillna(0).gt(0)
    else:
        df["glide_event"] = False

    return df


def line_chart(df, y_cols, title, y_title, markers=None, threshold=None):
    available = [c for c in y_cols if c in df.columns]
    if not available:
        st.info(f"No data available for {title}.")
        return

    fig = go.Figure()

    for col in available:
        fig.add_trace(
            go.Scatter(
                x=df["time_s"],
                y=df[col],
                mode="lines",
                name=f"{DISPLAY_NAMES.get(col, col)} [{COLUMN_UNITS.get(col, '')}]",
                line=dict(width=3),
            )
        )

    if threshold is not None:
        fig.add_hline(
            y=threshold,
            line_dash="dot",
            annotation_text=f"Threshold {threshold}",
            annotation_position="top left",
        )

    if markers is not None and not markers.empty:
        fig.add_trace(
            go.Scatter(
                x=markers["time_s"],
                y=markers["y"],
                mode="markers",
                name=markers["name"].iloc[0] if "name" in markers.columns else "Events",
                marker=dict(size=10, symbol="diamond"),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Time [s]",
        yaxis_title=y_title,
        template="plotly_white",
        height=430,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)


def build_events_timeline(df: pd.DataFrame):
    events = []

    event_specs = [
        ("stroke_event", "Stroke", 4),
        ("breath_event", "Breath", 3),
        ("turn_event", "Turn", 2),
        ("glide_event", "Glide", 1),
    ]

    for col, label, ypos in event_specs:
        if col in df.columns:
            temp = df.loc[df[col], ["time_s"]].copy()
            if not temp.empty:
                temp["event"] = label
                temp["y"] = ypos
                events.append(temp)

    if not events:
        return pd.DataFrame(columns=["time_s", "event", "y"])

    return pd.concat(events, ignore_index=True)


def plot_event_timeline(events_df: pd.DataFrame):
    if events_df.empty:
        st.info("No events detected yet. Move the device or upload a longer acquisition.")
        return

    fig = px.scatter(
        events_df,
        x="time_s",
        y="event",
        color="event",
        title="Detected events timeline",
        labels={"time_s": "Time [s]", "event": "Event"},
    )
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
    fig.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text="Event",
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_breathing_side(df: pd.DataFrame):
    right = safe_last(df, "breath_right", 0)
    left = safe_last(df, "breath_left", 0)

    side_df = pd.DataFrame(
        {
            "Side": ["Right", "Left"],
            "Breaths": [right, left],
        }
    )

    fig = px.bar(
        side_df,
        x="Side",
        y="Breaths",
        text="Breaths",
        title="Breathing side distribution",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        template="plotly_white",
        height=360,
        yaxis_title="Breaths [count]",
        xaxis_title="Breathing side",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def lap_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "turn_event" not in df.columns:
        df = add_event_columns(df)

    turn_rows = df.loc[df["turn_event"]].copy()

    if turn_rows.empty:
        return pd.DataFrame(
            columns=[
                "lap_number",
                "turn_time_s",
                "lap_velocity_m_s",
                "distance_per_stroke_m",
                "turn_duration_s",
            ]
        )

    keep = [
        c
        for c in [
            "lap_number",
            "time_s",
            "lap_velocity_m_s",
            "distance_per_stroke_m",
            "turn_duration_s",
        ]
        if c in turn_rows.columns
    ]

    out = turn_rows[keep].copy()
    out = out.rename(columns={"time_s": "turn_time_s"})
    return out.reset_index(drop=True)


def download_button_for_clean_data(df: pd.DataFrame, key: str):
    columns_to_export = [c for c in CANONICAL_COLUMNS if c in df.columns]
    event_columns = [
        c for c in ["stroke_event", "breath_event", "turn_event", "glide_event"]
        if c in df.columns and c not in columns_to_export
    ]

    export_df = df[columns_to_export + event_columns].copy()
    csv = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download cleaned CSV",
        data=csv,
        file_name="swimwearable_cleaned_data.csv",
        mime="text/csv",
        use_container_width=True,
        key=key,
    )



def render_message(text: str, kind: str = "info"):
    css_class = "info-box"
    if kind == "good":
        css_class = "good-box"
    elif kind == "warning":
        css_class = "warning-box"
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)


def get_positive_mean(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return np.nan
    values = df.loc[df[col] > 0, col]
    return np.nan if values.empty else values.mean()


def get_positive_max(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return np.nan
    values = df.loc[df[col] > 0, col]
    return np.nan if values.empty else values.max()


def get_positive_min(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return np.nan
    values = df.loc[df[col] > 0, col]
    return np.nan if values.empty else values.min()


def compact_number(value, decimals=1):
    if value is None or pd.isna(value):
        return "—"
    try:
        value = float(value)
    except Exception:
        return str(value)
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.{decimals}f}"


def make_session_insights(df, duration_s, mean_hr, mean_spo2, total_strokes, total_breaths, completed_laps):
    insights = []

    if pd.isna(mean_hr):
        insights.append(("warning", "<b>HR non disponibile:</b> controlla contatto del MAX30102 e isolamento dalla luce."))
    elif mean_hr > 160:
        insights.append(("warning", "<b>HR medio alto:</b> può indicare sforzo elevato oppure rumore PPG durante movimento."))
    else:
        insights.append(("good", "<b>HR acquisito:</b> il segnale cardiaco è utilizzabile per trend e visualizzazione del prototipo."))

    if pd.isna(mean_spo2):
        insights.append(("warning", "<b>SpO₂ non disponibile:</b> il contatto ottico potrebbe non essere stabile."))
    elif mean_spo2 < 94:
        insights.append(("warning", "<b>SpO₂ media bassa:</b> interpretala con cautela, il MAX30102 in movimento non è medical-grade."))
    else:
        insights.append(("good", "<b>SpO₂ coerente:</b> i valori medi sono nel range atteso per una demo prototipale."))

    if total_strokes <= 0:
        insights.append(("warning", "<b>Nessuna bracciata rilevata:</b> prova ad abbassare la soglia di accelerazione o acquisire movimenti più marcati."))
    else:
        insights.append(("good", "<b>Stroke detection attivo:</b> le bracciate vengono riconosciute da picchi di accelerazione dinamica."))

    if total_breaths <= 0:
        insights.append(("warning", "<b>Nessuna respirazione rilevata:</b> valuta di cambiare asse del giroscopio nel codice Arduino."))
    else:
        right = safe_last(df, "breath_right", 0)
        left = safe_last(df, "breath_left", 0)
        if right + left > 0 and abs(right - left) / (right + left) > 0.75:
            insights.append(("warning", "<b>Respirazione molto monolaterale:</b> può essere voluta, ma è un feedback tecnico utile."))
        else:
            insights.append(("good", "<b>Breathing pattern rilevato:</b> puoi analizzare conteggio e lato di respirazione."))

    if completed_laps <= 0:
        insights.append(("warning", "<b>Nessuna virata rilevata:</b> velocità vasca e distance per stroke restano vuote o pari a zero."))
    else:
        insights.append(("good", "<b>Lap metrics disponibili:</b> la virata aggiorna velocità vasca e avanzamento per bracciata."))

    return insights


def build_markdown_report(session_label, swimmer_name, duration_s, mean_hr, mean_spo2, total_strokes, total_breaths, completed_laps, mean_stroke_rate, last_lap_velocity, last_dps, last_glide, insights):
    lines = [
        "# SwimWearable session report",
        "",
        f"**Session:** {session_label}",
        f"**Swimmer:** {swimmer_name}",
        "",
        "## Overview",
        f"- Duration: {compact_number(duration_s, 1)} s",
        f"- Completed laps: {compact_number(completed_laps, 0)}",
        f"- Total strokes: {compact_number(total_strokes, 0)}",
        f"- Total breaths: {compact_number(total_breaths, 0)}",
        "",
        "## Physiology",
        f"- Mean HR: {compact_number(mean_hr, 0)} bpm",
        f"- Mean SpO₂: {compact_number(mean_spo2, 0)} %",
        "",
        "## Technique",
        f"- Mean stroke rate: {compact_number(mean_stroke_rate, 1)} strokes/min",
        f"- Last glide time: {compact_number(last_glide, 2)} s",
        f"- Last lap velocity: {compact_number(last_lap_velocity, 2)} m/s",
        f"- Last distance per stroke: {compact_number(last_dps, 2)} m/stroke",
        "",
        "## Automatic notes",
    ]
    for kind, text in insights:
        clean = re.sub(r"<.*?>", "", text)
        prefix = "✅" if kind == "good" else "⚠️"
        lines.append(f"- {prefix} {clean}")
    return "\n".join(lines)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="hero-card">
  <div class="hero-title">🏊‍♀️ SwimWearable Analytics</div>
  <div class="hero-subtitle">
    Dashboard interattiva per visualizzare i dati acquisiti da Arduino Nano 33 BLE, MAX30102, IMU, BLE e microSD.
    Carica il file della sessione e analizza fisiologia, tecnica, eventi, virate e metriche per vasca.
  </div>
  <span class="hero-pill">MAX30102 HR + SpO₂</span>
  <span class="hero-pill">Head-mounted IMU</span>
  <span class="hero-pill">Stroke rate</span>
  <span class="hero-pill">Breathing side</span>
  <span class="hero-pill">Laps & turns</span>
  <span class="hero-pill">CSV / XLSX</span>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## Upload data")
    uploaded_file = st.file_uploader(
        "Upload the file saved from SD card or exported from Excel",
        type=["csv", "xlsx", "xls"],
    )

    if "uploaded_file_signature" not in st.session_state:
        st.session_state.uploaded_file_signature = None
    if "analyze_requested" not in st.session_state:
        st.session_state.analyze_requested = False

    current_signature = None
    if uploaded_file is not None:
        current_signature = f"{uploaded_file.name}_{uploaded_file.size}"

    if current_signature != st.session_state.uploaded_file_signature:
        st.session_state.uploaded_file_signature = current_signature
        st.session_state.analyze_requested = False

    analyze_button = st.button(
        "🔍 Analyze uploaded file",
        use_container_width=True,
        type="primary",
        disabled=uploaded_file is None,
    )

    if analyze_button:
        st.session_state.analyze_requested = True

    st.markdown("---")
    st.markdown("## Settings")

    stroke_threshold = st.number_input(
        "Stroke acceleration threshold [g]",
        min_value=0.01,
        max_value=2.00,
        value=0.18,
        step=0.01,
        help="Same threshold used in Arduino for stroke detection. Here it is only shown as reference in the plot.",
    )

    hr_min, hr_max = st.slider(
        "Physiological HR display range [bpm]",
        min_value=30,
        max_value=220,
        value=(40, 200),
    )

    show_raw = st.toggle("Show raw table by default", value=False)

    st.markdown("---")
    st.markdown("## Session info")
    swimmer_name = st.text_input("Swimmer", value="Prototype athlete")
    session_label = st.text_input("Session label", value="Wearable test")
    pool_length = st.number_input("Pool length [m]", min_value=10.0, max_value=100.0, value=25.0, step=5.0)
    session_notes = st.text_area("Notes", value="", height=90)

    st.markdown("---")
    st.markdown("## Data format")
    st.markdown(
        """
<span class="metric-pill">CSV</span>
<span class="metric-pill">XLSX</span>
<span class="metric-pill">Arduino SD</span>
<span class="metric-pill">Serial export</span>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# DATA LOADING
# ============================================================

df = None

if uploaded_file is not None:
    if not st.session_state.analyze_requested:
        st.markdown(
            """
<div class="info-box">
File loaded successfully. Press <b>Analyze uploaded file</b> in the sidebar to process it and generate the dashboard.
</div>
""",
            unsafe_allow_html=True,
        )
        st.stop()

    try:
        df = load_data_from_bytes(uploaded_file.name, uploaded_file.getvalue())
    except Exception as exc:
        st.error(f"Could not read the uploaded file: {exc}")
        st.stop()

else:
    demo_df = load_demo_if_available()
    if demo_df is not None:
        df = demo_df
        st.info("Loaded local demo file found in the app folder.")
    else:
        st.markdown(
            """
<div class="info-box">
Upload your <b>SWIMxx.CSV</b> file from the SD card or the Excel file created from Arduino data.
The expected columns are: <b>time_s, HR, SpO2, accel_dynamic, total_strokes, lap_strokes, stroke_rate_spm,
breaths, breath_right, breath_left, glide_time_s, lap_velocity_m_s, distance_per_stroke_m,
lap_number, turn_detected, turn_duration_s</b>.
</div>
""",
            unsafe_allow_html=True,
        )
        st.stop()

if df is None or df.empty:
    st.warning("No valid numeric data found in the file.")
    st.stop()

missing_cols = [c for c in CANONICAL_COLUMNS if c not in df.columns]
if missing_cols:
    st.warning(f"Some expected columns are missing: {', '.join(missing_cols)}")

df = add_event_columns(df)

st.success(f"File analyzed correctly: {len(df)} samples loaded.")


# ============================================================
# SUMMARY VALUES
# ============================================================

duration_s = safe_max(df, "time_s", 0)
mean_hr = safe_mean_positive(df, "HR")
mean_spo2 = safe_mean_positive(df, "SpO2")
total_strokes = safe_last(df, "total_strokes", 0)
total_breaths = safe_last(df, "breaths", 0)
completed_laps = safe_last(df, "lap_number", 0)
mean_stroke_rate = safe_mean_positive(df, "stroke_rate_spm")
last_glide = safe_last(df, "glide_time_s", 0)
last_lap_velocity = safe_last(df.loc[df.get("lap_velocity_m_s", pd.Series([0])) > 0] if "lap_velocity_m_s" in df.columns else df, "lap_velocity_m_s", np.nan)
last_dps = safe_last(df.loc[df.get("distance_per_stroke_m", pd.Series([0])) > 0] if "distance_per_stroke_m" in df.columns else df, "distance_per_stroke_m", np.nan)
max_hr = get_positive_max(df, "HR")
min_spo2 = get_positive_min(df, "SpO2")
sample_rate_est = len(df) / duration_s if duration_s else np.nan
last_turn_duration = safe_last(df, "turn_duration_s", 0)
turn_events_count = int(df["turn_event"].sum()) if "turn_event" in df.columns else 0
stroke_events_count = int(df["stroke_event"].sum()) if "stroke_event" in df.columns else 0
breath_events_count = int(df["breath_event"].sum()) if "breath_event" in df.columns else 0
insights = make_session_insights(df, duration_s, mean_hr, mean_spo2, total_strokes, total_breaths, completed_laps)
report_text = build_markdown_report(session_label, swimmer_name, duration_s, mean_hr, mean_spo2, total_strokes, total_breaths, completed_laps, mean_stroke_rate, last_lap_velocity, last_dps, last_glide, insights)


# ============================================================
# SESSION CONTROL PANEL
# ============================================================

st.markdown('<div class="section-title">Session control panel</div>', unsafe_allow_html=True)
meta_left, meta_right = st.columns([2.3, 1])
with meta_left:
    st.markdown(
        f"""
<div class="glass-card">
  <b>Session:</b> {session_label}<br>
  <b>Swimmer:</b> {swimmer_name}<br>
  <b>Pool length:</b> {pool_length:g} m<br>
  <span class="metric-pill">Samples: {compact_number(len(df), 0)}</span>
  <span class="metric-pill">Duration: {compact_number(duration_s, 1)} s</span>
  <span class="metric-pill">Estimated rate: {compact_number(sample_rate_est, 1)} Hz</span>
</div>
""",
        unsafe_allow_html=True,
    )
with meta_right:
    st.download_button(
        "📋 Download session report",
        data=report_text.encode("utf-8"),
        file_name="swimwearable_session_report.md",
        mime="text/markdown",
        use_container_width=True,
        key="download_session_report",
    )
    download_button_for_clean_data(df, key="download_clean_data_top")


# ============================================================
# KPI CARDS
# ============================================================

st.markdown('<div class="section-title">Session overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Duration", duration_s, "s", "Total acquisition time", decimals=1)
with c2:
    kpi_card("Heart rate", mean_hr, "bpm", "Mean value, zeros excluded", decimals=0)
with c3:
    kpi_card("SpO₂", mean_spo2, "%", "Mean value, zeros excluded", decimals=0)
with c4:
    kpi_card("Completed laps", completed_laps, "laps", "Based on detected turns", decimals=0)

c5, c6, c7, c8 = st.columns(4)
with c5:
    kpi_card("Total strokes", total_strokes, "strokes", "Cumulative count", decimals=0)
with c6:
    kpi_card("Stroke rate", mean_stroke_rate, "strokes/min", "Mean positive value", decimals=1)
with c7:
    kpi_card("Breaths", total_breaths, "breaths", "Cumulative count", decimals=0)
with c8:
    kpi_card("Last glide", last_glide, "s", "Last detected glide phase", decimals=2)

c9, c10, c11, c12 = st.columns(4)
with c9:
    kpi_card("Max HR", max_hr, "bpm", "Peak valid heart rate", decimals=0)
with c10:
    kpi_card("Min SpO₂", min_spo2, "%", "Minimum valid oxygen saturation", decimals=0)
with c11:
    kpi_card("Turn events", turn_events_count, "events", "Detected from gyro peaks", decimals=0)
with c12:
    kpi_card("Last turn", last_turn_duration, "s", "Duration of last detected turn", decimals=2)


# ============================================================
# TABS
# ============================================================

tab_overview, tab_physiology, tab_technique, tab_laps, tab_insights, tab_raw = st.tabs(
    ["🌊 Overview", "❤️ Physiology", "🏊 Technique", "🔁 Laps & turns", "💡 Insights", "📄 Raw data"]
)


# ------------------------------------------------------------
# OVERVIEW
# ------------------------------------------------------------

with tab_overview:
    st.markdown('<div class="section-title">Main signals</div>', unsafe_allow_html=True)

    line_chart(
        df,
        ["accel_dynamic", "stroke_rate_spm"],
        "Dynamic acceleration and stroke rate",
        "Value",
        threshold=stroke_threshold,
    )

    events_df = build_events_timeline(df)
    plot_event_timeline(events_df)

    st.markdown(
        """
<div class="info-box">
<b>How to read this dashboard:</b> stroke events come from dynamic acceleration peaks,
breathing events from head rotation detected by the gyroscope, turns from high angular velocity,
and lap velocity / distance per stroke are updated after a detected turn.
</div>
""",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# PHYSIOLOGY
# ------------------------------------------------------------

with tab_physiology:
    st.markdown('<div class="section-title">Physiological monitoring</div>', unsafe_allow_html=True)

    physio_cols = [c for c in ["HR", "SpO2"] if c in df.columns]
    if physio_cols:
        fig = go.Figure()

        if "HR" in df.columns:
            hr_plot = df.copy()
            hr_plot.loc[(hr_plot["HR"] < hr_min) | (hr_plot["HR"] > hr_max), "HR"] = np.nan
            fig.add_trace(
                go.Scatter(
                    x=hr_plot["time_s"],
                    y=hr_plot["HR"],
                    mode="lines",
                    name="Heart rate [bpm]",
                    line=dict(width=3),
                )
            )

        if "SpO2" in df.columns:
            spo2_plot = df.copy()
            spo2_plot.loc[spo2_plot["SpO2"] <= 0, "SpO2"] = np.nan
            fig.add_trace(
                go.Scatter(
                    x=spo2_plot["time_s"],
                    y=spo2_plot["SpO2"],
                    mode="lines",
                    name="SpO₂ [%]",
                    line=dict(width=3),
                    yaxis="y2",
                )
            )

        fig.update_layout(
            title="Heart rate and SpO₂ over time",
            xaxis_title="Time [s]",
            yaxis=dict(title="Heart rate [bpm]"),
            yaxis2=dict(title="SpO₂ [%]", overlaying="y", side="right", range=[80, 105]),
            template="plotly_white",
            height=460,
            margin=dict(l=20, r=20, t=60, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No physiological columns found.")

    col_a, col_b = st.columns(2)

    with col_a:
        if "HR" in df.columns and (df["HR"] > 0).any():
            fig_hr_hist = px.histogram(
                df.loc[df["HR"] > 0],
                x="HR",
                nbins=25,
                title="Heart rate distribution",
                labels={"HR": "Heart rate [bpm]"},
            )
            fig_hr_hist.update_layout(template="plotly_white", height=360)
            st.plotly_chart(fig_hr_hist, use_container_width=True)
        else:
            st.info("HR is currently zero or unavailable. Check MAX30102 contact quality.")

    with col_b:
        if "SpO2" in df.columns and (df["SpO2"] > 0).any():
            fig_spo2_hist = px.histogram(
                df.loc[df["SpO2"] > 0],
                x="SpO2",
                nbins=15,
                title="SpO₂ distribution",
                labels={"SpO2": "SpO₂ [%]"},
            )
            fig_spo2_hist.update_layout(template="plotly_white", height=360)
            st.plotly_chart(fig_spo2_hist, use_container_width=True)
        else:
            st.info("SpO₂ is currently zero or unavailable. Check MAX30102 contact quality.")


# ------------------------------------------------------------
# TECHNIQUE
# ------------------------------------------------------------

with tab_technique:
    st.markdown('<div class="section-title">Swimming technique metrics</div>', unsafe_allow_html=True)

    stroke_markers = pd.DataFrame()
    if "stroke_event" in df.columns and "accel_dynamic" in df.columns:
        stroke_markers = df.loc[df["stroke_event"], ["time_s", "accel_dynamic"]].copy()
        stroke_markers = stroke_markers.rename(columns={"accel_dynamic": "y"})
        stroke_markers["name"] = "Detected strokes"

    line_chart(
        df,
        ["accel_dynamic"],
        "Dynamic acceleration with stroke threshold",
        "Dynamic acceleration [g]",
        markers=stroke_markers,
        threshold=stroke_threshold,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        line_chart(
            df,
            ["stroke_rate_spm"],
            "Stroke rate over time",
            "Stroke rate [strokes/min]",
        )

    with col_b:
        plot_breathing_side(df)

    col_c, col_d = st.columns(2)

    with col_c:
        line_chart(
            df,
            ["total_strokes", "breaths"],
            "Cumulative strokes and breaths",
            "Count",
        )

    with col_d:
        if "glide_time_s" in df.columns:
            line_chart(
                df,
                ["glide_time_s"],
                "Detected glide time",
                "Glide time [s]",
            )
        else:
            st.info("No glide data available.")


# ------------------------------------------------------------
# LAPS & TURNS
# ------------------------------------------------------------

with tab_laps:
    st.markdown('<div class="section-title">Lap and turn analysis</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Last lap velocity", last_lap_velocity, "m/s", "Updated after turn", decimals=2)
    with c2:
        kpi_card("Distance per stroke", last_dps, "m/stroke", "Updated after turn", decimals=2)
    with c3:
        kpi_card("Turn duration", safe_last(df, "turn_duration_s", 0), "s", "Last detected turn", decimals=2)

    laps = lap_summary(df)

    if not laps.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            if "lap_velocity_m_s" in laps.columns:
                fig_lap_v = px.bar(
                    laps,
                    x="lap_number",
                    y="lap_velocity_m_s",
                    text="lap_velocity_m_s",
                    title="Lap velocity by lap",
                    labels={"lap_number": "Lap", "lap_velocity_m_s": "Velocity [m/s]"},
                )
                fig_lap_v.update_traces(texttemplate="%{text:.2f}", textposition="outside")
                fig_lap_v.update_layout(template="plotly_white", height=380)
                st.plotly_chart(fig_lap_v, use_container_width=True)

        with col_b:
            if "distance_per_stroke_m" in laps.columns:
                fig_dps = px.bar(
                    laps,
                    x="lap_number",
                    y="distance_per_stroke_m",
                    text="distance_per_stroke_m",
                    title="Distance per stroke by lap",
                    labels={
                        "lap_number": "Lap",
                        "distance_per_stroke_m": "Distance per stroke [m/stroke]",
                    },
                )
                fig_dps.update_traces(texttemplate="%{text:.2f}", textposition="outside")
                fig_dps.update_layout(template="plotly_white", height=380)
                st.plotly_chart(fig_dps, use_container_width=True)

        st.markdown("#### Lap summary table")
        st.dataframe(laps, use_container_width=True)
    else:
        st.info("No turns detected yet, so lap-level metrics are still empty.")


# ------------------------------------------------------------
# INSIGHTS
# ------------------------------------------------------------

with tab_insights:
    st.markdown('<div class="section-title">Automatic interpretation</div>', unsafe_allow_html=True)

    for kind, text in insights:
        render_message(text, kind)

    st.markdown('<div class="section-title">Prototype logic</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="glass-card">
<b>Stroke detection</b> is based on peaks of dynamic acceleration measured by the head-mounted IMU.<br>
<b>Breathing detection</b> uses head rotation from the gyroscope.<br>
<b>Turn detection</b> uses high angular velocity peaks plus a cooldown window.<br>
<b>Lap velocity</b> and <b>distance per stroke</b> are updated after a detected turn.
<br><br>
<span style="color:#607D8B;">These values are intended for prototype visualization and technical feedback, not for medical use.</span>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Report preview")
    st.text_area("Generated session report", report_text, height=360)

    if session_notes.strip():
        st.markdown("#### User notes")
        st.info(session_notes)


# ------------------------------------------------------------
# RAW DATA
# ------------------------------------------------------------

with tab_raw:
    st.markdown('<div class="section-title">Raw and cleaned data</div>', unsafe_allow_html=True)

    st.markdown("#### Column units")
    units_df = pd.DataFrame(
        {
            "Column": [c for c in CANONICAL_COLUMNS if c in df.columns],
            "Name": [DISPLAY_NAMES.get(c, c) for c in CANONICAL_COLUMNS if c in df.columns],
            "Unit": [COLUMN_UNITS.get(c, "") for c in CANONICAL_COLUMNS if c in df.columns],
        }
    )
    st.dataframe(units_df, use_container_width=True, hide_index=True)

    st.markdown("#### Data preview")
    if show_raw:
        st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(df.head(40), use_container_width=True)

    download_button_for_clean_data(df, key="download_clean_data_raw_tab")
