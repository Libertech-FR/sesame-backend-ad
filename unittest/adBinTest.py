import unittest
import subprocess
import os
import json
__PYTHONENV__='/../.venv/bin/python'
class adBinTest (unittest.TestCase):
    def run_backend(self,script, file= "",args=""):
        dir = os.getcwd()
        exe=dir + __PYTHONENV__
        execargs=[]
        execargs.append(exe)
        execargs.append(script)
        if args :
            execargs.append(args)
        if file == '':
            os.chdir('../src/bin')
            ret = subprocess.run(execargs,capture_output=True)
        else:
            #open file to pass to stdin
            fic = open(file, "r")
            content = fic.read()
            fic.close()
            os.chdir('../src/bin')
            ret = subprocess.run(execargs,input=content.encode(),capture_output=True)
        os.chdir(dir)
        return { "returncode" : ret.returncode,"stdout" : ret.stdout.decode()}

    def test_01ping(self):
        ret = self.run_backend('ping.py','')
        self.assertEqual(ret['returncode'],0)
        result=json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "I m alive")

    def test_02upsertidentity(self):
        ret = self.run_backend('upsertidentity.py','./files_ad_utils/identity1.json')
        self.assertEqual(ret['returncode'], 0)

    def test_03delentity(self):
        ret = self.run_backend('delentity.py', './files_ad_utils/identity1.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "user deleted")

    def test_04upsertidentity_add(self):
        ret = self.run_backend('upsertidentity.py', './files_ad_utils/identity1.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Identity created")

    def test_04upsertidentity_mod(self):
        ret = self.run_backend('upsertidentity.py', './files_ad_utils/identity1.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Identity modified")

    def test_05init_password(self):
        ret = self.run_backend('resetpwd.py', './files_ad_utils/resetpassword.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "password reseted")
    def test_06change_password(self):
        ret = self.run_backend('changepwd.py', './files_ad_utils/changepassword_true.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "Password changed")

    def test_07change_bad_password(self):
        ret = self.run_backend('changepwd.py', './files_ad_utils/changepassword_true.json')
        self.assertEqual(ret['returncode'], 1)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 1)
        self.assertEqual(result["message"], "Authentication Invalid password")

    def test_08desactivate(self):
        ret = self.run_backend('activation.py', './files_ad_utils/identity1.json',"--active=1")
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "user Enabled")

    def test_09activate(self):
        ret = self.run_backend('activation.py', './files_ad_utils/identity1.json',"--active=0")
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "user Disabled")

    def test_10upsertidentify_notconcerned(self):
        ret = self.run_backend('upsertidentity.py', './files_ad_utils/identity_notconcerned.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "not concerned")

    def test_11delentity_notconcerned(self):
        ret = self.run_backend('delentity.py', './files_ad_utils/identity_notconcerned.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "not concerned")

    def test_12init_password_notconcerned(self):
        ret = self.run_backend('resetpwd.py', './files_ad_utils/resetpassword_notconcerned.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "not concerned")

    def test_13change_password_notconcerned(self):
        ret = self.run_backend('changepwd.py', './files_ad_utils/changepassword_true_notconcerned.json')
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "not concerned")

    def test_14desactivate_notconcerned(self):
        ret = self.run_backend('activation.py', './files_ad_utils/identity_notconcerned.json',"--active=1")
        self.assertEqual(ret['returncode'], 0)
        result = json.loads(ret["stdout"])
        self.assertEqual(result["status"], 0)
        self.assertEqual(result["message"], "not concerned")

if __name__ == '__main__':
    unittest.main()
