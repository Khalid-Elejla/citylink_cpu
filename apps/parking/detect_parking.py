import cv2
import numpy as np
from ultralytics import YOLO
from pydantic import BaseModel
from typing import List, Union

class BBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    track_id: int = 0
    confidence: float = 0.0
    class_id: int

def point_in_polygon(point, polygon):
    return cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), point, False) >= 0

def check_parking_vacancy(frame, boxes, parking_spots):
    relevant_class_ids = [1, 2, 3, 4, 5, 7]  # Indices corresponding to ["car", "van", "bus", "truck", "heavy truck", "motorcycle"]
    
    available_spots = 0
    for i, spot in enumerate(parking_spots):
        occupied = False
        for box in boxes:
            if box.class_id in relevant_class_ids:
                center = ((box.x1 + box.x2) / 2, (box.y1 + box.y2) / 2)
                if point_in_polygon(center, spot):
                    occupied = True
                    break

        color = (0, 0, 255) if occupied else (0, 255, 0)
        cv2.polylines(frame, [np.array(spot, dtype=np.int32)], isClosed=True, color=color, thickness=2)
        
        if not occupied:
            available_spots += 1
    
    return frame, available_spots


# def check_parking_vacancy(frame, boxes, parking_spots):
#     # Specify the class IDs for the relevant vehicle types
#     relevant_class_ids = [1, 2, 3, 4, 5, 7]  # Indices corresponding to ["car", "van", "bus", "truck", "heavy truck", "motorcycle"]

#     for i, spot in enumerate(parking_spots):
#         occupied = False
#         for box in boxes:
#             # Check if the box belongs to one of the relevant vehicle classes
#             if box.class_id in relevant_class_ids:
#                 center = ((box.x1 + box.x2) / 2, (box.y1 + box.y2) / 2)
#                 if point_in_polygon(center, spot):
#                     occupied = True
#                     break

#         color = (0, 0, 255) if occupied else (0, 255, 0)
#         cv2.polylines(frame, [np.array(spot, dtype=np.int32)], isClosed=True, color=color, thickness=2)
        
#     return frame


def draw_bounding_box(frame: np.ndarray, vehicles_bbox: List[BBox], vehicle_names: List[str]) -> np.ndarray:
    for bbox in vehicles_bbox:
        cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (0, 255, 0), 1)
        cv2.putText(frame, f"{vehicle_names[bbox.class_id]} {bbox.track_id} {bbox.confidence:.2f}", 
                    (bbox.x1, bbox.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame



def run_parking_detection(video_source: Union[str, int], model_path: str, parking_spots: list, stframe, show_boxes: bool, counter_display):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        stframe.text("Error: Could not open video source.")
        print("Error: Could not open video source.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) if isinstance(video_source, str) else 30
    output_path = 'output5.mp4' if isinstance(video_source, str) else None

    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not out.isOpened():
            stframe.text("Error: Could not open video writer.")
            return

    vehicle_names = ["person","car", "van", "bus", "truck", "heavy truck", "bicycle", "motorcycle"]

    total_spots = len(parking_spots)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to read frame from video source.")
            break

        results = model.track(frame)
        if not results:
            print("No results from model tracking.")
            continue

        bboxes = [BBox(
            x1=int(box.xyxy[0].tolist()[0]),
            y1=int(box.xyxy[0].tolist()[1]),
            x2=int(box.xyxy[0].tolist()[2]),
            y2=int(box.xyxy[0].tolist()[3]),
            track_id=int(box.id) if box.id is not None else 0,
            confidence=box.conf.item(),
            class_id=int(box.cls.item())
        ) for r in results for box in r.boxes]

        if show_boxes:
            frame = draw_bounding_box(frame, bboxes, vehicle_names)

        frame, available_spots = check_parking_vacancy(frame, bboxes, parking_spots)

        # Update the counter in the third column
        #counter_display.write(f"**{available_spots}/{total_spots}**", unsafe_allow_html=True)
        # Update the counter in the third column with large text
        counter_display.markdown(
            f"""
            <div style="text-align: center; font-size: 20px; font-weight: bold;">
            <div style="text-align: center; font-size: 30px; font-weight: bold;">
                Available Spots:<br>{available_spots}<br><br>
                Total Spots:<br>{total_spots}
            </div>
            """,
            unsafe_allow_html=True
        )

        if output_path:
            out.write(frame)

        stframe.image(frame, channels="BGR")

    cap.release()
    if output_path:
        out.release()
        stframe.text(f"Saved output video to {output_path}")

# def run_parking_detection(video_source: Union[str, int], model_path: str, parking_spots: list, stframe, show_boxes: bool):
#     model = YOLO(model_path)
#     cap = cv2.VideoCapture(video_source)
    
#     if not cap.isOpened():
#         stframe.text("Error: Could not open video source.")
#         print("Error: Could not open video source.")
#         return

#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = cap.get(cv2.CAP_PROP_FPS) if isinstance(video_source, str) else 30
#     output_path = 'output5.mp4' if isinstance(video_source, str) else None

#     if output_path:
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
#         if not out.isOpened():
#             stframe.text("Error: Could not open video writer.")
#             return

#     vehicle_names = ["person","car", "van", "bus", "truck", "heavy truck", "bicycle", "motorcycle"]

#     while True:
#         ret, frame = cap.read()
#         if not ret or frame is None:
#             print("Failed to read frame from video source.")
#             break

#         results = model.track(frame)
#         if not results:
#             print("No results from model tracking.")
#             continue

#         bboxes = [BBox(
#             x1=int(box.xyxy[0].tolist()[0]),
#             y1=int(box.xyxy[0].tolist()[1]),
#             x2=int(box.xyxy[0].tolist()[2]),
#             y2=int(box.xyxy[0].tolist()[3]),
#             track_id=int(box.id) if box.id is not None else 0,
#             confidence=box.conf.item(),
#             class_id=int(box.cls.item())
#         ) for r in results for box in r.boxes]

#         if show_boxes:
#             frame = draw_bounding_box(frame, bboxes, vehicle_names)

#         frame = check_parking_vacancy(frame, bboxes, parking_spots)

#         if output_path:
#             out.write(frame)

#         stframe.image(frame, channels="BGR")

#     cap.release()
#     if output_path:
#         out.release()
#         stframe.text(f"Saved output video to {output_path}")