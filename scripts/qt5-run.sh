#!/bin/bash
# Run Tsubame with the Qt5 GUI using QtQuick Controls
cd ..
# path to the main QML file
QML_MAIN="gui/qt5/qml/main.qml"
# path to the component set
COMPONENTS="gui/qt5/qml/universal_components/controls"

qmlscene ${QML_MAIN} -I ${COMPONENTS}
