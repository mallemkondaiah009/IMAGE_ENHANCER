"""
app/models/studio_models.py
Data entities and state representations (like Android data classes).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from PIL import Image


class EnhancementMode(str, Enum):
    ENHANCE = "enhance"
    REMOVE_BG = "remove_bg"
    COMBO = "combo"


class ViewMode(str, Enum):
    SPLIT = "split"
    ENHANCED = "enhanced"
    ORIGINAL = "original"


class ProcessingStatus(str, Enum):
    IDLE = "idle"
    PREPARING = "preparing"
    ENHANCING = "enhancing"
    REMOVING_BG = "removing_bg"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ImageMetrics:
    original_width: int = 0
    original_height: int = 0
    original_kb: float = 0.0
    result_width: int = 0
    result_height: int = 0
    result_kb: float = 0.0
    duration_seconds: float = 0.0


@dataclass
class StudioState:
    input_path: Optional[str] = None
    input_image: Optional[Image.Image] = None
    input_data_uri: Optional[str] = None

    output_path: Optional[str] = None
    output_image: Optional[Image.Image] = None
    output_data_uri: Optional[str] = None

    active_mode: EnhancementMode = EnhancementMode.ENHANCE
    view_mode: ViewMode = ViewMode.SPLIT
    status: ProcessingStatus = ProcessingStatus.IDLE
    status_message: str = "Ready — Load an image to begin."
    status_step: str = ""
    status_subtext: str = ""

    current_screen: str = "home"
    metrics: ImageMetrics = field(default_factory=ImageMetrics)
    is_processing: bool = False
