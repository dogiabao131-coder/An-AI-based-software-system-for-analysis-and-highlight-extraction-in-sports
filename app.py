import logging
import os
import shutil
import uuid

import pandas as pd
import streamlit as st

from week4_video_clipper import SUMMARY_FILENAME, extract_highlights
from week5_analysis_system import analyze_video

logger = logging.getLogger(__name__)

# Cấu hình trang web
st.set_page_config(page_title="AI Sports Analysis", layout="wide")

st.title("⚽ Hệ thống Phân tích & Trích xuất Highlight AI")
st.markdown("---")

# 1. Sidebar - Nơi tải video và cấu hình
st.sidebar.header("Cấu hình đầu vào")
allowed_types = ["mp4", "avi", "mov"]
uploaded_file = st.sidebar.file_uploader("Tải lên video trận đấu", type=allowed_types)
enable_ocr = st.sidebar.checkbox("Bật OCR số áo (tuỳ chọn)", value=False)
allowed_extensions = {f".{ext}" for ext in allowed_types}

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "highlight_files" not in st.session_state:
    st.session_state.highlight_files = []
if "summary_path" not in st.session_state:
    st.session_state.summary_path = None
if "temp_video_path" not in st.session_state:
    st.session_state.temp_video_path = None
if "upload_error" not in st.session_state:
    st.session_state.upload_error = None
if "upload_key" not in st.session_state:
    st.session_state.upload_key = None
if "highlight_folder" not in st.session_state:
    st.session_state.highlight_folder = None

temp_video_path = st.session_state.temp_video_path
upload_error = st.session_state.upload_error
session_temp_dir = os.path.join("temp_uploads", st.session_state.session_id)
session_highlight_dir = os.path.join("highlights", st.session_state.session_id)

if uploaded_file is not None:
    upload_key = (uploaded_file.name, uploaded_file.size)
    is_new_upload = st.session_state.upload_key != upload_key
    if is_new_upload:
        if st.session_state.temp_video_path and os.path.exists(st.session_state.temp_video_path):
            try:
                os.remove(st.session_state.temp_video_path)
            except OSError:
                logger.warning("Không thể xóa file video tạm trước đó.")
        if st.session_state.highlight_folder and os.path.exists(st.session_state.highlight_folder):
            try:
                shutil.rmtree(st.session_state.highlight_folder)
            except OSError:
                logger.warning("Không thể xóa thư mục highlight trước đó.")
        st.session_state.analysis_results = None
        st.session_state.highlight_files = []
        st.session_state.summary_path = None
        st.session_state.upload_key = upload_key

    filename = uploaded_file.name
    extension = os.path.splitext(filename)[1].lower()
    if extension not in allowed_extensions:
        upload_error = (
            "Định dạng file không hợp lệ. Vui lòng tải " + ", ".join(allowed_types) + "."
        )
        temp_video_path = None
        st.session_state.temp_video_path = None
        st.sidebar.error(upload_error)
    else:
        upload_error = None
        temp_video_path = os.path.join(session_temp_dir, f"temp_video{extension}")
        if is_new_upload or not os.path.exists(temp_video_path):
            os.makedirs(session_temp_dir, exist_ok=True)
            try:
                with open(temp_video_path, "wb") as f:
                    f.write(uploaded_file.read())
                st.sidebar.success("Đã tải video lên thành công!")
            except OSError:
                upload_error = "Không thể lưu video tạm thời. Vui lòng thử lại."
                temp_video_path = None
                st.sidebar.error(upload_error)
        st.session_state.temp_video_path = temp_video_path
    st.session_state.upload_error = upload_error
    st.session_state.highlight_folder = session_highlight_dir

# 2. Giao diện chính - Chia làm 2 cột
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📺 Video gốc")
    if uploaded_file and temp_video_path:
        st.video(temp_video_path)
    elif uploaded_file:
        st.error(upload_error or "Không thể hiển thị video đã tải.")
    else:
        st.info("Vui lòng tải video ở thanh bên để bắt đầu.")

with col2:
    st.subheader("📊 Kết quả phân tích (Analysis)")
    if st.button("Bắt đầu phân tích & tạo highlights"):
        if not uploaded_file:
            st.error("Vui lòng tải video trước khi phân tích.")
        elif upload_error:
            st.error(upload_error)
        elif not temp_video_path:
            st.error("Không thể lưu video tạm thời để phân tích.")
        else:
            with st.spinner("AI đang quét trận đấu và cắt highlight..."):
                report_folder = os.path.join("analysis_reports", st.session_state.session_id)
                os.makedirs(report_folder, exist_ok=True)
                output_json = os.path.join(report_folder, "analysis_report.json")
                output_csv = os.path.join(report_folder, "analysis_report.csv")
                data = analyze_video(
                    temp_video_path,
                    output_json=output_json,
                    output_csv=output_csv,
                    enable_ocr=enable_ocr,
                )
                timestamps = [event["timestamp_seconds"] for event in data]
                highlight_files, summary_path = extract_highlights(
                    temp_video_path,
                    timestamps,
                    output_folder=session_highlight_dir,
                )
                st.session_state.analysis_results = data
                st.session_state.highlight_files = highlight_files
                st.session_state.summary_path = summary_path

    if st.session_state.analysis_results is None:
        st.info("Chưa có dữ liệu phân tích. Hãy chạy AI Scanning trước.")
    else:
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
        invalid_scorer_ids = []
        if "scorer_track_id" in df.columns:
            unique_scorers = []
            for value in df["scorer_track_id"].dropna().unique():
                try:
                    unique_scorers.append(int(value))
                except (TypeError, ValueError):
                    invalid_scorer_ids.append(value)
                    continue
            unique_scorers = sorted(set(unique_scorers))
        else:
            unique_scorers = []
        if total_goals == 0:
            st.info("Không phát hiện highlight nào trong trận này.")
        else:
            st.success(f"Tìm thấy {total_goals} pha highlight!")
        if unique_scorers:
            st.info(f"Cầu thủ ghi bàn (track id): {', '.join(map(str, unique_scorers))}")
        if invalid_scorer_ids:
            st.caption(
                "Bỏ qua track id không hợp lệ: "
                + ", ".join(map(str, invalid_scorer_ids))
            )

# 3. Khu vực Highlight Clips
st.markdown("---")
st.subheader("🎬 Danh sách Highlights")

highlight_files = st.session_state.highlight_files
if highlight_files and st.session_state.highlight_folder and (
    st.session_state.summary_path is None
    or not os.path.exists(st.session_state.summary_path)
):
    summary_candidate = os.path.join(st.session_state.highlight_folder, SUMMARY_FILENAME)
    if os.path.exists(summary_candidate):
        st.session_state.summary_path = summary_candidate

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
