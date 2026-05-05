import csv
import json
import os

import cv2
from ultralytics import YOLO

try:
    import pytesseract
except ImportError:  # Optional dependency
    pytesseract = None


def get_scorer_candidate(ball_center, boxes, cls_ids, track_ids):
    min_dist = float("inf")
    scorer_id = None
    scorer_box = None
    bx, by = ball_center

    for box, cls, t_id in zip(boxes, cls_ids, track_ids):
        if cls == 0:  # Lớp 'person'
            px, py = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            dist = ((px - bx) ** 2 + (py - by) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                scorer_id = int(t_id)
                scorer_box = box

    return scorer_id, scorer_box


def extract_jersey_number(frame, player_box):
    if pytesseract is None or player_box is None:
        return None

    x1, y1, x2, y2 = [int(v) for v in player_box]
    if x2 <= x1 or y2 <= y1:
        return None

    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return None

    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi_resized = cv2.resize(roi_gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    _, roi_thresh = cv2.threshold(roi_resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    config = "--psm 7 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(roi_thresh, config=config)
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits if digits else None


def analyze_video(
    video_path,
    output_json="analysis_report.json",
    output_csv="analysis_report.csv",
    model_path="yolov8n.pt",
    goal_roi=None,
    cooldown_seconds=10,
    display=False,
    enable_ocr=False,
):
    goal_roi = goal_roi or [100, 350, 480, 580]
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    match_analysis_data = []
    last_goal_frame = -int(fps * cooldown_seconds)
    last_ball_inside = False

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            results = model.track(frame, persist=True, classes=[0, 32], conf=0.25)

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                cls_ids = results[0].boxes.cls.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().numpy()
                ball_seen = False
                for box, cls in zip(boxes, cls_ids):
                    if cls == 32:  # Quả bóng
                        ball_seen = True
                        x1, y1, x2, y2 = box
                        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                        ball_inside = goal_roi[0] < cx < goal_roi[2] and goal_roi[1] < cy < goal_roi[3]

                        if (
                            ball_inside
                            and not last_ball_inside
                            and frame_index - last_goal_frame > fps * cooldown_seconds
                        ):
                            total_seconds = frame_index / fps
                            minutes = int(total_seconds // 60)
                            seconds = int(total_seconds % 60)
                            timestamp_str = f"{minutes:02d}:{seconds:02d}"

                            scorer_id, scorer_box = get_scorer_candidate(
                                (cx, cy), boxes, cls_ids, track_ids
                            )
                            jersey_number = (
                                extract_jersey_number(frame, scorer_box) if enable_ocr else None
                            )

                            event = {
                                "event_type": "Goal",
                                "match_time": timestamp_str,
                                "timestamp_seconds": round(total_seconds, 2),
                                "frame_index": frame_index,
                                "ball_coordinates": [float(cx), float(cy)],
                                "scorer_track_id": scorer_id,
                                "scorer_jersey_number": jersey_number,
                                "video_file": os.path.basename(video_path),
                            }

                            match_analysis_data.append(event)
                            last_goal_frame = frame_index
                            print(f"✅ Ghi nhận phân tích: Bàn thắng tại phút {timestamp_str}")

                        last_ball_inside = ball_inside
                if not ball_seen:
                    last_ball_inside = False
            else:
                last_ball_inside = False

            if display:
                cv2.rectangle(
                    frame,
                    (goal_roi[0], goal_roi[1]),
                    (goal_roi[2], goal_roi[3]),
                    (0, 0, 255),
                    2,
                )
                cv2.putText(
                    frame,
                    "GOAL ZONE",
                    (goal_roi[0], goal_roi[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )
                cv2.imshow("Week 5: Analysis System", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        cap.release()
        if display:
            cv2.destroyAllWindows()

    with open(output_json, "w") as f:
        json.dump(match_analysis_data, f, indent=4)

    if match_analysis_data:
        keys = match_analysis_data[0].keys()
        with open(output_csv, "w", newline="") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(match_analysis_data)
    else:
        with open(output_csv, "w"):
            pass

    print("📂 Đã xuất báo cáo phân tích ra file analysis_report.csv và .json")
    return match_analysis_data


if __name__ == "__main__":
    analyze_video("video_test.mp4", display=True, enable_ocr=False)
