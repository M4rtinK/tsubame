//TextBoxPage.qml
//
// A page that displays a piece of text in a textboax
// with a header. This way the user can copy paste
// pieces of the text (generally a Twitter message, user
// profile text, etc.) or even first edit and then copy paste
// the result.

import QtQuick 2.0
import UC 1.0
import "tsubame_components"
import "functions.js" as F

BasePage {
    id : sendMessagePage
    headerText : qsTr("Send Tweet")
    headerMenu : TopMenu {
        MenuItem {
            text: qsTr("Add media")
            onClicked : {
                rWin.log.info('media adding not yet implemented')
            }
        }
    }

    property string messageText : ""
    property int characterCount : 0
    property string messageAccountUsername : ""
    property bool mediaUploadInProgress : false
    property int media1 : 0
    property int media2 : 0
    property int media3 : 0
    property int media4 : 0
    property bool readyToSend : messageText && messageAccountUsername && !mediaUploadInProgress
    property bool sending : false
    content : ContentColumn {

        ThemedTextRectangle {
            width : sendMessagePage.width - rWin.c.style.main.spacing * 2
            height : textArea.height
            TextArea {
                id : textArea
                width : parent.width
                text : sendMessagePage.messageText
                onTextChanged : {
                    sendMessagePage.messageText = text
                    sendMessagePage.characterCount = text.length
                }
                readOnly : false
                wrapMode : TextEdit.WordWrap
                // only enable select by mouse on desktop
                selectByMouse : rWin.isDesktop
            }
        }

        Label {
            id : characterCount
            text : sendMessagePage.characterCount + " " + qsTr("characters")
        }
        Item {
            height : sendTweetButton.height
            width : parent.width
            Label {
                id : accountLabel
                anchors.left : parent.left
                anchors.leftMargin : rWin.c.style.main.spacing
                text : qsTr("Account")
            }
            AccountComboBox {
                id : accountCB
                anchors.left : accountLabel.right
                anchors.leftMargin : rWin.c.style.main.spacing
                width : parent.width / 3.0
                onSelectedAccountUsernameChanged : {
                    sendMessagePage.messageAccountUsername = selectedAccountUsername
                }
            }
            Button {
                anchors.right : parent.right
                anchors.rightMargin : rWin.c.style.main.spacing
                anchors.verticalCenter : accountLabel.verticalCenter
                id : sendTweetButton
                width : parent.width / 3.0
                text : sendMessagePage.sending ? qsTr("Sending...") : qsTr("Send Tweet")
                // TODO: deactivate the button instead of hiding it
                visible : sendMessagePage.readyToSend

                onClicked : {
                    if (sendMessagePage.sending) {
                        return
                    } else {
                        sendMessagePage.sending = true
                    }
                    rWin.python.call("tsubame.gui.messages.send_message",
                    [sendMessagePage.messageAccountUsername,
                     sendMessagePage.messageText,
                     []], function(success){
                        // show success/error notification
                        if (success) {
                            rWin.notify(qsTr("Tweet sent"))
                        } else {
                            rWin.notify(qsTr("Tweet sending failed"))
                        }
                        // go back
                        rWin.pop()
                    })
                }
            }
        }
    }
}

