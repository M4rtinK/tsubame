//HashtagStreamPage.qml

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BaseTemporaryStreamPage {
    id : userTweetsPage
    temporaryStream : true
    property string username : ""
    idleStateHeaderText: "@" + username + " " + qsTr("tweets")
    // temporary stream always fetch messages on startup
    fetchingMessages : true

    onUsernameChanged : {
        // tell Python we want to have a temporary stream for a hashtag setup
        rWin.python.call("tsubame.gui.streams.get_user_tweets_stream", [userTweetsPage.username], function(streamName){
            // the Python function call return a generated stream name we can then use to retrieve
            // the stream messages
            userTweetsPage.streamName = streamName
        })
    }
}



