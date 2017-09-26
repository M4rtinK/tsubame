//ThemedListView.qml
//
// A list view respecting Tsubame styles, themes
// and default settings.
// Main aim - have the stuff here so it does not have
// to be filled again foe each instance.

import QtQuick 2.0
import UC 1.0

PlatformListView {
    id : llw
    spacing : rWin.isDesktop ? rWin.c.style.listView.spacing/4 : rWin.c.style.listView.spacing
    clip : true

    focus : false
    interactive : true
    //snapMode : ListView.SnapToItem
    //highlightRangeMode : ListView.StrictlyEnforceRange
    //highlightRangeMode : ListView.NoHighlightRange
    highlightRangeMode : ListView.NoHighlightRange
    highlightFollowsCurrentItem : true
    highlightMoveVelocity : -1
    highlightMoveDuration : -1
    property int customIndex : 0
    //preferredHighlightBegin : -100

    //preferredHighlightEnd : 500

    onFlickingChanged : {
        console.log("FLICKING: " + flicking)
        if (flicking) {
            console.log("APPLY")
            //highlightFollowsCurrentItem = false
            currentIndex = -1
            console.log(highlightFollowsCurrentItem)
            //highlightRangeMode : ListView.ApplyRange
        } else {
            console.log("STRICTLY " + contentY)
            llw.customIndex = llw.indexAt(0,contentY)
            //highlightRangeMode : ListView.StrictlyEnforceRange
        }
    }

    Keys.onPressed: {
        rWin.log.debug("PAGE KEY PRESSED: " + event.key)
        event.accept = false
        if (!currentIndex) {
            currentIndex = customIndex
        }
        highlightFollowsCurrentItem = true
        console.log(highlightFollowsCurrentItem)
    }

    onCurrentIndexChanged : {
        console.log("CURRENT INDEX: " + currentIndex)
        console.log(highlightFollowsCurrentItem)
    }


}

