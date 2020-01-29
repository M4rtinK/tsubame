#!/bin/bash
# Run Tsubame with the Qt5 GUI using Silica on Sailfish OS
cd ..
# path to the main QML file
QML_MAIN="gui/qt5/qml/main.qml"
# path to the component set
COMPONENTS="gui/qt5/qml/universal_components/silica"

qmlscene ${QML_MAIN} -I ${COMPONENTS}
