if ((Get-PackageProvider -Name NuGet).version -lt 2.8.5.201 ) {
    try {
        Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Confirm:$False -Force
    }
    catch [Exception]{
        $_.message 
        exit
    }
}
else {
    Write-Host "Version of NuGet installed = " (Get-PackageProvider -Name NuGet).version
}


if (Get-Module -ListAvailable -Name "posh-git") {
    Write-Host "posh-git Already Installed"
} 
else {
    try {
        Set-PSRepository -Name PSGallery -InstallationPolicy Trusted
        Install-Module -Name "posh-git" 
    }
    catch [Exception] {
        $_.message 
        exit
    }
}


if (!(Get-Module "posh-git")) { 
    try {
        Import-Module -Name posh-git
    }
    catch [Exception] {
        $_.message 
        exit
    }
}
else {
    Write-Host "posh-git Already Imported"
} 