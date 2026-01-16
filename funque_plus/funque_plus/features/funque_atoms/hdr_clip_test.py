import os
import numpy as np
import cv2
from ..funque_atoms import hdr_clipping_fex as fex


def _read_mp4_y_frames(path, stride=1):
    """Read MP4 video frames and extract Y (luma) channel, sampling every stride frames."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV cannot open: {path}")
    
    try:
        # Optimize stride handling: skip frames without reading when stride > 1
        if stride > 1:
            idx = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if (idx % stride) == 0:
                    # BGR -> YUV, take Y channel in [0,1]
                    Y = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)[:, :, 0].astype(np.float32) / 255.0
                    yield Y
                idx += 1
        else:
            # stride == 1: process every frame
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                Y = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)[:, :, 0].astype(np.float32) / 255.0
                yield Y
    finally:
        cap.release()


def _read_yuv420_8bit_luma(path, width, height, stride=1):
    """Read 8-bit YUV420 video and extract Y (luma) plane, sampling every stride frames."""
    frame_size_y = width * height
    frame_size_uv = frame_size_y // 2  # U/2 + V/2 for 4:2:0
    frame_size_total = frame_size_y + frame_size_uv
    
    with open(path, "rb") as f:
        fi = 0
        while True:
            y = f.read(frame_size_y)
            if len(y) < frame_size_y:
                break
            uv = f.read(frame_size_uv)
            if len(uv) < frame_size_uv:
                break
            
            if (fi % stride) == 0:
                Y = np.frombuffer(y, dtype=np.uint8).reshape((height, width))
                yield Y.astype(np.float32) / 255.0
            fi += 1


def _read_yuv420_p010_luma(path, width, height, stride=1):
    """Read P010 (10-bit) YUV420 video and extract Y plane, sampling every stride frames."""
    # P010: 10-bit in 16-bit little-endian words. Luma plane first (width*height*2 bytes)
    frame_size_y_bytes = width * height * 2
    # UV plane also exists but we skip it (width*height*2 bytes for P010 4:2:0)
    frame_size_uv_bytes = (width * height * 2) // 2
    frame_size_total_bytes = frame_size_y_bytes + frame_size_uv_bytes
    
    with open(path, "rb") as f:
        fi = 0
        while True:
            ybytes = f.read(frame_size_y_bytes)
            if len(ybytes) < frame_size_y_bytes:
                break
            uvbytes = f.read(frame_size_uv_bytes)
            if len(uvbytes) < frame_size_uv_bytes:
                break
            
            if (fi % stride) == 0:
                Yn = np.frombuffer(ybytes, dtype=np.uint16).reshape((height, width))
                # 10-bit is in the most significant bits of the 16-bit word for P010
                Y10 = (Yn >> 6).astype(np.float32)  # keep top 10 bits
                Y = Y10 / 1023.0
                yield Y
            fi += 1

def detect_brightness_clipping_video(
    path,
    *,
    input_type="auto",      # "auto", "mp4", "yuv8", "p010"
    width=None,
    height=None,
    frame_stride=2,         # sample every Nth frame
    treat_mp4_as_hdr=False, # OpenCV is usually tone-mapped SDR -> keep False
    is_pq_10bit=False,      # True only if you feed PQ codes (P010 or PQ-10bit Y)
    area_min_px=64,
    thr_norm=0.96,          # a bit looser than 0.99 for SDR/tone-mapped
    thr_nits_ratio=0.96,
    peak_nits=None
):
    # pick reader
    ext = os.path.splitext(path)[1].lower()
    if input_type == "auto":
        if ext in (".mp4", ".mov", ".mkv"):
            input_type = "mp4"
        elif ext == ".yuv":
            # you must also set width/height and know 8-bit vs P010
            raise ValueError("For .yuv, set input_type='yuv8' or 'p010' and provide width/height.")
        else:
            raise ValueError(f"Unknown extension {ext}; set input_type explicitly.")

    if input_type == "mp4":
        frames = _read_mp4_y_frames(path, stride=frame_stride)
        is_hdr = bool(treat_mp4_as_hdr)  # usually False for OpenCV
        pq_10 = False
    elif input_type == "yuv8":
        if not width or not height:
            raise ValueError("yuv8 requires width and height.")
        frames = _read_yuv420_8bit_luma(path, width, height, stride=frame_stride)
        is_hdr = bool(is_pq_10bit)      # if your Y plane actually contains PQ codes (rare for yuv8)
        pq_10 = bool(is_pq_10bit)
    elif input_type == "p010":
        if not width or not height:
            raise ValueError("p010 requires width and height.")
        frames = _read_yuv420_p010_luma(path, width, height, stride=frame_stride)
        is_hdr = True                   # P010 commonly used for HDR10 PQ content
        pq_10 = True
    else:
        raise ValueError(f"Unsupported input_type {input_type}")

    per_frame = []
    for Y in frames:
        f = fex.brightness_clipping_features(
            Y,
            is_hdr=is_hdr,
            is_pq_10bit=pq_10,
            peak_nits=peak_nits,
            area_min_px=area_min_px,
            thr_norm=thr_norm,
            thr_nits_ratio=thr_nits_ratio,
        )
        per_frame.append(f)

    agg = fex.aggregate_brightness_clipping(per_frame)
    return {"per_frame": per_frame, "aggregate": agg}