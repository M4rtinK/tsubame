//MessageInteractionPage.qml

import QtQuick 2.0
import QtWebKit 3.0
import UC 1.0
import "tsubame_components"

BasePage {
    id : messagePage
    property var message
    property string messageInteractionUsername
    headerText : qsTr("Tweet interaction")

    content : ContentColumn {
        Item {
            id : spaceItem
            height : rWin.c.style.main.spacing
            width : rWin.c.style.main.spacing
        }
        AccountComboBox {
            id : accountCB
            label : qsTr("Account")
            width : parent.width / 2
            anchors.horizontalCenter : parent.horizontalCenter
            onSelectedAccountUsernameChanged : {
                messageInteractionUsername = selectedAccountUsername
            }
        }

        Button {
            id : retweetActionButton
            anchors.horizontalCenter : accountCB.horizontalCenter
            text : qsTr("Retweet")
            visible : messageInteractionUsername
            onClicked : {
                rWin.python.call("tsubame.gui.messages.post_retweet",
                [messageInteractionUsername, message.id_str],
                function(result){
                    var message = ""
                    if (result[0] == true) {
                        message = qsTr("Tweet has been retweeted")
                    } else {
                        message = qsTr("Retweet failed")
                        if (result[1]) {
                            message = message + ": " + result[1]
                        }
                    }
                    rWin.notify(message)
                })
            }
        }
        Button {
            id : favoriteActionButton
            anchors.horizontalCenter : accountCB.horizontalCenter
            text : qsTr("Favorite")
            visible : messageInteractionUsername
            onClicked : {
                rWin.python.call("tsubame.gui.messages.create_favorite",
                [messageInteractionUsername, message.id_str],
                function(result){
                    var message = ""
                    if (result[0] == true) {
                        message = qsTr("Tweet has been favorited")
                    } else {
                        message = qsTr("Favorite failed")
                        if (result[1]) {
                            message = message + ": " + result[1]
                        }
                    }
                    rWin.notify(message)
                })
            }
        }
        /*
        Button {
            id : replyButton
            text : qsTr("Reply")
        }
        */
    }
}