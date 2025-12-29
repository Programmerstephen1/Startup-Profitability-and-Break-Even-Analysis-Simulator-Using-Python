# PowerShell helper to run the config-based demo
python src\run_from_config.py sample_config.json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Demo run completed."
