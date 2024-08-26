#!/usr//bin/python3 -u
import paramiko
import argparse
parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')
parser.add_argument('-s', '--server')
parser.add_argument('-u', '--user')      # option that takes a value
parser.add_argument('-p', '--password')
parser.add_argument('-k', '--keyfile')
args = parser.parse_args()

client = paramiko.SSHClient()
policy = paramiko.AutoAddPolicy()
client.set_missing_host_key_policy(policy)
try:
    client.connect(hostname=args.server, username=args.user, password=args.password)
    sshfile = client.open_sftp()
    with open(args.keyfile) as f: new_key = f.read()
    ## ouverture sur windows du authorized_Keys
    with sshfile.open(".ssh/authorized_keys", mode="a") as message:
        message.write(new_key)
        message.close()
    del client
except paramiko.ssh_exception.SSHException as e:
        e_dict = e.args[0]
        print("Erreur d'authentification")
        exit(1)

