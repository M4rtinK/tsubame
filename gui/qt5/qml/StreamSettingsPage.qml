//StreamSettingsPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamSettings
    property string streamName : ""
    headerText : streamName
    content : ContentColumn {
        anchors.left : parent.left
        anchors.right : parent.right
        Button {
            anchors.centerIn : parent.centerIn
            // TODO: confirmation
            text : qsTr("Delete stream")
            onClicked : {
                streamSettings.deleteStream()
            }
        }
    }

    function deleteStream() {
        rWin.log.info("deleting stream " + streamSettings.streamName)
        rWin.python.call("tsubame.gui.streams.delete_stream", [streamSettings.streamName], function(success){
            if (success) {
                rWin.log.debug(qsTr("Stream ") + streamSettings.streamName + qsTr(" has been deleted."))
                rWin.pop()  // back from settings
                rWin.pop()  // back to stream list (hopefully :D)
                rWin.mapPage.reload_streams() // we really should rename this
            } else {
                rWin.log.debug(qsTr("Stream ") + streamSettings.streamName + qsTr(" can't be deleted due to an error."))
            }
        })
    }

}