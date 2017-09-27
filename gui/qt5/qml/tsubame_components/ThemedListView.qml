//ThemedListView.qml
//
// A list view respecting Tsubame styles, themes
// and default settings.
// Main aim - have the stuff here so it does not have
// to be filled again foe each instance.

import QtQuick 2.0
import UC 1.0

PlatformListView {
    id : themedListView
    spacing : rWin.isDesktop ? rWin.c.style.listView.spacing/4 : rWin.c.style.listView.spacing
    clip : true
    focus : true
    currentIndex : -1
    property int customIndex : 0
    property real oldFlickDeceleration : 0

    property real flickStartY : 0

    Behavior on contentY{
        enabled : true
        id : yBehaviour
        NumberAnimation {
            id : scrollAnimation
            duration: 200
            onRunningChanged : {
                themedListView.flick(0, 0)
            }
        }
    }
   Keys.onPressed: {
        priority : Keys.BeforeItem
        rWin.log.debug("listview KEY PRESSED: " + event.text)
        var flick_amount = 0
        switch (event.key) {
            case Qt.Key_Up:
                flick_amount = -themedListView.height / 4.0
                //flick_amount = -100
                event.accepted = true
                break
            case Qt.Key_Down:
                flick_amount = themedListView.height / 4.0
                flick_amount = 100
                event.accepted = true
                break
            case Qt.Key_PageUp:
                flick_amount = -themedListView.height
                event.accepted = true
                break
            case Qt.Key_PageDown:
                flick_amount = themedListView.height
                event.accepted = true
                break
            default:
                flick_amount = 0
        }
        var newContentY = contentY + flick_amount

        if (flick_amount > 0) {
            if (!themedListView.atYEnd) {
                themedListView.contentY = newContentY
            } else {
                themedListView.flick(0, -1)
            }

        } else if (flick_amount <0) {
            if (!themedListView.atYBeginning) {
                themedListView.contentY = newContentY
            } else {
                themedListView.flick(0, 1)
            }
        }
    }
}

