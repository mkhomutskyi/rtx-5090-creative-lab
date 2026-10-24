$ErrorActionPreference = 'Stop'
$labRoot = Split-Path -Parent $PSScriptRoot
foreach ($relative in @('models/diffusion_models','models/text_encoders','models/vae','inputs','outputs','state/comfyui')) {
    $target = Join-Path $labRoot $relative
    New-Item -ItemType Directory -Path $target -Force | Out-Null
}
Write-Output "Prepared project folders under $labRoot. No models or software were installed."
