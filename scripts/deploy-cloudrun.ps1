$ErrorActionPreference = 'Stop'

function Read-EnvFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()

        if (-not $line -or $line.StartsWith('#')) {
            return
        }

        $match = [regex]::Match($line, '^(?<key>[A-Za-z_][A-Za-z0-9_]*)=(?<value>.*)$')
        if (-not $match.Success) {
            return
        }

        $key = $match.Groups['key'].Value
        $value = $match.Groups['value'].Value.Trim()

        if ($value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        Set-Item -Path "Env:$key" -Value $value
    }
}

function Read-SecretValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Prompt
    )

    $secure = Read-Host -Prompt $Prompt -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        if ($ptr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        }
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $repoRoot

Read-EnvFile (Join-Path $repoRoot 'backend\.env')
Read-EnvFile (Join-Path $repoRoot 'backend\app\.env')

$projectId = 'soa1-485322'
$region = 'us-central1'
$serviceName = 'arboretum-backend'
$cloudSqlInstance = 'soa1-485322:us-central1:my-pg-instance'
$qdrantUrlDefault = 'https://27aff9e6-8dae-4699-8803-9ee4fd06af81.eu-central-1-0.aws.cloud.qdrant.io'

if (-not $env:QDRANT_URL) {
    $env:QDRANT_URL = $qdrantUrlDefault
}

if (-not $env:QDRANT_API_KEY) {
    $env:QDRANT_API_KEY = Read-SecretValue 'Qdrant API key'
}

if (-not $env:OPENAI_API_KEY) {
    $env:OPENAI_API_KEY = Read-SecretValue 'OpenAI API key'
}

if (-not $env:DB_PASS) {
    $env:DB_PASS = Read-SecretValue 'Cloud SQL password'
}

if (-not $env:DB_USER) {
    $env:DB_USER = 'postgres'
}

if (-not $env:DB_NAME) {
    $env:DB_NAME = 'my_app_db'
}

if (-not $env:DB_HOST) {
    $env:DB_HOST = "/cloudsql/$cloudSqlInstance"
}

if (-not $env:BETA_TELEMETRY_ENABLED) {
    $env:BETA_TELEMETRY_ENABLED = 'true'
}

# HuggingFace token for CLIP model (avoids rate limits)
$hfTokenInput = Read-Host 'HuggingFace token (optional, press Enter to skip)'
if ($hfTokenInput) {
    $env:HF_TOKEN = $hfTokenInput
}

& gcloud.cmd config set project $projectId
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$envVarsList = @(
    "QDRANT_URL=$($env:QDRANT_URL)",
    "QDRANT_API_KEY=$($env:QDRANT_API_KEY)",
    "OPENAI_API_KEY=$($env:OPENAI_API_KEY)",
    "DB_USER=$($env:DB_USER)",
    "DB_PASS=$($env:DB_PASS)",
    "DB_NAME=$($env:DB_NAME)",
    "DB_HOST=$($env:DB_HOST)",
    "BETA_TELEMETRY_ENABLED=$($env:BETA_TELEMETRY_ENABLED)"
)

if ($env:ADMIN_LOG_TOKEN) {
    $envVarsList += "ADMIN_LOG_TOKEN=$($env:ADMIN_LOG_TOKEN)"
}

if ($env:HF_TOKEN) {
    $envVarsList += "HF_TOKEN=$($env:HF_TOKEN)"
}

$envVars = $envVarsList -join ','

& gcloud.cmd run deploy $serviceName `
    --source backend `
    --region $region `
    --allow-unauthenticated `
    --cpu 2 `
    --memory 2Gi `
    --timeout 300 `
    --add-cloudsql-instances $cloudSqlInstance `
    --set-env-vars $envVars

exit $LASTEXITCODE
