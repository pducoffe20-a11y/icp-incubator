param(
    [Parameter(Mandatory = $false)]
    [string]$DraftsFile = "./outbox/drafts.json",

    [Parameter(Mandatory = $false)]
    [string]$FolderName = "Outreach - Review"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $DraftsFile)) {
    throw "Drafts file not found: $DraftsFile"
}

$drafts = Get-Content -Path $DraftsFile -Raw | ConvertFrom-Json
$outlook = New-Object -ComObject Outlook.Application
$namespace = $outlook.GetNamespace("MAPI")
$draftsFolder = $namespace.GetDefaultFolder(16)

function Get-OrCreateFolder {
    param(
        [Parameter(Mandatory = $true)]$Parent,
        [Parameter(Mandatory = $true)][string]$Name
    )

    foreach ($folder in $Parent.Folders) {
        if ($folder.Name -eq $Name) {
            return $folder
        }
    }

    return $Parent.Folders.Add($Name)
}

$targetFolder = Get-OrCreateFolder -Parent $draftsFolder -Name $FolderName
$count = 0

foreach ($draft in $drafts) {
    $mail = $outlook.CreateItem(0)
    $mail.To = $draft.to
    $mail.Subject = $draft.subject

    if ($draft.body_format -eq "html") {
        $mail.HTMLBody = $draft.body
    }
    else {
        $mail.Body = $draft.body
    }

    if ($draft.category) {
        $mail.Categories = $draft.category
    }

    $mail.Save()
    $mail.Move($targetFolder) | Out-Null
    $count += 1
}

Write-Host "Staged $count Outlook drafts in Drafts/$FolderName. Review before sending."
