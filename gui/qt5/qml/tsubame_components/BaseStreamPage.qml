//BaseStreamPage.qml
//
// A base element for message stream pages.
//
// Turns out there is quite a bit of common functionality
// that can be reused when implementing specialized
// message stream pages (named message streams, hashtags,
// user messages, arbitrary user favorites, arbitrary list etc.)

import QtQuick 2.0
import UC 1.0

BasePage {
    id : baseStreamPage
    property string streamName : ""
    // displayed when the stream is idle
    // (so derived pages can override it without having to reimplement
    // the "refreshing" text)
    property string idleStateHeaderText : streamName
    property bool temporaryStream : false
    property bool fetchingMessages : false
    property bool refreshInProgress : false
    property alias contentY : streamLW.contentY
    signal listViewMovementEnded
    headerText : refreshInProgress ? qsTr("Refreshing...") : idleStateHeaderText

    function indexAt(index) {
        return streamLW.indexAt(0, index)
    }

    function getItem(index) {
        return streamLW.model.get(index)
    }

    Keys.onPressed : {
        if (event.key == Qt.Key_F5) {
            refreshStream(streamName)
        }
    }
    content : ContentColumn {
        id : streamContent
        anchors.leftMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        anchors.rightMargin : rWin.isDesktop ? 0 : rWin.c.style.main.spacing
        ThemedListView {
            id : streamLW
            anchors.left : parent.left
            anchors.right : parent.right
            height : baseStreamPage.height - rWin.headerHeight
            model : ListModel {}
            // The messages are ordered as oldest -> newest in the list
            // and we want to have the newest messages on the top of the
            // list view. So use the bottom-to-top layout direction.
            verticalLayoutDirection : ListView.BottomToTop
            onMovementEnded : {
                // trigger the top-level signal so that listeners
                // (such ase stream position saving) can react
                baseStreamPage.listViewMovementEnded()
            }
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
                        var messagePage = rWin.loadPage("MessagePage", {"message" : clickedMessage})
                        rWin.pushPageInstance(messagePage)
                    }
                    onUserInfoClicked : {
                        rWin.log.info("user info clicked")
                        var userPage = rWin.loadPage("UserPage", {"user" : userInfo, "dataValid" : true})
                        rWin.pushPageInstance(userPage)
                    }
                }
            }
        }
    }
    Label {
        id : noStreamsLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : qsTr("<h2>No messages available.</h2>")
        visible : streamLW.model.count == 0 && !baseStreamPage.fetchingMessages
    }
    BusyIndicator {
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        visible : baseStreamPage.fetchingMessages
        running : baseStreamPage.fetchingMessages
    }
    onStreamNameChanged : {
        // Only fetch initial messages once the stream name is set.
        // This is important because for temporary streams as the stream
        // might not yet exists when the stream page is instantiated.
        get_messages()
    }

    Component.onDestruction: {
        // tell Python we no longer need any temporary streams possibly corresponding to this page
        if (baseStreamPage.temporaryStream) {
            rWin.python.call("tsubame.gui.streams.remove_temporary_stream", [baseStreamPage.streamName])
        }
    }

    function get_message_dict(message) {verticalCenter
        // full type-specific dict describing the message
        return {"messageData" : message}
    }

    function get_messages() {
        // reload the stream list from the Python backend
        rWin.log.info("loading messages for " + streamName)
        baseStreamPage.fetchingMessages = true
        rWin.python.call("tsubame.gui.streams.get_stream_messages", [streamName, baseStreamPage.temporaryStream], function(result){
            var message_list = result[0]
            var match_index = result[1]
            streamLW.model.clear()
            for (var i=0; i<message_list.length; i++) {
                streamLW.model.append(get_message_dict(message_list[i]))
            }
            baseStreamPage.fetchingMessages = false
            if (match_index != null) {
                rWin.log.info("restoring stream position to index: " + match_index)
                streamLW.positionViewAtIndex(match_index, ListView.Beginning)
            } else {
                rWin.log.info("setting stream position: end")
                streamLW.positionViewAtEnd()
            }
        })
    }

    function refreshStream() {
        // reload the stream list from the Python backend
        rWin.log.info("refreshing stream " + streamName)
        baseStreamPage.refreshInProgress = true
        rWin.python.call("tsubame.gui.streams.refresh_stream", [streamName, baseStreamPage.temporaryStream], function(message_list){
            for (var i=0; i<message_list.length; i++) {
                streamLW.model.append(get_message_dict(message_list[i]))
            }
            var messageCount = message_list.length
            if (messageCount > 0) {
                rWin.notify(qsTr("Added " + messageCount + " new messages."), 2000)
            } else {
                rWin.notify(qsTr("No new messages found."), 2000)
            }
        baseStreamPage.refreshInProgress = false
        })
    }
}