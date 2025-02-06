"""Utility for AD and sesame """
import os.path
import sys
sys.path.append('.')
import paramiko
from jinja2 import FileSystemLoader,BaseLoader
import backend_utils as u
import jinja2
__PRIVATE_KEY__ = '../.ssh/id_ed25519'
__TEMPLATES_PS1__ = "../ps1_templates/"
__DEBUG__=0
def set_private_key(keyfile):
    global __PRIVATE_KEY__
    __PRIVATE_KEY__=keyfile

def set_template_ps1_dir(dir):
    global __TEMPLATES_PS1__
    __TEMPLATES_PS1__=dir
def set_config(config):
    u.__CONFIG__ = config
def set_debug():
    global __DEBUG__
    __DEBUG__=1
def open_ssh_conn():
    """Opening a ssh client connection with parameter in ../etc/config.conf"""
    pkey = paramiko.Ed25519Key.from_private_key_file(__PRIVATE_KEY__)
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
        if type(branchValue) is list:
            key_branch = 'branchFor' + branchValue[0]
        else:
            key_branch='branchFor' + branchValue
        if key_branch != '':
            branch=u.config(key_branch,'')
            data['branch']=branch
            if branch == "":
                template_string = 'cn={{ rdnValue}},{{ config.base }}'
            else:
                template_string = 'cn={{ rdnValue}},{{ branch }},{{ config.base }}'
        else:
            template_string = 'cn={{ rdnValue}},{{ config.base }}'
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
    environment = jinja2.Environment(loader=FileSystemLoader(__TEMPLATES_PS1__))
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
    return exitCode


def gen_script_from_template(entity,template):
    dataStatus = 0
    if 'dataStatus' in entity['payload'].keys():
        dataStatus = entity['payload']['dataStatus']
    elif 'dataStatus' in entity['payload']['identity']:
        dataStatus = entity['payload']['identity']['dataStatus']
    data={
        'domain' :u.config('domain'),
        'base': u.config('base'),
        'dn' : compose_dn(entity),
        'path': dn_superior(compose_dn(entity)),
        'e': u.make_entry_array(entity),
        'config': u.get_config(),
        'dataStatus' : dataStatus
    }

    environment = jinja2.Environment(loader=FileSystemLoader(__TEMPLATES_PS1__))
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
            return(0)
        else:
            print(u.returncode(1,content.rstrip("\n")))
            return(1)
    else:
        print(u.returncode(0, "Backend in debug mode"))
        return(0)

def ad_exec_script_content(entity,template,params=""):
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
        return(content.rstrip("\n"))
    else:
        return("")
def reset_password(entity):
    x= ad_exec_script(entity, 'resetpassword.template',"-user " + entity['payload']['uid'] + " -newp " + '"' + entity['payload']['newPassword'] + '"')
    return x
def change_password(entity):
    r=ad_exec_script(entity, 'changepassword.template',
                      "-user " + entity['payload']['uid'] + ' -oldp "' + entity['payload']['oldPassword'] + '" -newp "' +
                      entity['payload']['newPassword'] + '"')
    return(r)