//HashtagStreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BaseStreamPage {
    id : hashtagPage
    temporaryStream : true
    property string hashtag : ""
    idleStateHeaderText: "#" + hashtag

    onHashtagChanged : {
        // tell Python we want to have a temporary stream for a hashtag setup
        rWin.python.call("tsubame.gui.streams.get_hashtag_stream", [hashtagPage.hashtag], function(streamName){
            // the Python function call return a generated stream name we can then use to retrieve
            // the stream messages
            hashtagPage.streamName = streamName
        })
    }
}



