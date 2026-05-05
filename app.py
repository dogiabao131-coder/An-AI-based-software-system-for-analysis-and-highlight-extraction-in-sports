import json
import os

import pandas as pd
import streamlit as st

from week4_video_clipper import extract_highlights
from week5_analysis_system import analyze_video

# Cấu hình trang web
st.set_page_config(page_title="AI Sports Analysis", layout="wide")

st.title("⚽ Hệ thống Phân tích & Trích xuất Highlight AI")
st.markdown("---")

# 1. Sidebar - Nơi tải video và cấu hình
st.sidebar.header("Cấu hình đầu vào")
uploaded_file = st.sidebar.file_uploader("Tải lên video trận đấu", type=["mp4", "avi", "mov"])
enable_ocr = st.sidebar.checkbox("Bật OCR số áo (tuỳ chọn)", value=False)

if uploaded_file is not None:
    # Lưu video tạm thời để xử lý
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    st.sidebar.success("Đã tải video lên thành công!")

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "highlight_files" not in st.session_state:
    st.session_state.highlight_files = []
if "summary_path" not in st.session_state:
    st.session_state.summary_path = None

# 2. Giao diện chính - Chia làm 2 cột
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📺 Video gốc")
    if uploaded_file:
        st.video("temp_video.mp4")
    else:
        st.info("Vui lòng tải video ở thanh bên để bắt đầu.")

with col2:
    st.subheader("📊 Kết quả phân tích (Analysis)")
    if st.button("Bắt đầu phân tích & tạo highlights"):
        if not uploaded_file:
            st.error("Vui lòng tải video trước khi phân tích.")
        else:
            with st.spinner("AI đang quét trận đấu và cắt highlight..."):
                data = analyze_video(
                    "temp_video.mp4",
                    output_json="analysis_report.json",
                    output_csv="analysis_report.csv",
                    enable_ocr=enable_ocr,
                )
                timestamps = [event["timestamp_seconds"] for event in data]
                highlight_files, summary_path = extract_highlights("temp_video.mp4", timestamps)
                st.session_state.analysis_results = data
                st.session_state.highlight_files = highlight_files
                st.session_state.summary_path = summary_path

    if st.session_state.analysis_results is None and os.path.exists("analysis_report.json"):
        with open("analysis_report.json", "r") as f:
            st.session_state.analysis_results = json.load(f)

    if st.session_state.analysis_results:
        df = pd.DataFrame(st.session_state.analysis_results)
        display_cols = [
            col
            for col in [
                "match_time",
                "event_type",
                "scorer_track_id",
                "scorer_jersey_number",
            ]
            if col in df.columns
        ]
        st.dataframe(df[display_cols] if display_cols else df)

        total_goals = len(df)
        if "scorer_track_id" in df.columns:
            unique_scorers = sorted(
                {int(s) for s in df["scorer_track_id"].dropna().unique()}
            )
        else:
            unique_scorers = []
        st.success(f"Tìm thấy {total_goals} pha highlight!")
        if unique_scorers:
            st.info(f"Cầu thủ ghi bàn (track id): {', '.join(map(str, unique_scorers))}")
    else:
        st.error("Chưa có dữ liệu phân tích. Hãy chạy AI Scanning trước.")

# 3. Khu vực Highlight Clips
st.markdown("---")
st.subheader("🎬 Danh sách Highlights")

highlight_folder = "highlights"
highlight_files = st.session_state.highlight_files
if not highlight_files and os.path.exists(highlight_folder):
    highlight_files = [
        os.path.join(highlight_folder, f)
        for f in os.listdir(highlight_folder)
        if f.endswith(".mp4") and not f.startswith("final_summary")
    ]

if highlight_files:
    cols = st.columns(len(highlight_files))
    for i, file_path in enumerate(highlight_files):
        file_name = os.path.basename(file_path)
        with cols[i]:
            st.write(f"Clip {i+1}")
            st.video(file_path)
            with open(file_path, "rb") as file:
                st.download_button(label="Tải về", data=file, file_name=file_name)
    if st.session_state.summary_path and os.path.exists(st.session_state.summary_path):
        with open(st.session_state.summary_path, "rb") as file:
            st.download_button(
                label="Tải video tổng hợp",
                data=file,
                file_name=os.path.basename(st.session_state.summary_path),
            )
else:
    st.write("Chưa có clip nào được trích xuất.")
