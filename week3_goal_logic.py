import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture("video_test.mp4")
highlight_timestamps = []  # Danh sách chứa các giây có bàn thắng

# Vẽ VÙNG KHUNG THÀNH
goal_roi = [100, 350, 480, 580] 

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    results = model.track(frame, persist=True, classes=[0, 32], conf=0.2)

    # Vẽ vùng khung thành để quan sát
    cv2.rectangle(frame, (goal_roi[0], goal_roi[1]), (goal_roi[2], goal_roi[3]), (0, 0, 255), 2)
    cv2.putText(frame, "GOAL ZONE", (goal_roi[0], goal_roi[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        cls_ids = results[0].boxes.cls.cpu().numpy()

        for box, cls in zip(boxes, cls_ids):
            if cls == 32: # Nếu là quả bóng
                x1, y1, x2, y2 = box
                # Tính tâm quả bóng
                center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2

                # KIỂM TRA BÓNG VÀO KHUNG THÀNH
        if goal_roi[0] < center_x < goal_roi[2] and goal_roi[1] < center_y < goal_roi[3]:
            # Lấy thời gian hiện tại của video 
            current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            
            # Chỉ lưu nếu bàn thắng này cách bàn thắng trước ít nhất 10 giây 
           
            if not highlight_timestamps or (current_time - highlight_timestamps[-1] > 10):
                highlight_timestamps.append(current_time)
                print(f"🚩 Highlight detected at: {current_time:.2f}s")
                
            cv2.putText(frame, "GOAL DETECTED!!!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    

    cv2.imshow("Week 3: Goal Logic", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break

cap.release()
print("-" * 30)
print(f"Tổng cộng có {len(highlight_timestamps)} pha Highlight.")
print(f"Danh sách mốc thời gian: {highlight_timestamps}")
cv2.destroyAllWindows()