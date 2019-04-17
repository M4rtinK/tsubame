//MessageContainer.qml

import QtQuick 2.0
import UC 1.0

Column {
    id : messageContainer
    property var message
    property bool retweeted : message.tsubame_message_is_retweet
    property bool quoted : message.tsubame_message_is_quote
    signal userInfoClicked(var userInfo)
    signal messageClicked(var clickedMessage)
    property bool messageClickable : true
    property real horizontalMargin : rWin.c.style.main.spacing
    // this is a very gross hack for positioning the furigana webview
    property int headerHeight : headerTBR.height

    function handleMessageClicked () {
        if (retweeted) {
            // we need to fake the retweeted message a bit
            var clickedMessage = messageContainer.message.retweeted_status
            // set full text & full text plaintext
            // (this way we don't need to duplicate these in the dict send from Python)
            clickedMessage.full_text = messageContainer.message.full_text
            clickedMessage.tsubame_full_text_plaintext = messageContainer.message.full_text_plaintext
            // set media
            clickedMessage.media = messageContainer.message.media
            // and also make sure this si no longer considered to be a retweet or quote
            clickedMessage.tsubame_message_is_retweet = false
            clickedMessage.tsubame_message_is_quote = false
            // now finally trigger the signal
            messageContainer.messageClicked(clickedMessage)
        } else {
            // this is not a retweet, so we can simply use the message
            messageContainer.messageClicked(messageContainer.message)
        }
    }

    function handleQuoteClicked () {
        // we need to fake the quoted message a bit
        var clickedMessage = messageContainer.message.quoted_status
        // set media
        clickedMessage.media = messageContainer.message.media
        // and also make sure this si no longer considered to be a retweet or quote
        clickedMessage.tsubame_message_is_retweet = false
        clickedMessage.tsubame_message_is_quote = false
        // now finally trigger the signal
        messageContainer.messageClicked(clickedMessage)
    }

    ThemedBackgroundRectangle {
        width : messageContainer.width
        height : reTweetLabel.height + rWin.c.style.main.spacing * 3.0
        visible : messageContainer.retweeted
        Label {
            id : reTweetLabel
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            text : messageContainer.message.tsubame_retweet_user ?
                "🔃" + qsTr("Retweeted by") + " <b>" +
                messageContainer.message.tsubame_retweet_user.name + "</b>"
            : ""
        }
        onClicked : {
            messageContainer.userInfoClicked(messageContainer.message.tsubame_retweet_user)
        }
    }

    ThemedBackgroundRectangle {
        id : headerTBR
        pressed_override : bodyTBR.pressed || mediaTBR.pressed || originTBR.pressed
        width : messageContainer.width
        height : messageHeader.height + rWin.c.style.main.spacing * 2.0
        UserInfo {
            id : messageHeader
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            user : messageContainer.message.user
        }
        onClicked : {
            messageContainer.userInfoClicked(messageHeader.user)
        }
    }
    ThemedBackgroundRectangle {
        id : bodyTBR
        pressed_override : mediaTBR.pressed || originTBR.pressed
        enabled : messageClickable
        width : messageContainer.width
        height : messageBody.height + quoteTBR.height + rWin.c.style.main.spacing * 3.0
        MessageBody {
            id : messageBody
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            message : messageContainer.message
        }
        ThemedBackgroundRectangle {
            id : quoteTBR
            anchors.top : messageBody.bottom
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            anchors.right : parent.right
            anchors.rightMargin : horizontalMargin
            visible : messageContainer.quoted
            height : visible ? quoteHeader.height + quoteBody.height + rWin.c.style.main.spacing * 3.0 : 0
            borderWidth : 2 * rWin.c.style.m
            Label {
                id : quoteHeader
                anchors.top : parent.top
                anchors.topMargin : rWin.c.style.main.spacing
                anchors.left : parent.left
                anchors.leftMargin : horizontalMargin * 2
                anchors.right : parent.right
                anchors.rightMargin : horizontalMargin * 2

                text : messageContainer.message.quoted_status ?
                    "<b>" + messageContainer.message.quoted_status.user.name + "</b> @" +
                    messageContainer.message.quoted_status.user.screen_name : ""
            }
            MessageBody {
                id : quoteBody
                anchors.top : quoteHeader.bottom
                anchors.topMargin : rWin.c.style.main.spacing
                anchors.left : parent.left
                anchors.leftMargin : horizontalMargin * 2
                anchors.right : parent.right
                anchors.rightMargin : horizontalMargin * 2
                message : messageContainer.message.quoted_status
            }
            onClicked : {
                handleQuoteClicked()
            }
        }
        onClicked : {
            handleMessageClicked()
        }
    }
    ThemedBackgroundRectangle {
        id : mediaTBR
        pressed_override : bodyTBR.pressed || mediaTBR.pressed
        enabled : messageClickable
        width : messageContainer.width
        height : mediaGrid.visible ? mediaGrid.height + rWin.c.style.main.spacing * 2.0 : 0
        MediaGrid {
            id : mediaGrid
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            mediaList : messageContainer.message.media
            spacing : rWin.c.style.main.spacing / 2.0
        }
        onClicked : {
            handleMessageClicked()
        }
    }
    ThemedBackgroundRectangle {
        id : originTBR
        pressed_override : bodyTBR.pressed
        enabled : messageClickable
        width : messageContainer.width
        height : messageOrigin.height + rWin.c.style.main.spacing * 2.0
        MessageOrigin {
            id : messageOrigin
            anchors.top : parent.top
            anchors.topMargin : rWin.c.style.main.spacing
            anchors.left : parent.left
            anchors.leftMargin : horizontalMargin
            width : messageContainer.width - horizontalMargin * 2.0
            message : messageContainer.message
        }
        onClicked : {
            handleMessageClicked()
        }
    }
}

