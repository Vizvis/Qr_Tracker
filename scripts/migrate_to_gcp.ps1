# =============================================================
# migrate_to_gcp.ps1
# Dumps local PostgreSQL DB and restores it to GCP Cloud SQL.
#
# Prerequisites:
#   - pg_dump / psql in PATH  (comes with PostgreSQL client tools)
#   - GCP Cloud SQL public IP set in .env (DB_HOST_CLOUD)
#   - Your local IP whitelisted in GCP Cloud SQL → Connections → Authorised Networks
#
# Usage:
#   cd "c:\Users\user\Documents\Code\Viss QR\Qr_Tracker"
#   .\scripts\migrate_to_gcp.ps1
# =============================================================

$ErrorActionPreference = "Stop"

# ── Load .env ────────────────────────────────────────────────
$envFile = Join-Path $PSScriptRoot "..\.env"
if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found at: $envFile"
    exit 1
}

$env_vars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=\s]+)\s*=\s*(.*)$') {
        $env_vars[$Matches[1]] = $Matches[2].Trim()
    }
}

# ── Local (source) credentials ───────────────────────────────
$LOCAL_USER     = $env_vars["DB_USER"]
# URL-decode the password (e.g. %40 → @) so PGPASSWORD gets the literal character
$LOCAL_PASSWORD = [System.Uri]::UnescapeDataString($env_vars["DB_PASSWORD"])
$LOCAL_HOST     = if ($env_vars["DB_HOST"]) { $env_vars["DB_HOST"] } else { "localhost" }
$LOCAL_PORT     = if ($env_vars["DB_PORT"]) { $env_vars["DB_PORT"] } else { "5432" }
$LOCAL_DB       = $env_vars["DB_NAME"]

# ── Cloud (target) credentials ───────────────────────────────
$CLOUD_USER     = $env_vars["DB_USER_CLOUD"]
$CLOUD_PASSWORD = $env_vars["DB_PASSWORD_CLOUD"]
$CLOUD_HOST     = $env_vars["DB_HOST_CLOUD"]
$CLOUD_PORT     = if ($env_vars["DB_PORT_CLOUD"]) { $env_vars["DB_PORT_CLOUD"] } else { "5432" }
$CLOUD_DB       = $env_vars["DB_NAME_CLOUD"]

# ── Validate cloud credentials are set ───────────────────────
if (-not $CLOUD_HOST) {
    Write-Error "DB_HOST_CLOUD is empty in .env! Set it to your GCP Cloud SQL public IP first."
    exit 1
}
if (-not $CLOUD_PASSWORD) {
    Write-Error "DB_PASSWORD_CLOUD is empty in .env!"
    exit 1
}

# ── Detect PostgreSQL bin path ───────────────────────────────
# Try PATH first; if not found, scan Program Files
$pgDumpCmd = Get-Command pg_dump -ErrorAction SilentlyContinue
if ($pgDumpCmd) { $pgDump = $pgDumpCmd.Source } else { $pgDump = $null }
if (-not $pgDump) {
    $pgVersions = Get-ChildItem "C:\Program Files\PostgreSQL" -ErrorAction SilentlyContinue |
                  Sort-Object Name -Descending
    if ($pgVersions) {
        $pgBin  = Join-Path $pgVersions[0].FullName "bin"
        $pgDump = Join-Path $pgBin "pg_dump.exe"
        $pgPsql = Join-Path $pgBin "psql.exe"
    } else {
        Write-Error "pg_dump not found in PATH or Program Files\PostgreSQL. Install PostgreSQL client tools."
        exit 1
    }
} else {
    $pgBin  = Split-Path $pgDump
    $pgPsql = Join-Path $pgBin "psql.exe"
}
Write-Host "Using PostgreSQL bin: $pgBin"

$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$dumpFile   = Join-Path $PSScriptRoot "..\qr_tracker_dump_$timestamp.sql"
$dumpFile   = [System.IO.Path]::GetFullPath($dumpFile)

Write-Host ""
Write-Host "========================================"
Write-Host "  QR Tracker → GCP Cloud SQL Migration"
Write-Host "========================================"
Write-Host "Source : ${LOCAL_USER}@${LOCAL_HOST}:${LOCAL_PORT}/${LOCAL_DB}"
Write-Host "Target : ${CLOUD_USER}@${CLOUD_HOST}:${CLOUD_PORT}/${CLOUD_DB}"
Write-Host "Dump   : $dumpFile"
Write-Host ""

# ── Step 1: pg_dump local DB ─────────────────────────────────
Write-Host "[1/3] Dumping local database..."
$env:PGPASSWORD = $LOCAL_PASSWORD
& $pgDump `
    "--host=$LOCAL_HOST" `
    "--port=$LOCAL_PORT" `
    "--username=$LOCAL_USER" `
    "--dbname=$LOCAL_DB" `
    "--no-password" `
    "--format=plain" `
    "--encoding=UTF8" `
    "--file=$dumpFile"

if ($LASTEXITCODE -ne 0) {
    Write-Error "pg_dump failed! Check local DB credentials."
    exit 1
}
Write-Host "    Dump saved to: $dumpFile"

# ── Step 2: Create target DB if it doesn't exist ─────────────
Write-Host ""
Write-Host "[2/3] Ensuring database '$CLOUD_DB' exists on GCP..."
$env:PGPASSWORD = $CLOUD_PASSWORD
& $pgPsql `
    "--host=$CLOUD_HOST" `
    "--port=$CLOUD_PORT" `
    "--username=$CLOUD_USER" `
    "--dbname=postgres" `
    "--no-password" `
    "--command=SELECT 1 FROM pg_database WHERE datname='$CLOUD_DB'" `
    2>&1 | Out-Null

$dbExists = & $pgPsql `
    "--host=$CLOUD_HOST" `
    "--port=$CLOUD_PORT" `
    "--username=$CLOUD_USER" `
    "--dbname=postgres" `
    "--no-password" `
    "--tuples-only" `
    "--command=SELECT 1 FROM pg_database WHERE datname='$CLOUD_DB';" 2>&1

if ($dbExists -notmatch "1") {
    Write-Host "    Creating database '$CLOUD_DB'..."
    & $pgPsql `
        "--host=$CLOUD_HOST" `
        "--port=$CLOUD_PORT" `
        "--username=$CLOUD_USER" `
        "--dbname=postgres" `
        "--no-password" `
        "--command=CREATE DATABASE `"$CLOUD_DB`";"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create database on GCP!"
        exit 1
    }
} else {
    Write-Host "    Database '$CLOUD_DB' already exists."
}

# ── Step 3: Restore dump to GCP ──────────────────────────────
Write-Host ""
Write-Host "[3/3] Restoring dump to GCP Cloud SQL..."
$env:PGPASSWORD = $CLOUD_PASSWORD
& $pgPsql `
    "--host=$CLOUD_HOST" `
    "--port=$CLOUD_PORT" `
    "--username=$CLOUD_USER" `
    "--dbname=$CLOUD_DB" `
    "--no-password" `
    "--file=$dumpFile"

if ($LASTEXITCODE -ne 0) {
    Write-Error "psql restore failed!"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Migration complete!"
Write-Host ""
Write-Host "  Next steps:"
Write-Host "  1. Open .env and set USE_LOCAL_DB=false"
Write-Host "  2. Restart the backend: uvicorn main:app --reload"
Write-Host "  3. Test a few API endpoints to confirm connectivity"
Write-Host "========================================"
Write-Host ""

# Clean up PGPASSWORD
Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
