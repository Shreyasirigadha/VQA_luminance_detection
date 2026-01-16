# Connection Between HDR Clipping Files

## Overview

These three files form a **layered architecture** for HDR brightness clipping detection:

```
┌─────────────────────────────────────────────────────────────┐
│  hdr_clipping.py                                             │
│  ════════════════                                            │
│  CORE ALGORITHMS (Lowest Layer)                             │
│  • brightness_clipping_features() - Frame processing         │
│  • aggregate_brightness_clipping() - Video aggregation       │
│  • pq_eotf() - PQ to nits conversion                        │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ imports
                            │
┌───────────────────────────┴─────────────────────────────────┐
│  hdr_clip_test.py                                           │
│  ════════════════                                           │
│  VIDEO PROCESSING LAYER (Middle Layer)                      │
│  • detect_brightness_clipping_video() - Main entry point    │
│  • _read_mp4_y_frames() - MP4 reader                       │
│  • _read_yuv420_8bit_luma() - 8-bit YUV reader            │
│  • _read_yuv420_p010_luma() - 10-bit P010 reader           │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ imports
                            │
┌───────────────────────────┴─────────────────────────────────┐
│  hdr_clipping_fex.py                                        │
│  ═══════════════════                                        │
│  FEATURE EXTRACTOR WRAPPER (Top Layer)                      │
│  • HDRClippingFex class - Conforms to Runner interface     │
│  • __call__() - Entry point for Runner framework           │
│  • _process_frames() - Frame processing wrapper            │
│  • _read_mp4_frames() - MP4 reading wrapper               │
│  • _read_yuv420_frames() - YUV reading wrapper            │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. `hdr_clipping.py` - Core Algorithms Layer

**Role:** Pure algorithmic functions (no I/O, no framework dependencies)

**Key Functions:**

### `brightness_clipping_features(frame_y, ...)`
- **Input:** Single frame (numpy array)
- **Output:** Dictionary with clipping metrics:
  ```python
  {
    "clip_area_ratio": 0.0234,      # Fraction of frame that's clipped
    "clip_num_regions": 5,           # Number of clipped regions
    "clip_max_region_ratio": 0.0123, # Largest region size
    "clip_flatness": 0.8567,         # How flat clipped regions are
    "clip_severity": 0.3456          # Combined severity score
  }
  ```
- **What it does:**
  1. Converts PQ codes to nits (if HDR)
  2. Applies Gaussian blur
  3. Thresholds to find clipped regions
  4. Removes small blobs
  5. Computes statistics

### `aggregate_brightness_clipping(per_frame)`
- **Input:** List of per-frame dictionaries
- **Output:** Video-level aggregated metrics:
  ```python
  {
    "clip_area_ratio_mean": 0.0234,
    "clip_area_ratio_p95": 0.0456,
    "clip_frames_over_thresh": 0.1234,
    "clip_severity_mean": 0.3456,
    "clip_severity_p95": 0.4567
  }
  ```

### `pq_eotf(v_norm)`
- **Input:** Normalized PQ values [0, 1]
- **Output:** Luminance in nits
- **Purpose:** Converts HDR10 PQ encoding to absolute luminance

**Dependencies:** None (pure functions)

---

## 2. `hdr_clip_test.py` - Video Processing Layer

**Role:** Video I/O and frame-by-frame processing

**Key Functions:**

### `detect_brightness_clipping_video(path, ...)`
- **Main Entry Point** for direct video processing
- **Input:** Video file path + parameters
- **Output:** Dictionary with per-frame and aggregate results:
  ```python
  {
    "per_frame": [dict1, dict2, ...],  # One dict per frame
    "aggregate": {
      "clip_area_ratio_mean": ...,
      ...
    }
  }
  ```

**What it does:**
1. **Detects video format** (MP4, YUV8, P010)
2. **Reads frames** using appropriate reader:
   - `_read_mp4_y_frames()` - For MP4/MOV files
   - `_read_yuv420_8bit_luma()` - For 8-bit YUV
   - `_read_yuv420_p010_luma()` - For 10-bit P010 HDR
3. **Processes each frame** by calling `brightness_clipping_features()` from `hdr_clipping_fex`
4. **Aggregates results** using `aggregate_brightness_clipping()` from `hdr_clipping_fex`

**Import Chain:**
```python
from ..funque_atoms import hdr_clipping_fex as fex
# Then calls:
fex.brightness_clipping_features(...)      # Actually from hdr_clipping.py
fex.aggregate_brightness_clipping(...)     # Actually from hdr_clipping.py
```

**Note:** This is a bit confusing - it imports `hdr_clipping_fex` but uses functions that are actually in `hdr_clipping.py`. This works because `hdr_clipping_fex.py` imports and re-exports them.

---

## 3. `hdr_clipping_fex.py` - Feature Extractor Wrapper Layer

**Role:** Framework integration (conforms to `qualitylib` Runner interface)

**Key Components:**

### `HDRClippingFex` Class
- **Purpose:** Makes clipping detection usable with the Runner framework
- **Interface:** Implements `__call__(asset)` method expected by Runner

### `__call__(asset)` Method
- **Input:** Asset dictionary with video path and metadata
- **Output:** Dictionary with video-level features:
  ```python
  {
    "fex_name": "hdr_clipping",
    "fex_version": "1.0",
    "clip_area_ratio_mean": 0.0234,
    "clip_area_ratio_p95": 0.0456,
    "clip_frames_over_thresh": 0.1234,
    "clip_severity_mean": 0.3456,
    "clip_severity_p95": 0.4567
  }
  ```

**What it does:**
1. **Reads video** (MP4 or YUV)
2. **Processes frames** by calling `brightness_clipping_features()` from `hdr_clipping.py`
3. **Aggregates** using `aggregate_brightness_clipping()` from `hdr_clipping.py`
4. **Returns** formatted results for Runner framework

**Import Chain:**
```python
from ..funque_atoms.hdr_clipping import (
    brightness_clipping_features,
    aggregate_brightness_clipping,
)
```

---

## Connection Flow Diagram

### Direct Usage (Standalone):
```
User Code
    ↓
