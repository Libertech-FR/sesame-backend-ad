"""Utility for AD and sesame """
import os.path
import sys
sys.path.append('.')
import paramiko
from jinja2 import FileSystemLoader,BaseLoader
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
    data = {
        'e': u.make_entry_array(entity),
        'config': u.get_config()
    }

    rdnValue=u.find_key(entity,'cn')
    x=type(rdnValue)
    if rdnValue is None:
        rdnValue='test'
    branchAttr=u.config('branchAttr','')
    data['rdnValue']=rdnValue
    if branchAttr != '':
        branchValue=u.find_key(entity,branchAttr)
        key_branch='branchFor' + branchValue
        branch=u.config(key_branch,'')
        data['branch']=branch
        template_string = 'cn={{ rdnValue}},{{ branch }},{{ config.base }}'
    else:
        template_string= 'cn={{ rdnValue}},{{ config.base }}'
    template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(u.config('dnTemplate',template_string))
    content = template.render(data)
    return content

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
        'e': u.make_entry_array(entity),
        'config': u.get_config(),
        'dataStatus' : entity['payload']['dataStatus']
    }

    environment = jinja2.Environment(loader=FileSystemLoader("../ps1_templates/"))
    template = environment.get_template(template)
    content=template.render(data)
    return content

def ad_exec_script(entity,template,params=""):
    if u.config('debug',0) == "1":
        __DEBUG__ = 1
    else:
        __DEBUG__ = 0
    content=gen_script_from_template(entity,template)
    client = open_ssh_conn()
    sshfile = client.open_sftp()
    pid=os.getpid()
    if __DEBUG__ == 0 :
        scriptName='sesame_script.' + str(pid) + '.ps1'
    else:
        scriptName = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".ps1"
    with sshfile.open(scriptName, mode="w") as message:
        message.write(content)
    ##execution du script
    chan = client.get_transport().open_session()
    if params == '':
        cmd=scriptName
    else:
        cmd=scriptName + " " + params
    if __DEBUG__ == 0 :
        chan.exec_command('powershell -ExecutionPolicy Bypass -NonInteractive -File ' + cmd)
        exitCode = chan.recv_exit_status()
        content = chan.recv(4096).decode()
        error = chan.recv_stderr(4096).decode()
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
    else:
        print(u.returncode(0, "Backend in debug mode"))

