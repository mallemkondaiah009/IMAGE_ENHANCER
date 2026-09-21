"""
app/config.py
Centralised desktop application settings — fully self-contained with hardcoded defaults (no .env needed).
"""
import os
import sys
from typing import Optional


class Settings:
    # Resolution & Output Quality Rules
    # Caps input to 500px -> Real-ESRGAN 4x gives 2000px native super-resolution
    max_enhance_input_dim: int = 500
    target_output_width: int = 2000
    target_output_height: int = 2000
    max_output_file_size_kb: int = 500

    # Application metadata
    app_title: str = "Image Studio"
    app_description: str = (
        "High-fidelity 4x AI Image Enhancement tailored for "
        "diamonds, gemstones, and precious metals."
    )
    app_version: str = "2.0.0"
    brand_name: str = "Image Studio"
    brand_tagline: str = "AI Studio"

    # Derived paths (computed as properties so they work in development and packaged .exe builds)
    @property
    def app_dir(self) -> str:
        """Directory where the executable or workspace root lives."""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @property
    def base_dir(self) -> str:
        """Directory where bundled internal resources live (handles PyInstaller _MEIPASS)."""
        if getattr(sys, "frozen", False):
            return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @property
    def permanent_engine_dir(self) -> str:
        """Permanent directory on disk for Real-ESRGAN engine and neural models."""
        local_app = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        p = os.path.join(local_app, "ImageStudio", "engine")
        os.makedirs(p, exist_ok=True)
        return p

    @property
    def engine_dir(self) -> str:
        """
        Permanent on-disk engine resolution (zero unpack latency):
        1. Permanent storage in %LOCALAPPDATA%/ImageStudio/engine
        2. Engine directory next to executable (app_dir/engine)
        3. Internal bundled engine (base_dir/engine)
        """
        perm_dir = self.permanent_engine_dir
        if os.path.exists(os.path.join(perm_dir, "realesrgan-ncnn-vulkan.exe")):
            return perm_dir

        app_engine = os.path.join(self.app_dir, "engine")
        if os.path.exists(os.path.join(app_engine, "realesrgan-ncnn-vulkan.exe")):
            return app_engine

        base_engine = os.path.join(self.base_dir, "engine")
        if os.path.exists(base_engine):
            return base_engine

        return perm_dir

    @property
    def models_dir(self) -> str:
        return os.path.join(self.engine_dir, "models")

    @property
    def temp_dir(self) -> str:
        """System temporary directory for scratch image processing buffers (auto-cleaned)."""
        import tempfile
        p = os.path.join(tempfile.gettempdir(), "image_studio_scratch")
        os.makedirs(p, exist_ok=True)
        return p

    @property
    def uploads_dir(self) -> str:
        return self.temp_dir

    @property
    def outputs_dir(self) -> str:
        p = os.path.join(self.app_dir, "outputs")
        os.makedirs(p, exist_ok=True)
        return p

    @property
    def assets_dir(self) -> str:
        path_in_base = os.path.join(self.base_dir, "assets")
        if os.path.exists(path_in_base):
            return path_in_base
        return os.path.join(self.app_dir, "assets")

    @property
    def exe_path(self) -> str:
        exe_name = "realesrgan-ncnn-vulkan.exe" if sys.platform == "win32" else "realesrgan-ncnn-vulkan"
        return os.path.join(self.engine_dir, exe_name)


settings = Settings()

