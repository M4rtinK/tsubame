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
    // move by small amount (up/down arrow)
    property real smallMove : themedListView.height / 4.0
    // move by whole "page", corresponding to visible content (page up/page down)
    property real pageMove : themedListView.height
    // smoothly animate the custom contentY changes during (custom) keyboard navigation
    Behavior on contentY{
        enabled : true
        id : yBehaviour
        SmoothedAnimation {
            id : scrollAnimation
            duration: 200
            onRunningChanged : {
                yBehaviour.enabled = false
                themedListView.flick(0, 0)
            }
        }
    }
    Keys.onPressed: {
        priority : Keys.BeforeItem
        var move_amount = 0
        // We set event.accept == true so that the up and down
        // event will not be forwarded to the default handlers
        // that attempt to move the highlight and change the
        // current index property and we don't want that as
        // it clashes with the custom keyboard navigation an
        // manual list view panning.
        switch (event.key) {
            case Qt.Key_Up:
                move_amount = -smallMove
                event.accepted = true
                break
            case Qt.Key_Down:
                move_amount = smallMove
                event.accepted = true
                break
            case Qt.Key_PageUp:
                move_amount = -pageMove
                event.accepted = true
                break
            case Qt.Key_PageDown:
                move_amount = pageMove
                event.accepted = true
                break
            case Qt.Key_Home:
                positionViewAtEnd()
                event.accepted = true
                break
            case Qt.Key_End:
                positionViewAtBeginning()
                event.accepted = true
                break
            default:
                move_amount = 0
        }
        var newContentY = contentY + move_amount
        if (move_amount > 0) {
            if (!themedListView.atYEnd) {
                yBehaviour.enabled = true
                themedListView.contentY = newContentY
            } else {
                themedListView.flick(0, -1)
            }
        } else if (move_amount < 0) {
            if (!themedListView.atYBeginning) {
                yBehaviour.enabled = true
                themedListView.contentY = newContentY
            } else {
                themedListView.flick(0, 1)
            }
        }
    }
}
