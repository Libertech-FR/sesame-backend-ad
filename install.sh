#!/bin/bash
echo "Deploiment du module AD"
echo "La position determinera l'ordre d'execution des backends (comme dans init.d)"
read -p "Numero de demarrage du module (2 positions):" NUM
echo "installation dans backends/${NUM}openldap"
BACKEND=ad
INSTALL=../../backends/${NUM}${BACKEND}
if [  -d ../../backends/${NUM}${BACKEND} ];then
   echo "Repertoire deja existant choisissez un autre numéro"
   exit 1
else
   mkdir ../../backends/${NUM}${BACKEND}
fi
echo "Copie des fichiers dans ${INSTALL}"
mkdir $INSTALL/etc
cp  ./etc/* $INSTALL/etc
mkdir $INSTALL/bin
mkdir $INSTALL/lib
PWD=`pwd`
cp ./lib/__init__.py $INSTALL/lib
ln -s $PWD/lib/backend_utils.py $INSTALL/lib/backend_utils.py
ln -s $PWD/lib/ad_utils.py $INSTALL/lib/ad_utils.py
ln -s $PWD/bin/changepwd.py $INSTALL/bin/changepwd.py
ln -s $PWD/bin/ping.py $INSTALL/bin/ping.py
ln -s $PWD/bin/resetpwd.py $INSTALL/bin/resetpwd.py
ln -s $PWD/bin/upsertidentity.py $INSTALL/bin/upsertidentity.py
chmod 700 $INSTALL/bin/*
mkdir $INSTALL/ps1_templates
cp ./ps1_templates/* $INSTALL/ps1_templates
chmod 600 $INSTALL/ps1_templates/*
cp config.yml $INSTALL

echo "Le backend a été installé dans $INSTALL"
echo "Configuration"
read -p "Adresse du serveur AD primaire : " HOST
read -p "Utilisateur (doit avoir les droits d'administration) : " USER
read -s -p "Mot de passe : " PASSWORD
echo ""
read -p "Base ldap AD : " BASE
read -p "Domaine pour UserPrincipalName : " DOMAIN
echo "Génération du fichier de configuration"
CONFFILE=${INSTALL}/etc/config.conf
echo "host=${HOST}" > ${CONFFILE}
echo "user=${USER}" >> ${CONFFILE}
echo "base=${BASE}" >> ${CONFFILE}
echo "domain=${DOMAIN}" >> ${CONFFILE}
echo "backendFor=adm,etd,esn" >> ${CONFFILE}
chmod 600 ${CONFFILE}
echo "Generation d'une clé ssh"
if [ ! -f $INSTALL/.ssh/id_ed25519 ];then
  mkdir $INSTALL/.ssh 2>/dev/null
  ssh-keygen -t ed25519 -f ${INSTALL}/.ssh/id_ed25519 -N ''
fi
./copy_ssh_key.py --server=${HOST} --user=${USER} --password="${PASSWORD}" --keyfile=${INSTALL}/.ssh/id_ed25519.pub
OK=$?
if [ $OK -ne 0 ];then
  echo "Impossible de copier la clé sur le serveur  windows. Verifier que l'utilisateur a les droits d'administration"
  echo "Installation avortée"
  exit 1
fi
#test de connection
echo "Test de connection"
cd ${INSTALL}/bin
./ping.py
OK=$?
if [ $OK -eq 0 ];then
  echo "Test de connexion OK "
else
  echo" Erreur de connexion"
fi
systemctl restart sesame-daemon
echo "Vous pouvez completer le fichier de configuration avec les parametres optionnels (voir README.md)"
echo "Merci "