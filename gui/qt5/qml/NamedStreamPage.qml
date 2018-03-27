//StreamPage.qml
//
// A persistent named stream.

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BaseStreamPage {
    id : namedStreamPage
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Stream settings")
            onClicked : {
                var streamSettingsPage = rWin.loadPage("StreamSettingsPage")
                streamSettingsPage.streamName = streamName
                rWin.pushPageInstance(streamSettingsPage)
            }
        }
        MenuItem {
            text : qsTr("Refresh")
            onClicked : {
                refreshStream(streamName)
            }
        }
    }
    Keys.onPressed : {
        if (event.key == Qt.Key_F5) {
            refreshStream(streamName)
        }
    }
    // save active message when the user exists the page
    onIsActiveChanged : {
        if (!isActive) {
            saveActiveMessageTimer.running = false
            saveActiveMessage()
        }
    }
    onListViewMovementEnded : {
         // save active message a while after last list
        // via timer to avoid backend spamming
        // TODO: also save after relevant key presses
        saveActiveMessageTimer.restart()
    }

    // use a timer to batch active message saving requests
    // (we need to do this periodically as various quit/destroyed
    //  signals are not very reliable and it's always possible
    //  to get hard crash or hard kill/OOM kill)
    Timer {
        id : saveActiveMessageTimer
        interval : 1000
        repeat : false
        running : false
        onTriggered : {
            saveActiveMessage()
        }
    }
    function saveActiveMessage() {
        var modelIndex = namedStreamPage.indexAt(namedStreamPage.contentY)
        if (modelIndex != null) {
            rWin.log.info("saving stream index: " + modelIndex)
            var data = namedStreamPage.getItem(modelIndex).messageData
            rWin.python.call("tsubame.gui.streams.set_stream_active_message", [streamName, data], function(){})
        }
    }
}