import unittest
import sys
sys.path.append('../src/lib')
import json
import ad_utils as ad
import backend_utils as u
class backendAdCase(unittest.TestCase):
    def connection(self):
        config = u.read_config('./files_ad_utils/config.conf')
        ad.set_config(config)
        ad.set_private_key('./files_ad_utils/id_ed25519')
        ad.set_template_ps1_dir('../src/ps1_templates/')

    def test_00prepare(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        ad.ad_exec_script(entity, 'delentity.template')
        entity = u.readjsonfile("./files_ad_utils/identity_complex.json")
        ad.ad_exec_script(entity, 'delentity.template')

    def test_01connection(self):
        self.connection()
        self.assertEqual(ad.test_conn(),0)
    def test_02createIdentity(self):
        self.connection()
        # creation de l identité
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        self.assertEqual(ad.ad_exec_script(entity, 'upsertidentity.template'),0)
        # on relit l'identité pour la verifier
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content=ad.ad_exec_script_content(entity,'readuser.template')
        self.assertNotEqual(content,'')
        user=json.loads(content)
        self.assertEqual(user['GivenName'],'Olivier')
        self.assertEqual(user['Surname'], 'Maton')
        self.assertEqual(user['UserPrincipalName'],'omaton@libertest1.fr')
        self.assertEqual(user['SamAccountName'], 'omaton')
        self.assertEqual(user['DistinguishedName'], 'CN=Maton Olivier,OU=Administratifs,DC=libertest1,DC=fr')
        self.assertEqual(user['EmailAddress'], 'olivier.maton@exemple.fr')

    def test_03modifyentry(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        entity['payload']['identity']['identity']['inetOrgPerson']['mail']="omaton@exemple.fr"
        self.assertEqual(ad.ad_exec_script(entity, 'upsertidentity.template'), 0)
        ## test si l entree a été bien changée
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content = ad.ad_exec_script_content(entity, 'readuser.template')
        self.assertNotEqual(content, '')
        user = json.loads(content)
        self.assertEqual(user['GivenName'], 'Olivier')
        self.assertEqual(user['Surname'], 'Maton')
        self.assertEqual(user['UserPrincipalName'], 'omaton@libertest1.fr')
        self.assertEqual(user['SamAccountName'], 'omaton')
        self.assertEqual(user['DistinguishedName'], 'CN=Maton Olivier,OU=Administratifs,DC=libertest1,DC=fr')
        self.assertEqual(user['EmailAddress'],'omaton@exemple.fr')

    def test_04changecn(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        entity['payload']['identity']['identity']['inetOrgPerson']['cn'] = "MATON Olivier Junior"
        self.assertEqual(ad.ad_exec_script(entity, 'upsertidentity.template'), 0)
        ## test si l entree a été bien changée
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content = ad.ad_exec_script_content(entity, 'readuser.template')
        self.assertNotEqual(content, '')
        user = json.loads(content)
        self.assertEqual(user['DistinguishedName'], 'CN=MATON Olivier Junior,OU=Administratifs,DC=libertest1,DC=fr','DN non modifié')

    def test_05deleteuser(self):
        self.connection()
        # on delete l identité pour etre sur de la recreer
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        ad.ad_exec_script(entity, 'delentity.template')
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content = ad.ad_exec_script_content(entity, 'readuser.template')
        self.assertEqual(content,'')

    def test_06complex_name(self):
        self.connection()
        # creation de l identité
        entity = u.readjsonfile("./files_ad_utils/identity_complex.json")
        self.assertEqual(ad.ad_exec_script(entity, 'upsertidentity.template'), 0)
        # on relit l'identité pour la verifier
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content = ad.ad_exec_script_content(entity, 'readuser.template')
        self.assertNotEqual(content, '')
        user = json.loads(content)
        self.assertEqual(user['GivenName'], 'Olivier')
        self.assertEqual(user['Surname'], "D'Maton")
        self.assertEqual(user['UserPrincipalName'], 'omaton@libertest1.fr')
        self.assertEqual(user['SamAccountName'], 'omaton')
        self.assertEqual(user['DistinguishedName'], "CN=D'Maton Olivier,OU=Administratifs,DC=libertest1,DC=fr")
        self.assertEqual(user['EmailAddress'], 'olivier.maton@exemple.fr')
        ## tout est ok on delete l'entree
        ad.set_template_ps1_dir('../src/ps1_templates/')
        self.assertEqual(ad.ad_exec_script(entity, 'delentity.template'),0)

    def test_07moveou(self):
        ## creation de l entree
        self.test_02createIdentity()
        self.connection()
        ## changement du type de population
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        entity['payload']['identity']['identity']['additionalFields']['attributes']['supannPerson']['supannEntiteAffectationPrincipale']="esn"
        self.assertEqual(ad.ad_exec_script(entity, 'upsertidentity.template'), 0)
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content = ad.ad_exec_script_content(entity, 'readuser.template')
        self.assertNotEqual(content, '')
        user = json.loads(content)
        self.assertEqual(user['DistinguishedName'], 'CN=Maton Olivier,OU=Enseignants,DC=libertest1,DC=fr','DN non modifié')
        self.test_05deleteuser()

    def test_08reset_password(self):
        self.test_02createIdentity()
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/resetpassword.json")
        self.assertEqual(ad.reset_password(entity),0)
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        self.assertEqual(ad.ad_exec_script(entity,'checkpwd.template','-user omaton -password "Abbert1xIEIIE88!"'),0)

    def test_09change_password(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/changepassword_true.json")
        self.assertEqual(ad.change_password(entity),0)
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        self.assertEqual(ad.ad_exec_script(entity, 'checkpwd.template', '-user omaton -password "AbCx34IddWZE1!"'), 0)

    def test_10reset_password_on_active_user(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/resetpassword.json")
        self.assertEqual(ad.reset_password(entity),0)
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        self.assertEqual(ad.ad_exec_script(entity,'checkpwd.template','-user omaton -password "Abbert1xIEIIE88!"'),0)
    def test_11reset_with_special_char(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/resetpassword.json")
        entity['payload']['newPassword']='AZE123&$*<>@#!%|[]()°-_§$^¨'
        self.assertEqual(ad.reset_password(entity), 0)
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        self.assertEqual(ad.ad_exec_script(entity, 'checkpwd.template', '-user omaton -password "AZE123&$*<>@#!%|[]()°-_§$^¨"'), 0)

    def test_12disable_user(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        self.assertEqual(ad.ad_exec_script(entity,"disable.template"),0)
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content = ad.ad_exec_script_content(entity, 'readuser.template')
        self.assertNotEqual(content, '')
        user = json.loads(content)
        self.assertFalse(user['Enabled'])

    def test_13try_to_reset(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/resetpassword.json")
        entity['payload']['dataStatus']=-3
        self.assertEqual(ad.reset_password(entity), 1)

    def test_14try_to_change_password(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/changepassword_true.json")
        self.assertEqual(ad.change_password(entity), 1)

    def test_15enable_user(self):
        self.connection()
        entity = u.readjsonfile("./files_ad_utils/identity1.json")
        self.assertEqual(ad.ad_exec_script(entity, "enable.template"), 0)
        ad.set_template_ps1_dir('./files_ad_utils/ps1_templates/')
        content = ad.ad_exec_script_content(entity, 'readuser.template')
        self.assertNotEqual(content, '')
        user = json.loads(content)
        self.assertTrue(user['Enabled'])

if __name__ == '__main__':
    unittest.main()
