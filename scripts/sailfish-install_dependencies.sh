#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run this script as root, otherwise packages can't be installed."
  exit
fi

cat << EOF

To run Python 3 + QML programs on Sailfish OS
the following needs to be installed:

- Python 3 for the Python code
- PyOtherSide to provide a Python 3 <-> QML bindings
- qmlscene to run the app from source
- qtchooser as qmlscene has some weird depndency issues
  without it
- lsb-release so that the Tsubame platform detection works correctly

As PyOtherSide depends on Python 3, we only need to
install thy pyotherside, qmlscene & qtchooser packages.
EOF

cat << EOF
Installing via pkcon:
pyotherside-qml-plugin-python3-qt5
qt5-qtdeclarative-qmlscene
qtchooser
lsb-release
EOF
pkcon install pyotherside qtchooser qt5-qtdeclarative-qmlscene lsb-release

echo "All done."
