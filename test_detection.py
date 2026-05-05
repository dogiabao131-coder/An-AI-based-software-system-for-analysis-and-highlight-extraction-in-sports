import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="AI Sports Analysis", layout="wide")

st.title("⚽ AI-based Sports Analysis & Highlight System")
st.info("Dự án: Analysis and Highlight Extraction in Sports")

# 1. Sidebar - Tải Video
st.sidebar.header("📥 Input")
uploaded_file = st.sidebar.file_uploader("Chọn video trận đấu", type=["mp4"])

if uploaded_file is not None:
    # Lưu file vào thư mục dự án để Streamlit có thể đọc đường dẫn ổn định
    video_path = "temp_video.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Đã tải video!")

    # 2. Tabs - Chia khu vực hiển thị
    tab1, tab2, tab3 = st.tabs(["📺 Video Gốc", "📊 Phân tích Chi tiết", "🎬 Highlights"])

    with tab1:
        st.subheader("Trình xem video")
        # Hiển thị video trực tiếp từ đường dẫn đã lưu
        st.video(video_path)

    with tab2:
        st.subheader("Kết quả phân tích từ AI")
        if st.button("Chạy phân tích dữ liệu"):
            if os.path.exists('analysis_report.json'):
                with open('analysis_report.json', 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
                
                # Làm đẹp bảng dữ liệu
                st.table(df[['match_time', 'event_type', 'frame_index']])
                st.success(f"Phân tích hoàn tất! Tìm thấy {len(data)} bàn thắng.")
            else:
                st.warning("Cần chạy AI Scanning trước để tạo file report.")

    with tab3:
        st.subheader("Các đoạn Highlight đã trích xuất")
        if os.path.exists('highlights'):
            files = [f for f in os.listdir('highlights') if f.endswith('.mp4')]
            if files:
                for file_name in files:
                    with st.expander(f"Xem clip: {file_name}"):
                        st.video(f"highlights/{file_name}")
            else:
                st.write("Chưa có clip highlight nào.")
else:
    st.warning("👈 Hãy tải video ở thanh bên trái để bắt đầu.")
    # Logic tìm người ghi bàn
def get_scorer_id(ball_center, boxes, cls_ids, track_ids):
    min_dist = float('inf')
    scorer_id = "Unknown"
    bx, by = ball_center
    
    for box, cls, t_id in zip(boxes, cls_ids, track_ids):
        if cls == 0: # Lớp 'person'
            px, py = (box[0]+box[2])/2, (box[1]+box[3])/2
            dist = ((px - bx)**2 + (py - by)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                scorer_id = t_id
    return scorer_id

# Khi phát hiện bàn thắng, gọi hàm:
# scorer = get_scorer_id((cx, cy), boxes, cls_ids, track_ids)
# event["scorer_id"] = int(scorer)