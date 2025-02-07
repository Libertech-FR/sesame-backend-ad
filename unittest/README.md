# Tests Unitaires pour Backend AD

Avant de lancer les tests unitaires : 

* Creer un fichier files_ad_utils/config.conf
```
host=192.168.0.1
user=administrateur
base=dc=mondomaine,dc=fr
backendFor=adm,etd,esn
domain=mondomaine.fr
branchForetd=ou=etudiants
branchForadm=OU=administratifs
branchForesn=ou=Enseignants
branchAttr_old=departmentNumber
branchAttr=supannEntiteAffectationPrincipale
dnTemplate=cn={{e.cn}},{{branch}},{{config.base}}
debug=0
```
Les OU doivent exister dans AD

* Creer une clé privée ed25519 

La mettre dans le fichier files_ad_utils/id_ed25519

vous devez ajouter  la clé publique dans c:/programdata/ssh/administrators_authorized_keys sue le serveur AD 

Génération d'une clé privée : 
```
ssh-keygen -t ed25519 -f ./files_ad_utils/id_ed25519 -N ''

```

## Les differents tests 

### backendUtilsTest.py
teste les methodes de la librairie src/lib/backend_utlis.py

A besoin des fichiers du repertoire ./files_backend_utils et de ses fichiers

### adUtilsTest.py
Teste les methodes et les templates de la librairie src/lib/ad_utils.py

A besoin du repertoire files_ad_utils et de ses fichiers

## adBinTest.py
teste les scripts du repertoire src/bin en configuration reelle (fichier de cong etc/config.conf)