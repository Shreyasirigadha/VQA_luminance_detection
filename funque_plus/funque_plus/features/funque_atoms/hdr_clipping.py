# HDR Brightness Clipping Detector
# Detects luminance saturation ("clipping") in HDR (PQ) or SDR frames.
# ------------------------------------------------------------
from __future__ import annotations
import numpy as np
import cv2
from typing import Dict, List

# PQ transfer constants (for HDR10 / ST-2084)
C1 = 3424.0 / 4096.0
C2 = 2413.0 / 128.0
C3 = 2392.0 / 128.0
M1 = 2610.0 / 16384.0
M2 = 2523.0 / 32.0


def pq_eotf(v_norm: np.ndarray) -> np.ndarray:
    """Convert PQ (ST-2084) normalized code values [0,1] → absolute luminance (nits)."""
    V = np.clip(v_norm, 0.0, 1.0).astype(np.float32)
    V_m1 = np.power(V, 1.0 / M2)
    num = np.maximum(V_m1 - C1, 0.0)
    den = C2 - C3 * V_m1
    L = np.power(num / np.maximum(den, 1e-9), 1.0 / M1)
    return L  # in nits


# ------------------------------------------------------------
# Frame-level brightness clipping detector
# ------------------------------------------------------------
def brightness_clipping_features(
    frame_y: np.ndarray,
    *,
    is_hdr: bool = True,
    is_pq_10bit: bool = True,
    peak_nits=None,
    area_min_px=64,
    thr_norm=0.99,
    thr_nits_ratio=0.98,
) -> Dict[str, float]:
    """
    Detect highlight clipping in one frame.
    frame_y: luma array
      - PQ HDR (10-bit → normalized [0,1]) if is_hdr=True
      - or SDR [0,1] if is_hdr=False
    """
    H, W = frame_y.shape[:2]

    # Convert HDR PQ to nits if needed
    if is_hdr and is_pq_10bit:
        y_nits = pq_eotf(frame_y)
        y_work = y_nits
        thr_val = thr_nits_ratio * np.percentile(y_work, 99.99)
    else:
        # SDR path (0–1 normalized)
        y_work = frame_y.astype(np.float32)
        thr_val = thr_norm

    # Gaussian blur to smooth small peaks
    y_blur = cv2.GaussianBlur(y_work, (3, 3), 0)

    # Threshold near max
    clip_mask = y_blur >= thr_val
    clip_mask = cv2.morphologyEx(clip_mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    # Remove tiny blobs
    nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(clip_mask, connectivity=8)
    refined = np.zeros_like(clip_mask)
    for i in range(1, nlabels):
        if stats[i, cv2.CC_STAT_AREA] >= area_min_px:
            refined[labels == i] = 255
    clip_mask = refined > 0

    total_px = H * W
    area_ratio = float(clip_mask.sum()) / float(total_px)

    # compute region stats
    nlabels, labels, stats, _ = cv2.connectedComponentsWithStats(clip_mask.astype(np.uint8), connectivity=8)
    num_regions = nlabels - 1
    if num_regions > 0:
        max_region_ratio = float(stats[1:, cv2.CC_STAT_AREA].max() / total_px)
    else:
        max_region_ratio = 0.0

    # gradient-based flatness
    gx = cv2.Sobel(y_blur, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(y_blur, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.sqrt(gx**2 + gy**2)
    interior_grad = grad_mag[clip_mask].mean() if clip_mask.any() else 0.0
    flatness = 1.0 / (1.0 + interior_grad * 500.0)

    # fused severity metric
    severity = 0.6 * area_ratio + 0.2 * max_region_ratio + 0.2 * flatness

    return {
        "clip_area_ratio": area_ratio,
        "clip_num_regions": num_regions,
        "clip_max_region_ratio": max_region_ratio,
        "clip_flatness": flatness,
        "clip_severity": severity,
    }


# ------------------------------------------------------------
# Video-level aggregation (returns numeric array, not dict)
# ------------------------------------------------------------
def aggregate_brightness_clipping(per_frame):
    if not per_frame:
        return {
            "clip_area_ratio_mean": 0.0,
            "clip_area_ratio_p95": 0.0,
            "clip_frames_over_thresh": 0.0,
            "clip_severity_mean": 0.0,
            "clip_severity_p95": 0.0,
        }

    area = np.array([f["clip_area_ratio"] for f in per_frame], dtype=np.float32)
    sev = np.array([f["clip_severity"] for f in per_frame], dtype=np.float32)
    frames_over = float(np.mean(area > 1e-3))

    return {
        "clip_area_ratio_mean": float(area.mean()),
        "clip_area_ratio_p95": float(np.percentile(area, 95)),
        "clip_frames_over_thresh": frames_over,
        "clip_severity_mean": float(sev.mean()),
        "clip_severity_p95": float(np.percentile(sev, 95)),
    }



# Optional feature names (for reference)
FEATURE_NAMES = [
    "clip_area_ratio_mean",
    "clip_area_ratio_p95",
    "clip_frames_over_thresh",
    "clip_severity_mean",
    "clip_severity_p95",
]