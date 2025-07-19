# PowerShell GPU sanity-check script
Write-Host "=== NVIDIA driver ==="
try {
    nvidia-smi
} catch {
    Write-Host "❌  No NVIDIA GPU detected"
    exit 1
}

$pyScript = @'
import torch, lightgbm as lgb
print("PyTorch:", torch.__version__,
      "| CUDA available:", torch.cuda.is_available(),
      "| Device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

try:
    gbm = lgb.LGBMRegressor(device_type='gpu')
    print("LightGBM GPU build OK")
except Exception as e:
    print("LightGBM GPU init failed:", e)
'@

$pyFile = "gpu_check.py"
python.exe $pyFile
Remove-Item $pyFile 