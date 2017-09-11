//StreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : streamPage
    property string streamName : ""
    property bool fetching_messages : false
    headerText : streamName
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
    content : ContentColumn {
        //anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        //anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        ThemedListView {
            id : streamLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : streamPage.height
            model : ListModel {}
            // The messages are ordered as oldest -> newest in the list
            // and we want to have the newest messages on the top of the
            // list view. So use the bottom-to-top layout direction.
            verticalLayoutDirection : ListView.BottomToTop
            delegate : ThemedBackgroundRectangle {
                id : messageDelegate
                width : streamLW.width
                height : messageC.height + rWin.c.style.listView.itemBorder
                MessageContainer {
                    id : messageC
                    message : messageData
                    // Explicit width setting is needed due to the MediaGrid
                    // for some reason. We should probably fix that.
                    width : messageDelegate.width
                    onMessageClicked : {
                        rWin.log.info("message clicked")
                        var messagePage = rWin.loadPage("MessagePage", {"message" : messageData})
                        rWin.pushPageInstance(messagePage)
                    }
                }
            }
        }
    }
    Label {
        id : noStreamsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : fetching_messages ? qsTr("<h2>No messages available.</h2>") : qsTr("<h2>Fetching messages.</h2>")
        visible : streamLW.model.count == 0
    }
    onStreamNameChanged : {
        get_messages()
    }

    function get_message_dict(message) {verticalCenter
        // full type-specific dict describing the message
        return {"messageData" : message}
    }

    function get_messages() {
        // reload the stream list from the Python backend
        rWin.log.info("loading messages for " + streamName)
        rWin.python.call("tsubame.gui.streams.get_stream_messages", [streamName, false], function(message_list){
            streamLW.model.clear()
            fetching_messages = true
            for (var i=0; i<message_list.length; i++) {
                streamLW.model.append(get_message_dict(message_list[i]))
            }
            streamLW.positionViewAtEnd()
        })
    }

    function refreshStream() {
        // reload the stream list from the Python backend
        rWin.log.info("refreshing stream " + streamName)
        rWin.python.call("tsubame.gui.streams.refresh_stream", [streamName], function(message_list){
            for (var i=0; i<message_list.length; i++) {
                streamLW.model.append(get_message_dict(message_list[i]))
            }
            var messageCount = message_list.length
            if (messageCount > 0) {
                rWin.notify(qsTr("Added " + messageCount + " new messages."), 2000)
            } else {
                rWin.notify(qsTr("No new messages found."), 2000)
            }
        })
    }
}