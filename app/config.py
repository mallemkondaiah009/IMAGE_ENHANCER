"""
app/config.py
Centralised desktop application settings — reads from .env via pydantic-settings.
"""
import os
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Resolution & Output Quality Rules
    # Caps input to 500px -> Real-ESRGAN 4x gives 2000px native super-resolution
    max_enhance_input_dim: int = 500
    target_output_width: int = 2000
    target_output_height: int = 2000
    max_output_file_size_kb: int = 500

    # Application metadata
    app_title: str = "LUMIÈRE Jewelry AI Studio"
    app_description: str = (
        "High-fidelity 4x AI Image Enhancement tailored for "
        "diamonds, gemstones, and precious metals."
    )
    app_version: str = "2.0.0"
    brand_name: str = "LUMIÈRE"
    brand_tagline: str = "Fine Jewelry AI Studio"

    # Derived paths (computed as properties so they're always relative to project root)
    @property
    def base_dir(self) -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @property
    def engine_dir(self) -> str:
        return os.path.join(self.base_dir, "engine")

    @property
    def models_dir(self) -> str:
        return os.path.join(self.engine_dir, "models")

    @property
    def uploads_dir(self) -> str:
        return os.path.join(self.base_dir, "uploads")

    @property
    def outputs_dir(self) -> str:
        return os.path.join(self.base_dir, "outputs")

    @property
    def assets_dir(self) -> str:
        return os.path.join(self.base_dir, "assets")

    @property
    def exe_path(self) -> str:
        exe_name = "realesrgan-ncnn-vulkan.exe" if sys.platform == "win32" else "realesrgan-ncnn-vulkan"
        return os.path.join(self.engine_dir, exe_name)


settings = Settings()
