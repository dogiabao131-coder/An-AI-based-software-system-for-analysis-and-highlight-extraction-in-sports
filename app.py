import streamlit as st
import pandas as pd
import json
import os
from week4_video_clipper import extract_highlights # Gọi lại hàm tuần 4

# Cấu hình trang web
st.set_page_config(page_title="AI Sports Analysis", layout="wide")

st.title("⚽ Hệ thống Phân tích & Trích xuất Highlight AI")
st.markdown("---")

# 1. Sidebar - Nơi tải video và cấu hình
st.sidebar.header("Cấu hình đầu vào")
uploaded_file = st.sidebar.file_uploader("Tải lên video trận đấu", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # Lưu video tạm thời để xử lý
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    st.sidebar.success("Đã tải video lên thành công!")

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
    if st.button("Bắt đầu phân tích AI"):
        with st.spinner("AI đang quét trận đấu..."):
            # Ở đây bạn sẽ gọi script xử lý của Tuần 5
            # Để demo nhanh, mình sẽ đọc file JSON bạn đã tạo ở Tuần 5
            if os.path.exists('analysis_report.json'):
                with open('analysis_report.json', 'r') as f:
                    data = json.load(f)
                
                df = pd.DataFrame(data)
                st.dataframe(df[['match_time', 'event_type']])
                
                st.success(f"Tìm thấy {len(data)} pha highlight!")
            else:
                st.error("Chưa có dữ liệu phân tích. Hãy chạy AI Scanning trước.")

# 3. Khu vực Highlight Clips
st.markdown("---")
st.subheader("🎬 Danh sách Highlights")

if os.path.exists('highlights'):
    highlight_files = [f for f in os.listdir('highlights') if f.endswith('.mp4')]
    if highlight_files:
        cols = st.columns(len(highlight_files))
        for i, file_name in enumerate(highlight_files):
            with cols[i]:
                st.write(f"Clip {i+1}")
                st.video(f"highlights/{file_name}")
                with open(f"highlights/{file_name}", "rb") as file:
                    st.download_button(label="Tải về", data=file, file_name=file_name)
    else:
        st.write("Chưa có clip nào được trích xuất.")