import cv2
import json
import csv
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture("video_test.mp4")

# Lấy thông số video để tính toán thời gian
fps = cap.get(cv2.CAP_PROP_FPS)
match_analysis_data = []
goal_roi = [100, 350, 480, 580] # Tọa độ bạn đã chỉnh ở tuần 3

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    results = model.track(frame, persist=True, classes=[0, 32], conf=0.25)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        cls_ids = results[0].boxes.cls.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().numpy()

        for box, cls, track_id in zip(boxes, cls_ids, track_ids):
            if cls == 32:  # Quả bóng
                x1, y1, x2, y2 = box
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                if goal_roi[0] < cx < goal_roi[2] and goal_roi[1] < cy < goal_roi[3]:
                    # TÍNH TOÁN PHÚT THỨ MẤY TRONG TRẬN ĐẤU
                    total_seconds = frame_index / fps
                    minutes = int(total_seconds // 60)
                    seconds = int(total_seconds % 60)
                    timestamp_str = f"{minutes:02d}:{seconds:02d}"

                    # PHÂN TÍCH CẦU THỦ GẦN BÓNG NHẤT (Người ghi bàn)
                    # (Logic đơn giản: Tìm người có ID gần tọa độ bóng nhất trong frame này)
                    
                    event = {
                        "event_type": "Goal",
                        "match_time": timestamp_str,
                        "frame_index": frame_index,
                        "ball_coordinates": [float(cx), float(cy)],
                        "video_file": "video_test.mp4"
                    }

                    # Chống lưu trùng (giống tuần 3)
                    if not match_analysis_data or (frame_index - match_analysis_data[-1]['frame_index'] > fps * 10):
                        match_analysis_data.append(event)
                        print(f"✅ Ghi nhận phân tích: Bàn thắng tại phút {timestamp_str}")

    cv2.imshow("Week 5: Analysis System", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break

cap.release()
cv2.destroyAllWindows()

# --- XUẤT DỮ LIỆU PHÂN TÍCH ---
# 1. Xuất file JSON (Để lập trình Web tuần sau dùng)
with open('analysis_report.json', 'w') as f:
    json.dump(match_analysis_data, f, indent=4)

# 2. Xuất file CSV (Để Bảo nộp kèm báo cáo đồ án Word/Excel)
keys = match_analysis_data[0].keys() if match_analysis_data else []
with open('analysis_report.csv', 'w', newline='') as f:
    dict_writer = csv.DictWriter(f, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(match_analysis_data)

print("📂 Đã xuất báo cáo phân tích ra file analysis_report.csv và .json")