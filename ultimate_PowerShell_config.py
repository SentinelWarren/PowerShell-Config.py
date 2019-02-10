import ctypes
import os
import subprocess
import sys
from shutil import which
from threading import Timer
import traceback


def show_exception_and_exit(exc_type, exc_value, tb):

    traceback.print_exception(exc_type, exc_value, tb)
    sys.exit(-1)

# Check if the current execution is run on elevated mode


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# Define subprocess.Popen to execute PowerShell commands
def ps_arg(rarg):
    sub = subprocess.Popen
    ps = 'powershell.exe'

    cmd = sub([ps, rarg], stdout=subprocess.PIPE)

    return cmd


# A function to Set-ExecutionPolicy on windows system
def set_ps_exec_policy():
    print("Setting Execution Policy...")
    setting_policy = ps_arg(
        r'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force')
    print("Execution Policy Setup Successfully! \n")

    return setting_policy


def show_output(arg):
    while True:
        output = arg.stdout.readline(1)
        if output == b'' and arg.poll() is not None:
            break
        if output:
            sys.stdout.write(output.decode('utf-8'))
            sys.stdout.flush()


# A function to check if the tool/program 'to-be' installed is already available on the system
def is_tool(prog):
    names_list = prog.split()
    available_prog = []

    for i in names_list:
        if which(i) is not None:
            available_prog.append(i)

    return available_prog, names_list


# A function to install chocolatey if it doesn't exist on the system already
def install_choco():
    print("Checking if Chocolatey exists else installing...")
    available, _ = is_tool("choco")

    if "choco" not in available:
        print("Installing Chocolatey...")
        ps_arg(r'iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex')
    else:
        print("Chocolatey already exist! \n")


# A function to install a tool/program that the specified on 'is_tool()'
def install_tool(prog):
    available, tool = is_tool(prog)
    for i in tool:
        # print(i)
        if i not in available:
            print("Installing {}...".format(i))
            run = ps_arg(r'choco install -y {}'.format(i))
            show_output(run)
        else:
            print("{} already exist! \n".format(i))


def input_ans(arg):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = input(arg).lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


def git_setup():

    print("Checking if git exists else installing...")
    install_tool("git")

    print("Setting git environment...")
    ps_arg(
        r'if (-not (Test-Path $env:Path:"C:\Program Files\Git\usr\bin")) {[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Git\usr\bin", "Machine")}')
    print("git Env setup successfully! \n")

    print("Generating Ssh Key... \n")
    email = input("Enter your email > ")
    key_name = input("Specify key name > ")
    generating_ssh_key = ps_arg(
        r'ssh-keygen -t rsa -b 4096 -C "{}" -f $env:USERPROFILE\.ssh\{}'.format(email, key_name))
    show_output(generating_ssh_key)
    print("The generated key is stored at $env:USERPROFILE\\.ssh \n")

    cp_ans = input_ans(
        "Do you want to copy the generated key to the clipboard? y/N > ")

    if cp_ans == True:
        ps_arg(r'Get-Content $env:USERPROFILE\.ssh\{}.pub | clip'.format(key_name))
        show_output(
            ps_arg(r'ssh-keygen -y -f $env:USERPROFILE\.ssh\{}'.format(key_name)))

        print("""\nThe above key is successfully copied to clipboard! \n
            You can now Add the public key to your GitHub A/C\n
            See https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/ for more info\n""")
    else:
        print("Key not copied! \n")

    print("Adding Ssh-Agent...")
    show_output(
        ps_arg(r'Start-SshAgent;Add-SshKey $env:USERPROFILE\.ssh\{}'.format(key_name)))
    print("Ssh-Agent successfully added!\n")

    print("Test authentication to GitHub...")
    show_output(ps_arg(r'ssh -T git@github.com'))


def config_global_git():
    config_ans = input_ans(
        "Do you want to Configure global Git settings? y/N > ")
    email, username = input(
        "Enter Your Github email address and username separated with space respectively > ").split()

    if config_ans == True:
        ps_arg(r'git config --global user.email {};git config --global user.name {};git config --global push.default simple;git config --global core.ignorecase false;git config --global core.autocrlf true'.format(email, username))
    else:
        print("Global Git settings not configured")

# A function to run specific commands with elevated privileges


def run_as_admin():

    if is_admin():
        set_ps_exec_policy()
        install_choco()
        git_setup()
        config_global_git()
        install_ans = input_ans(
            "Do you want to install any other program/programs with choco? y/N > ")
        if install_ans == True:
            install_tool(input("\nProgram name or names > "))
        else:
            print("Well, this is the end of the program execution")

        input("Press a key to exit")
    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)

    return


if __name__ == "__main__":
    run_as_admin()
    sys.excepthook = show_exception_and_exit
