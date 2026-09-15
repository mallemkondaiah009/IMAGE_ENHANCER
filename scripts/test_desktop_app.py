"""
scripts/test_desktop_app.py
Verification test for the MVVM Flet desktop app architecture.
"""
import os
import sys
import asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.models import EnhancementMode, ViewMode, ProcessingStatus
from app.viewmodels import StudioViewModel, pil_to_data_uri, file_to_data_uri

sample_path = os.path.join(settings.assets_dir, "sample_ring_small.jpg")
assert os.path.exists(sample_path), f"Sample image missing at {sample_path}"

print("[+] Initializing StudioViewModel (MVVM Architecture)...")
vm = StudioViewModel()

# Observer to track state updates
updates_count = 0
def on_state_changed():
    global updates_count
    updates_count += 1

vm.add_listener(on_state_changed)

# 1. Test image loading
print("[+] Testing ViewModel.load_image()...")
ok = vm.load_image(sample_path)
assert ok, "ViewModel failed to load image"
assert vm.state.input_path == sample_path
assert vm.state.input_data_uri.startswith("data:image/")
assert vm.state.metrics.original_width > 0
assert updates_count > 0, "Observer was not notified on image load"
print(f"[+] Loaded: {vm.state.metrics.original_width}x{vm.state.metrics.original_height} px")

# 2. Test mode switching
print("[+] Testing ViewModel mode switching...")
vm.set_enhancement_mode(EnhancementMode.REMOVE_BG)
assert vm.state.active_mode == EnhancementMode.REMOVE_BG
vm.set_enhancement_mode(EnhancementMode.ENHANCE)
assert vm.state.active_mode == EnhancementMode.ENHANCE
print("[+] Mode switched back to ENHANCE.")

# 3. Test async process_image
print("[+] Running ViewModel.process_image() async worker...")
asyncio.run(vm.process_image())

assert vm.state.status == ProcessingStatus.COMPLETED, f"Expected COMPLETED, got {vm.state.status}"
assert vm.state.output_path and os.path.exists(vm.state.output_path)
assert (vm.state.metrics.result_width, vm.state.metrics.result_height) == (2000, 2000)
assert vm.state.metrics.result_kb <= 500.0

print(f"[+] Processing completed in {vm.state.metrics.duration_seconds}s!")
print(f"[+] Output: {vm.state.metrics.result_width}x{vm.state.metrics.result_height} px, {vm.state.metrics.result_kb} KB")
print(f"[+] Total ViewModel state notifications: {updates_count}")

print("\n==========================================================")
print("  ALL MVVM FLET DESKTOP ARCHITECTURE TESTS PASSED!       ")
print("==========================================================")
