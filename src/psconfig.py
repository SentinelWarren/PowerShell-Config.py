import ctypes
import os
import subprocess
import sys
from shutil import which
import webbrowser


# Check if the current execution is run on elevated mode
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# Define subprocess.Popen func to execute PowerShell commands
def ps_arg(rarg):
    sub = subprocess.Popen
    ps = 'powershell.exe'

    cmd = sub([ps, rarg], stdout=subprocess.PIPE)

    return cmd


# A function read out subprocess output
def show_output(arg):
    global res
    while True:
        output = arg.stdout.readline()
        if output == b'' and arg.poll() is not None:
            break
        if output:
            res = sys.stdout.write(output.decode('utf-8'))
            sys.stdout.flush()

    return res


# A function to Set-ExecutionPolicy on windows system
def set_ps_exec_policy():
    print("Checking if Execution Policy is set...")
    check_exe_policy = (subprocess.run(
        ['powershell.exe', 'Get-ExecutionPolicy'], stdout=subprocess.PIPE).stdout.decode('utf-8')).strip()

    if check_exe_policy == 'RemoteSigned':
        print("Execution Policy is already set to '{}'\n".format(check_exe_policy))
    else:
        print("Setting Execution Policy...")
        ps_arg(r'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force')
        print("Execution Policy Setup Successfully! \n")


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


# A fun to gather user input answer
def input_ans(arg):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}
    while True:
        choice = input(arg).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no' \n")


# A func for git initial setup
def git_setup():

    print("Checking if git exists else installing...")
    install_tool("git")

    print("Checking if hub exists else installing...")
    install_tool("hub")

    # Installing important PowerShell modules for working with git
    ps_file = os.path.realpath("ps1\\get-module.ps1")
    print("Installing additional PowerShell modules...")
    show_output(ps_arg(ps_file))

    print("\nSetting git environment...")
    ps_arg(
        r'if (-not (Test-Path $env:Path:"C:\Program Files\Git\usr\bin")) {[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Git\usr\bin", "Machine")}')
    print("git Env setup successfully! \n")

    print("Generating Ssh Key... \n")
    email = input("Enter your email > ")
    key_name = input("Specify key name, leave empty for default > ")
    if key_name == "":
        key_name = "id_rsa"

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

        op_tut = input_ans(
            "Do you want to open the tutorial right now? y/N > ")
        if op_tut == True:
            webbrowser.open(
                "https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account")
            print("New Tutorial Tab successfully opened! \n")
    else:
        print("Key not copied! \n")

    print("Adding Ssh-Agent...")
    show_output(
        ps_arg(r'Start-SshAgent;Add-SshKey $env:USERPROFILE\.ssh\{}'.format(key_name)))
    user_env = show_output(ps_arg(r'$env:USERPROFILE'))
    print(user_env)
    print("Ssh-Agent successfully added!\n")

    tst_auth = input_ans(
        "Do you want to Test authentication to GitHub?(NOTE: Your public key should be added on your Github A/C first.) y/N > ")
    if tst_auth == True:
        which_github = input_ans(
            "Do you use unique Organization github address?  y/N > ")
        if which_github == True:
            spec_url = input("Specify Organization github address > ")
            print("\nTesting authentication to GitHub...")
            show_output(ps_arg(r'ssh -T git@{}'.format(spec_url)))
        else:
            print("\nTesting authentication to GitHub...")
            show_output(ps_arg(r'ssh -T git@github.com'))
    else:
        print("\nSkipping GitHub authentication test! \n")


def config_global_git():
    config_ans = input_ans(
        "Do you want to Configure global Git settings? y/N > ")

    if config_ans == True:
        email, username = input(
            "Enter Your Github email address and username separated with space respectively > ").split()
        ps_arg(r'git config --global user.email {};git config --global user.name {};git config --global push.default simple;git config --global core.ignorecase false;git config --global core.autocrlf true'.format(email, username))
    else:
        print("Global Git settings not configured \n")


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
            print("Well, this is the end of the program execution \n")

        input("Press a key to exit")
    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)

    return


if __name__ == "__main__":
    run_as_admin()
