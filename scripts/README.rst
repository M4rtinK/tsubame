Tsubame utility scripts
=======================

This folder contains various utility scripts that
can be useful for Tsubame development or when
running Tsubame from a git clone without installation.

qt5-run.sh
----------

Run Tsubame via qmlscene on a "normal" system that has 
a reasonably modern Qt 5 installation with Qt Quick Controls 2 
available. This could be a modern Fedora release for example,
but really any Qt 5 & Controls 2 environment should do.

This uses the Universal Components "controls" backend.

sailfish-install_dependencies.sh
--------------------------------

Installs dependencies needed to successfully run
Tsubame from a git clone. This script needs to be
run as root, otherwise it can't install packages.

Check the script if you want to see what packages
it installs.

sailfish-run.sh
---------------

Runs Tsubame via qmlscene on Sailfish OS with
the "silica" Universal Components backend.

If this fails to run, try running the
sailfish-install_dependencies.sh script
first.
