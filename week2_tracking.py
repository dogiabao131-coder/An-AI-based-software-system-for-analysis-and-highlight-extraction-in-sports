from ultralytics import YOLO
import cv2



model = YOLO('yolov8n.pt') # Bạn có thể dùng v8 hoặc v11

video_path = "video_test.mp4" 
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    success, frame = cap.read()
    if success:
       
        results = model.track(
    frame, 
    persist=True, 
    conf=0.25,      
    iou=0.5,        
    tracker="botsort.yaml", 
    classes=[0, 32]
)

        # Lấy khung hình đã được vẽ ID và Bounding Box
        annotated_frame = results[0].plot()

        #  Hiển thị kết quả
        cv2.imshow("Week 2: Object Tracking", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()