from ultralytics import YOLO
import cv2

# 1. Tải mô hình đã được huấn luyện sẵn (Pre-trained)
# 'n' là viết tắt của Nano - chạy cực nhanh trên CPU laptop
model = YOLO('yolov8n.pt') 

# 2. Mở file video (thay 'video_test.mp4' bằng file của bạn)
video_path = "video_test.mp4"
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    success, frame = cap.read()
    if success:
        # 3. Chạy nhận diện trên khung hình (chỉ lấy lớp 'người' và 'bóng')
        # classes=[0, 32] tương ứng với 'person' và 'sports ball' trong tập COCO
        results = model.predict(frame, conf=0.5, classes=[0, 32])

        # 4. Hiển thị kết quả lên màn hình
        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Detection", annotated_frame)

        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()