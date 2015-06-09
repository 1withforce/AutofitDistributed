#!/bin/bash
# Installs required packages for distributed autofit and the distributed network.
function checkPackage {
	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $1|grep "install ok installed");
	return $PKG_OK;
}
function installPackage {
	PKG_NAME=$1
	PKG_OK=$(checkPackage $PKG_NAME)
	echo "Checking for $PKG_NAME: $PKG_OK"
	if [ "" == "$PKG_OK" ]; then
  		echo "No $PKG_NAME. Setting up $PKG_NAME."
  		sudo apt-get --force-yes --yes install $PKG_NAME
	fi
}

# Autofit dependencies: Numpy, Scipy
installPackage python-numpy
installPackage python-scipy

# Distributed Network dependencies: boto, paramiko
installPackage python-boto
installPackage python-paramiko
