//SearchStreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BaseTemporaryStreamPage {
    id : searchPage
    temporaryStream : true
    property string searchTerm : ""
    idleStateHeaderText: searchTerm
    // temporary stream always fetch messages on startup
    fetchingMessages : true

    Component.onCompleted : {
        // tell Python we want to have a temporary stream for a list setup
        rWin.python.call("tsubame.gui.streams.get_search_stream",
                         [searchPage.searchTerm],
        function(streamName){
            // the Python function call return a generated stream name we can then use to retrieve
            // the stream messages
            searchPage.streamName = streamName
        })
    }
}



