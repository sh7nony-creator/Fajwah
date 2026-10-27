# Fajwah local preview
Set-Location $PSScriptRoot
$localDependencies = Join-Path $PSScriptRoot '../../work/deps'
if (Test-Path $localDependencies) {
    $env:PYTHONPATH = (Resolve-Path $localDependencies).Path
}
python -m streamlit run app.py --global.developmentMode false --server.address 127.0.0.1 --server.port 8501
