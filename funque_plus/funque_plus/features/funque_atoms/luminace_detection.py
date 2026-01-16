# funque_plus/run_brightness_clipping.py


import os
import sys
import csv


# Add the parent folder (so imports work)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))


from funque_plus.datasets.HDR_VDC_dataset import dis_videos
from funque_plus.funque_plus.features.funque_atoms.hdr_clip_test import detect_brightness_clipping_video


# Output paths
output_dir = os.path.join("funque_plus", "brightness_results")
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "brightness_clipping_results.csv")


# Prepare CSV header
with open(csv_path, "w", newline="") as f:
   writer = csv.writer(f)
   writer.writerow(["Video_Index", "Video_Name", "Aggregate_Clipping_Value"])


# Loop through all distorted videos
for idx, video_info in dis_videos.items():
   video_path = video_info["path"]
   video_name = os.path.basename(video_path)
   print(f"🔹 Processing {idx}: {video_name}")


   try:
       result = detect_brightness_clipping_video(
           path=video_path,
           input_type="p010",
           width=1920,
           height=1080,
           frame_stride=1,
           is_pq_10bit=True,
       )


       agg_value = result["aggregate"]


       # Write result to CSV
       with open(csv_path, "a", newline="") as f:
           writer = csv.writer(f)
           writer.writerow([idx, video_name, agg_value])


       print(f"✅ Completed: {video_name}, Aggregate: {agg_value}")


   except Exception as e:
       print(f"❌ Error processing {video_name}: {e}")