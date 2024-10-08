"""Utility for AD and sesame """
import os.path
import sys
sys.path.append('.')
import paramiko
from jinja2 import FileSystemLoader
import backend_utils as u
import jinja2

__DEBUG__=0
def set_config(config):
    u.__CONFIG__ = config

def open_ssh_conn():
    """Opening a ssh client connection with parameter in ../etc/config.conf"""
    pkey = paramiko.Ed25519Key.from_private_key_file('../.ssh/id_ed25519')
    client = paramiko.SSHClient()
    policy = paramiko.AutoAddPolicy()
    client.set_missing_host_key_policy(policy)
    host = u.config('host')
    user = u.config('user')
    try:
        client.connect(host, username=user, pkey=pkey)
        return client
    except paramiko.ssh_exception.SSHException as e:
        e_dict = e.args[0]
        print(u.returncode(1, "Erreur d'authentification"))
        exit(1)


def exec_cmd(command):
    """Exec directly a command (connexion and command)"""
    client=open_ssh_conn()
    stdin, stdout, stderr = client.exec_command(command)
    content=stdout.read().decode()
    del client, stdin, stdout, stderr
    return content

def compose_dn(entity):
    """Compose the DN of a identity"""
    rdnValue=u.find_key(entity,'cn')
    x=type(rdnValue)
    if rdnValue is None:
        rdnValue='test'
    branchAttr=u.config('branchAttr','')
    branch  = ''
    if branchAttr != '':
        branchValue=u.find_key(entity,branchAttr)

        match branchValue:
            case 'etd':
                branch=u.config('branchForEtd','')
            case 'esn':
                branch = u.config('branchForEsn', '')
            case 'adm':
                branch = u.config('branchForAdm', '')
    if branch != '':
        return 'cn=' + rdnValue+ ',' + branch + "," + u.config('base')
    else:
        return 'cn=' + rdnValue+  "," + u.config('base')

def dn_superior(dn):
   tab=dn.split(',')
   tab.pop(0)
   return ','.join(tab)


def test_conn():
    environment = jinja2.Environment(loader=FileSystemLoader("../ps1_templates/"))
    template = environment.get_template('ping.template')
    content=template.render({})
    scriptName='ping.ps1'
    client = open_ssh_conn()
    sshfile = client.open_sftp()
    with sshfile.open(scriptName, mode="w") as message:
        message.write(content)
    ##execution du script
    chan = client.get_transport().open_session()
    chan.exec_command('powershell -ExecutionPolicy Bypass -NonInteractive -File ping.ps1')
    exitCode = chan.recv_exit_status()
    content = chan.recv(4096).decode('utf-8')
    del client
    if exitCode == 0:
        print(u.returncode(0, content.rstrip("\n")))
        exit(0)
    else:
        print(u.returncode(1, content.rstrip("\n")))
        exit(1)

def gen_script_from_template(entity,template):
    data={
        'domain' :u.config('domain'),
        'base': u.config('base'),
        'dn' : compose_dn(entity),
        'path': dn_superior(compose_dn(entity)),
        'e': u.make_entry_array(entity)
    }
    environment = jinja2.Environment(loader=FileSystemLoader("../ps1_templates/"))
    template = environment.get_template(template)
    content=template.render(data)
    return content

def ad_exec_script(entity,template,params=""):
    content=gen_script_from_template(entity,template)
    client = open_ssh_conn()
    sshfile = client.open_sftp()
    pid=os.getpid()
    if __DEBUG__ == 0 :
        scriptName='sesame_script.' + str(pid) + '.ps1'
    else:
        scriptName='sesame_script.ps1'
    with sshfile.open(scriptName, mode="w") as message:
        message.write(content)
    ##execution du script
    chan = client.get_transport().open_session()
    if params == '':
        cmd=scriptName
    else:
        cmd=scriptName + " " + params
    chan.exec_command('powershell -ExecutionPolicy Bypass -NonInteractive -File ' + cmd)
    exitCode = chan.recv_exit_status()
    content = chan.recv(4096).decode('utf-8')
    error = chan.recv_stderr(4096).decode()
    if __DEBUG__ == 0:
        chan = client.get_transport().open_session()
        ##supression du script
        chan.exec_command('del ' + scriptName)
    del client
    if exitCode == 0:
        print(u.returncode(0,content.rstrip("\n")))
        exit(0)
    else:
        print(u.returncode(1,content.rstrip("\n")))
        exit(1)

