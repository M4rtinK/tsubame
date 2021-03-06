// SmartGrid.qml
// Smart Grid is a smart Grid element that shows one column in portrait
// and two columns in landscape.

import QtQuick 2.0

Grid {
    width : parent.width - rWin.c.style.main.spacing
    property real cellWidth : width/columns
    // 2 columns in landscape, 1 in portrait
    columns : rWin.inPortrait ? 1 : 2
    spacing : rWin.c.style.main.spacing
}