# PowerShell-Config.py

A simple python script to simplify and automate first time PowerShell configuration.

## Features

- Sets Execution Policy of LocalMachine to RemoteSigned in order to be able to execute scripts
- Installing Chocolatey package management
- Installing & configuring Git & hub
- Generating Ssh key and configuring Github
- Option to install in bulk any number of programs/tools

## Requirements

- python3
- PowerShell >= v3

## Installation

- Clone the repo
    
    `git clone https://github.com/SentinelWarren/PowerShell-Config.py.git`

**OR**

- Run the following command on PowerShell to set Downloading folder location and download the zip

    `Set-Location "to\the\downloads\folder";iwr -outf PowerShell-Config.py.zip https://github.com/Sent
inelWarren/PowerShell-Config.py/archive/master.zip`
    
    i.e; 
    
    `Set-Location $env:USERPROFILE\Downloads;iwr -outf PowerShell-Config.py.zip https://github.com/Sent
inelWarren/PowerShell-Config.py/archive/master.zip`

## Usage
- `cd "to\the\PowerShell-Config.py\src\"` i.e; `cd "$env:USERPROFILE\Downloads\PowerShell-Config.py\src\"`

- `python psconfig.py`
    
## Todo

> To be added

## Contributing

- Open New Issue for a feature you want to add.
- When accepted, send PR and we will review and merge

**NOTE:** Its meant to simplify PowerShell first time setup on windows machine.