hdr_clip_test.py::detect_brightness_clipping_video()
    ↓
    Reads video frames
    ↓
hdr_clipping_fex (imported as fex)
    ↓ (calls)
hdr_clipping.py::brightness_clipping_features()  [per frame]
    ↓
hdr_clipping.py::aggregate_brightness_clipping() [video-level]
    ↓
Returns: {"per_frame": [...], "aggregate": {...}}
```

### Framework Usage (via Runner):
```
Runner Framework
    ↓
hdr_clipping_fex.py::HDRClippingFex.__call__()
    ↓
    Reads video frames
    ↓
hdr_clipping.py::brightness_clipping_features()  [per frame]
    ↓
hdr_clipping.py::aggregate_brightness_clipping() [video-level]
    ↓
Returns: {"fex_name": ..., "clip_area_ratio_mean": ..., ...}
```

### Integration with FUNQUE:
```
funque_feature_extractors.py::FunqueFeatureExtractor
    ↓ (calls)
hdr_clip_test.py::detect_brightness_clipping_video()
    ↓ (which uses)
hdr_clipping.py::brightness_clipping_features()
hdr_clipping.py::aggregate_brightness_clipping()
```

---

## Key Differences

| Aspect | hdr_clipping.py | hdr_clip_test.py | hdr_clipping_fex.py |
|--------|----------------|------------------|---------------------|
| **Purpose** | Core algorithms | Video I/O + processing | Framework wrapper |
| **Input** | Single frame | Video file path | Asset dictionary |
| **Output** | Frame metrics dict | Per-frame + aggregate | Video features dict |
| **Dependencies** | None (pure) | hdr_clipping_fex | hdr_clipping |
| **Usage** | Called by others | Standalone or via FUNQUE | Via Runner framework |
| **Video Reading** | ❌ No | ✅ Yes (MP4/YUV/P010) | ✅ Yes (MP4/YUV) |
| **Framework** | ❌ No | ❌ No | ✅ Yes (Runner) |

---

## Import Relationships

```
hdr_clipping.py
    (no imports from other clipping files)

hdr_clip_test.py
    imports → hdr_clipping_fex (as fex)
    uses → fex.brightness_clipping_features()
    uses → fex.aggregate_brightness_clipping()
    (These functions are actually in hdr_clipping.py, 
     but accessed through hdr_clipping_fex)

hdr_clipping_fex.py
    imports → hdr_clipping
    uses → brightness_clipping_features()
    uses → aggregate_brightness_clipping()
```

**Note:** There's a slight architectural quirk here - `hdr_clip_test.py` imports `hdr_clipping_fex` to access functions that are actually in `hdr_clipping.py`. This works because `hdr_clipping_fex.py` imports and re-exports them, but it would be cleaner to import directly from `hdr_clipping.py`.

---

## Usage Examples

### Example 1: Direct Video Processing
```python
from funque_plus.features.funque_atoms.hdr_clip_test import detect_brightness_clipping_video

result = detect_brightness_clipping_video(
    path="video.p010",
    input_type="p010",
    width=1920,
    height=1080,
    is_pq_10bit=True
)

print(result["aggregate"]["clip_area_ratio_mean"])
```

### Example 2: Via Runner Framework
```python
from funque_plus.features.funque_atoms.hdr_clipping_fex import HDRClippingFex

fex = HDRClippingFex(frame_stride=2, is_pq_10bit=True)
result = fex({
    "path": "video.p010",
    "width": 1920,
    "height": 1080
})

print(result["clip_area_ratio_mean"])
```

### Example 3: Via FUNQUE Feature Extractor
```python
# Used internally by FunqueFeatureExtractor
from funque_plus.features.funque_atoms.hdr_clip_test import detect_brightness_clipping_video

clip_result = detect_brightness_clipping_video(...)
# Results integrated into FUNQUE feature vector
```

---

## Summary

**Architecture Pattern:** Layered design with separation of concerns

1. **`hdr_clipping.py`** = Pure algorithms (reusable, testable)
2. **`hdr_clip_test.py`** = Video I/O + orchestration (standalone usage)
3. **`hdr_clipping_fex.py`** = Framework adapter (integrates with Runner)

**Data Flow:**
- Video file → Frame extraction → Frame processing → Aggregation → Features

**Key Insight:** The core algorithms in `hdr_clipping.py` are reused by both `hdr_clip_test.py` (for direct usage) and `hdr_clipping_fex.py` (for framework integration), demonstrating good code reuse and separation of concerns.
