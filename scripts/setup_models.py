"""
scripts/setup_models.py
Downloads the Real-ESRGAN NCNN Vulkan engine and 4x-UltraSharp model weights.

Usage (from project root):
    python scripts/setup_models.py
"""
import os
import sys
import zipfile
import urllib.request
import shutil

# Resolve paths relative to the project root (one level up from this script)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGINE_DIR = os.path.join(PROJECT_ROOT, "engine")
MODELS_DIR = os.path.join(ENGINE_DIR, "models")

ZIP_URL = (
    "https://github.com/xinntao/Real-ESRGAN/releases/download/"
    "v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip"
)
ZIP_PATH = os.path.join(ENGINE_DIR, "realesrgan-ncnn-vulkan.zip")

HF_PARAM_URL = (
    "https://huggingface.co/Kim2091/UltraSharp/resolve/main/"
    "NCNN/4x-UltraSharp-fp16.param"
)
HF_BIN_URL = (
    "https://huggingface.co/Kim2091/UltraSharp/resolve/main/"
    "NCNN/4x-UltraSharp-fp16.bin"
)


def download_with_progress(url: str, dest_path: str, desc: str) -> None:
    print(f"[+] Downloading {desc}...")

    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, downloaded * 100 / total_size)
            mb_down = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(
                f"\r    Progress: {percent:5.1f}% ({mb_down:.1f} MB / {mb_total:.1f} MB)"
            )
            sys.stdout.flush()

    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, dest_path, reporthook)
    sys.stdout.write("\n")
    print(f"[OK] Saved to {dest_path}")


def setup() -> None:
    os.makedirs(MODELS_DIR, exist_ok=True)
    exe_path = os.path.join(ENGINE_DIR, "realesrgan-ncnn-vulkan.exe")

    # ── 1. Download and extract Real-ESRGAN engine ────────────────────────────
    if not os.path.exists(exe_path):
        download_with_progress(ZIP_URL, ZIP_PATH, "Real-ESRGAN NCNN Vulkan Engine (~15 MB)")
        print("[+] Extracting engine zip...")
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            for member in zip_ref.namelist():
                filename = os.path.basename(member)
                if not filename:
                    continue
                source = zip_ref.open(member)
                target = (
                    os.path.join(MODELS_DIR, filename)
                    if "models" in member
                    else os.path.join(ENGINE_DIR, filename)
                )
                with open(target, "wb") as f:
                    shutil.copyfileobj(source, f)
                source.close()
        try:
            os.remove(ZIP_PATH)
        except OSError:
            pass
        print("[OK] Real-ESRGAN NCNN Vulkan engine ready.")
    else:
        print("[*] Engine executable already present, skipping download.")

    # ── 2. Download 4x-UltraSharp model weights ───────────────────────────────
    model_param = os.path.join(MODELS_DIR, "4x-UltraSharp.param")
    model_bin = os.path.join(MODELS_DIR, "4x-UltraSharp.bin")

    if not os.path.exists(model_param):
        download_with_progress(HF_PARAM_URL, model_param, "4x-UltraSharp.param (~5 KB)")
    else:
        print("[*] 4x-UltraSharp.param already present.")

    if not os.path.exists(model_bin):
        download_with_progress(HF_BIN_URL, model_bin, "4x-UltraSharp.bin (~33 MB)")
    else:
        print("[*] 4x-UltraSharp.bin already present.")

    print("\n[SUCCESS] All components are ready. Run: python main.py")


if __name__ == "__main__":
    setup()
