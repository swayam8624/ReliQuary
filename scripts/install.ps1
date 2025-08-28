# ReliQuary Platform - Windows Installation Script
# Usage: iwr -useb https://install.reliquary.io/windows.ps1 | iex

[CmdletBinding()]
param(
    [string]$Version = "latest",
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\ReliQuary",
    [string]$ConfigDir = "$env:APPDATA\ReliQuary",
    [switch]$SystemWide = $false,
    [switch]$Debug = $false
)

# Error handling
$ErrorActionPreference = "Stop"

# Configuration
$script:ReliQuaryVersion = $Version
$script:GitHubRepo = "reliquary/reliquary-platform"
$script:BinaryName = "reliquary.exe"
$script:TempDir = "$env:TEMP\reliquary-install"

# Adjust paths for system-wide installation
if ($SystemWide) {
    $InstallDir = "$env:ProgramFiles\ReliQuary"
    $ConfigDir = "$env:ProgramData\ReliQuary"
}

# Console colors
enum LogLevel {
    Info
    Success
    Warning
    Error
    Debug
}

function Write-Log {
    param(
        [LogLevel]$Level,
        [string]$Message
    )
    
    $color = switch ($Level) {
        'Info'    { 'Cyan' }
        'Success' { 'Green' }
        'Warning' { 'Yellow' }
        'Error'   { 'Red' }
        'Debug'   { 'Magenta' }
    }
    
    $prefix = switch ($Level) {
        'Info'    { '[INFO]' }
        'Success' { '[SUCCESS]' }
        'Warning' { '[WARN]' }
        'Error'   { '[ERROR]' }
        'Debug'   { '[DEBUG]' }
    }
    
    if ($Level -eq 'Debug' -and -not $Debug) {
        return
    }
    
    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Show-Banner {
    Write-Host @'
╦═╗┌─┐┬  ┬╔═╗┬ ┬┌─┐┬─┐┬ ┬
╠╦╝├┤ │  │║═╬╗│ │├─┤├┬┘└┬┘
╩╚═└─┘┴─┘┴╚═╝╚└─┘┴ ┴┴└─ ┴ 
                            
Enterprise-Grade Cryptographic Memory Platform
Post-Quantum • Multi-Agent • Zero-Knowledge
'@ -ForegroundColor Cyan

    Write-Log Success "Installing ReliQuary Platform for Windows..."
    Write-Host ""
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-SystemRequirements {
    Write-Log Info "Checking system requirements..."
    
    # Check Windows version (Windows 10+)
    $osVersion = [System.Environment]::OSVersion.Version
    if ($osVersion.Major -lt 10) {
        throw "Windows 10 or later is required"
    }
    
    # Check architecture
    $arch = $env:PROCESSOR_ARCHITECTURE
    if ($arch -notin @('AMD64', 'ARM64')) {
        throw "Unsupported architecture: $arch. Only x64 and ARM64 are supported."
    }
    
    # Check available disk space (minimum 1GB)
    $drive = (Get-Location).Drive
    $freeSpace = (Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='$($drive.Name)'").FreeSpace
    if ($freeSpace -lt 1GB) {
        throw "Insufficient disk space. At least 1GB free space is required."
    }
    
    # Check memory (minimum 2GB)
    $totalMemory = (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory
    if ($totalMemory -lt 2GB) {
        throw "Insufficient memory. At least 2GB RAM is required."
    }
    
    Write-Log Success "System requirements check passed"
}

function Test-Dependencies {
    Write-Log Info "Checking dependencies..."
    
    # Check PowerShell version (5.1+)
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        throw "PowerShell 5.1 or later is required"
    }
    
    # Check if PowerShell execution policy allows script execution
    $executionPolicy = Get-ExecutionPolicy
    if ($executionPolicy -eq 'Restricted') {
        Write-Log Warning "PowerShell execution policy is Restricted"
        Write-Log Info "Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        throw "PowerShell execution policy prevents script execution"
    }
    
    Write-Log Success "All dependencies satisfied"
}

function Get-LatestVersion {
    if ($script:ReliQuaryVersion -eq "latest") {
        Write-Log Info "Fetching latest version..."
        
        try {
            $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$script:GitHubRepo/releases/latest"
            $script:ReliQuaryVersion = $response.tag_name -replace '^v', ''
            Write-Log Info "Latest version: $script:ReliQuaryVersion"
        }
        catch {
            throw "Failed to fetch latest version: $($_.Exception.Message)"
        }
    }
}

function Get-Architecture {
    $arch = $env:PROCESSOR_ARCHITECTURE
    switch ($arch) {
        'AMD64' { return 'amd64' }
        'ARM64' { return 'arm64' }
        default { throw "Unsupported architecture: $arch" }
    }
}

function Install-ReliQuary {
    $arch = Get-Architecture
    $platform = "windows_$arch"
    
    Write-Log Info "Downloading ReliQuary v$script:ReliQuaryVersion for $platform..."
    
    # Create temp directory
    if (Test-Path $script:TempDir) {
        Remove-Item $script:TempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $script:TempDir -Force | Out-Null
    
    # Download URL
    $downloadUrl = "https://github.com/$script:GitHubRepo/releases/download/v$script:ReliQuaryVersion/reliquary-v$script:ReliQuaryVersion-$platform.zip"
    $archivePath = Join-Path $script:TempDir "reliquary.zip"
    
    Write-Log Debug "Download URL: $downloadUrl"
    
    try {
        # Download archive
        Invoke-WebRequest -Uri $downloadUrl -OutFile $archivePath -UseBasicParsing
        
        # Extract archive
        Write-Log Info "Extracting archive..."
        Expand-Archive -Path $archivePath -DestinationPath $script:TempDir -Force
        
        # Create install directory
        if (-not (Test-Path $InstallDir)) {
            New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        }
        
        # Install binary
        Write-Log Info "Installing binary to $InstallDir..."
        $binarySource = Join-Path $script:TempDir $script:BinaryName
        $binaryTarget = Join-Path $InstallDir $script:BinaryName
        
        Copy-Item $binarySource $binaryTarget -Force
        
        Write-Log Success "Binary installed successfully"
    }
    catch {
        throw "Failed to download or install ReliQuary: $($_.Exception.Message)"
    }
}

function Set-Configuration {
    Write-Log Info "Setting up configuration..."
    
    # Create config directory
    if (-not (Test-Path $ConfigDir)) {
        New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    }
    
    # Create default configuration
    $configPath = Join-Path $ConfigDir "config.yaml"
    $configContent = @"
# ReliQuary Platform Configuration
# Generated by installer on $(Get-Date)

# API Configuration
api:
  endpoint: "https://api.reliquary.io"
  timeout: 30s
  retries: 3

# Authentication
auth:
  # Set your API key here or use RELIQUARY_API_KEY environment variable
  api_key: ""
  
# Logging
logging:
  level: "info"
  format: "json"
  file: "$($ConfigDir -replace '\\', '/')/reliquary.log"

# Local Settings
local:
  data_dir: "$($ConfigDir -replace '\\', '/')/data"
  cache_dir: "$($ConfigDir -replace '\\', '/')/cache"
  temp_dir: "$($ConfigDir -replace '\\', '/')/tmp"

# Security
security:
  tls_verify: true
  allowed_origins: []
  
# Performance
performance:
  workers: 4
  max_connections: 100
  timeout: "30s"
"@

    Set-Content -Path $configPath -Value $configContent -Encoding UTF8
    
    # Create data directories
    @("data", "cache", "tmp", "logs") | ForEach-Object {
        $dir = Join-Path $ConfigDir $_
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Log Success "Configuration created at $configPath"
}

function Add-ToPath {
    Write-Log Info "Adding ReliQuary to PATH..."
    
    $target = if ($SystemWide) { 'Machine' } else { 'User' }
    $currentPath = [Environment]::GetEnvironmentVariable('PATH', $target)
    
    if ($currentPath -notlike "*$InstallDir*") {
        $newPath = "$currentPath;$InstallDir"
        [Environment]::SetEnvironmentVariable('PATH', $newPath, $target)
        
        # Update current session PATH
        $env:PATH = "$env:PATH;$InstallDir"
        
        Write-Log Success "Added $InstallDir to PATH"
    } else {
        Write-Log Info "ReliQuary is already in PATH"
    }
}

function Install-Service {
    if (-not $SystemWide) {
        return
    }
    
    Write-Log Info "Setting up Windows service..."
    
    $serviceName = "ReliQuary"
    $binaryPath = Join-Path $InstallDir $script:BinaryName
    $configPath = Join-Path $ConfigDir "config.yaml"
    
    # Check if service already exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Log Info "Service already exists, updating..."
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        Remove-Service -Name $serviceName -Force
    }
    
    # Create new service
    $serviceArgs = @{
        Name = $serviceName
        BinaryPathName = "`"$binaryPath`" server --config `"$configPath`""
        DisplayName = "ReliQuary Platform Service"
        Description = "Enterprise-grade cryptographic memory platform with post-quantum security"
        StartupType = "Automatic"
    }
    
    New-Service @serviceArgs | Out-Null
    
    Write-Log Success "Windows service configured"
    Write-Log Info "Use 'Start-Service ReliQuary' to start the service"
}

function Test-Installation {
    Write-Log Info "Verifying installation..."
    
    $binaryPath = Join-Path $InstallDir $script:BinaryName
    
    if (Test-Path $binaryPath) {
        try {
            $version = & $binaryPath --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log Success "ReliQuary installed successfully: $version"
            } else {
                Write-Log Success "ReliQuary binary installed at $binaryPath"
            }
        }
        catch {
            Write-Log Success "ReliQuary binary installed at $binaryPath"
        }
    } else {
        throw "Installation verification failed - binary not found"
    }
}

function Remove-TempFiles {
    Write-Log Info "Cleaning up..."
    
    if (Test-Path $script:TempDir) {
        Remove-Item $script:TempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Show-NextSteps {
    Write-Host ""
    Write-Log Success "🎉 Installation completed successfully!"
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Get your API key: https://platform.reliquary.io/api-keys"
    Write-Host "2. Configure your API key:"
    Write-Host "   `$env:RELIQUARY_API_KEY = 'your_api_key_here'"
    Write-Host "   # or edit $ConfigDir\config.yaml"
    Write-Host ""
    Write-Host "3. Test the installation:"
    Write-Host "   reliquary --version"
    Write-Host "   reliquary health check"
    Write-Host ""
    Write-Host "4. Start using ReliQuary:"
    Write-Host "   reliquary vault store --data 'Hello, World!'"
    Write-Host ""
    Write-Host "Documentation: https://docs.reliquary.io" -ForegroundColor Cyan
    Write-Host "Examples: https://github.com/reliquary/examples" -ForegroundColor Cyan
    Write-Host "Support: https://support.reliquary.io" -ForegroundColor Cyan
    Write-Host ""
    
    if ($SystemWide) {
        Write-Host "Service Management:" -ForegroundColor Yellow
        Write-Host "   Start-Service ReliQuary      # Start service"
        Write-Host "   Get-Service ReliQuary        # Check status"
        Write-Host "   Get-EventLog Application -Source ReliQuary  # View logs"
        Write-Host ""
    }
    
    Write-Host "Note: You may need to restart your terminal or run 'refreshenv' to use the 'reliquary' command." -ForegroundColor Yellow
}

function Install-ReliQuaryPlatform {
    try {
        Show-Banner
        
        # Check if running as administrator for system-wide installation
        if ($SystemWide -and -not (Test-Administrator)) {
            throw "System-wide installation requires administrator privileges. Run PowerShell as Administrator or remove -SystemWide flag."
        }
        
        Test-SystemRequirements
        Test-Dependencies
        Get-LatestVersion
        Install-ReliQuary
        Set-Configuration
        Add-ToPath
        
        if ($SystemWide) {
            Install-Service
        }
        
        Test-Installation
        Remove-TempFiles
        Show-NextSteps
    }
    catch {
        Write-Log Error "Installation failed: $($_.Exception.Message)"
        Remove-TempFiles
        exit 1
    }
}

# Help function
function Show-Help {
    Write-Host @'
ReliQuary Platform - Windows Installation Script

USAGE:
    iwr -useb https://install.reliquary.io/windows.ps1 | iex

PARAMETERS:
    -Version <string>      Install specific version (default: latest)
    -InstallDir <string>   Installation directory (default: $env:LOCALAPPDATA\Programs\ReliQuary)
    -ConfigDir <string>    Configuration directory (default: $env:APPDATA\ReliQuary)
    -SystemWide           Install system-wide (requires admin privileges)
    -Debug                Enable debug output

EXAMPLES:
    # Basic installation
    iwr -useb https://install.reliquary.io/windows.ps1 | iex

    # Install specific version
    iwr -useb https://install.reliquary.io/windows.ps1 | iex -ArgumentList '-Version "5.0.0"'

    # System-wide installation (run as admin)
    iwr -useb https://install.reliquary.io/windows.ps1 | iex -ArgumentList '-SystemWide'

ENVIRONMENT VARIABLES:
    RELIQUARY_VERSION     Version to install
    RELIQUARY_INSTALL_DIR Installation directory
    RELIQUARY_CONFIG_DIR  Configuration directory

'@
}

# Handle help parameter
if ($args -contains '--help' -or $args -contains '-h') {
    Show-Help
    exit 0
}

# Override with environment variables if set
if ($env:RELIQUARY_VERSION) { $Version = $env:RELIQUARY_VERSION }
if ($env:RELIQUARY_INSTALL_DIR) { $InstallDir = $env:RELIQUARY_INSTALL_DIR }
if ($env:RELIQUARY_CONFIG_DIR) { $ConfigDir = $env:RELIQUARY_CONFIG_DIR }

# Run installation
Install-ReliQuaryPlatform