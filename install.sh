#!/bin/bash
echo "Deploiment du module LDAP"
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
cp ./bin/* $INSTALL/bin
chmod 700 $INSTALL/bin/*
mkdir $INSTALL/lib
PWD=`pwd`
cp ./lib/__init__.py $INSTALL/lib
ln -s $PWD/lib/backend_utils.py $INSTALL/lib/backend_utils.py
ln -s $PWD/lib/ad_utils.py $INSTALL/lib/ad_utils.py
cp config.yml $INSTALL

echo "Le backend a été installé dans $INSTALL"
echo "Configuration"
read -p "Url du serveur AD  : " HOST
read -p "Utilisateur (doit avoir les droits d'ecriture) : " DN
read -p "Mot de passe : " PASSWORD
read -p "Base ldap AD : " BASE
read -p "Domaine pour UserPrincipalName : " DOMAIN
echo "Génération du fichier de configuration"
CONFFILE=${INSTALL}/etc/config.conf
echo "host=${HOST}" > ${CONFFILE}
echo "user=${DN}" >> ${CONFFILE}
echo "password=${PASSWORD}" >> ${CONFFILE}
echo "base=${BASE}" >> ${CONFFILE}
echo "domain=${DOMAIN}" >> ${CONFFILE}
echo "backendFor=adm,etd,esn" >> ${CONFFILE}
chmod 600 ${CONFFILE}
systemctl restart sesame-daemon
echo "Vous pouvez completer le fichier de configuration avec les parametres optionnels (voir README.md)"
echo "Merci "