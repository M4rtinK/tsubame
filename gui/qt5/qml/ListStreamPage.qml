//ListStreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BaseTemporaryStreamPage {
    id : listPage
    temporaryStream : true
    property string accountUsername : ""
    property string listOwnerUsername : ""
    property string listName : ""
    // List slug has unlike name properly transformed spaces
    // and other symbols that can otherwise we problematic when retrieving
    // list data.
    property string listSlug: ""
    property bool isPrivate: false
    property string headerPrefix: isPrivate ? "🔒" : "📢"
    idleStateHeaderText: headerPrefix + listName
    // temporary stream always fetch messages on startup
    fetchingMessages : true

    Component.onCompleted : {
        // tell Python we want to have a temporary stream for a list setup
        rWin.python.call("tsubame.gui.streams.get_list_stream",
                         [accountUsername, listOwnerUsername, listSlug],
        function(streamName){
            // the Python function call return a generated stream name we can then use to retrieve
            // the stream messages
            listPage.streamName = streamName
        })
    }
}



