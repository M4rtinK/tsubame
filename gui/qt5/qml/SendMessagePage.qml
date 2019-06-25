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

    // message text & length
    property string messageText : ""
    property int characterCount : 0
    property string messageAccountUsername : ""
    // is some media being uploaded ?
    property int mediaUploadInProgress : 0
    // Twitter media ids go there & need to be integers
    ListModel {
        id : imagesModel
    }
    property int maxImages : 4
    property int maxVideos : 1

    property int video : 0
    property string videoURL : ""
    // once we add an image we can't add a video and vice versa
    property bool canAddImage : messageAccountUsername &&
                                !mediaUploadInProgress &&
                                videoURL == "" &&
                                imagesModel.count < 4
    property bool canAddVideo : messageAccountUsername &&
                                !mediaUploadInProgress &&
                                imagesModel.count == 0

    property bool readyToSend : messageText && messageAccountUsername && !mediaUploadInProgress
    property bool sending : false

    PlatformImagePicker {
        id : imagePicker
        selectMultiple : true
        onSelectedFilesChanged : {
            imageChosen(selectedFiles)
        }
    }

    function chooseImage() {
        // choose an image
        imagePicker.run()
    }

    function imageChosen(imageURLs) {
        // add the images to our model,
        // while making sure they fit
        var slots = maxImages - imagesModel.count
        var iterations = Math.min(slots, imageURLs.length)
        for (var i=0; i<iterations; i++) {
            var imageURL = imageURLs[i]
            imagesModel.append({"imageURL" : imageURL, "mediaID" : ""})
            mediaUploadInProgress++
            uploadImage(imageURL, imagesModel.count-1, function(results){
                mediaUploadInProgress--
                var jobIndex = results[0]
                var mediaID = results[1]
                imagesModel.setProperty(jobIndex, "mediaID", mediaID)
            })
        }
    }

    function uploadImage(imageURL, jobIndex, callback) {
        rWin.python.call("tsubame.gui.upload.upload_media", [messageAccountUsername, imageURL, jobIndex], callback)
    }

    function chooseVideo() {
        // choose a video
    }

    function uploadVideo(videoURL) {

    }

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
        Row {
            spacing : rWin.c.style.main.spacing
            visible : sendMessagePage.canAddImage || sendMessagePage.canAddVideo
            Button {
                text : qsTr("Add image")
                visible : sendMessagePage.canAddImage
                onClicked : {
                    chooseImage()
                }
            }
            Button {
                text : qsTr("Add video")
                visible : sendMessagePage.canAddVideo
            }
        }
        GridView {
            id : imagesGW
            //property int columns : rWin.inPortrait ? 2 : 4
            property int columns : 4
            property real iconSize: parent.width / columns
            cellWidth : iconSize
            cellHeight : iconSize
            width : parent.width
            //height : rWin.inPortrait ? iconSize * 2 : iconSize
            height : iconSize
            visible : imagesModel.count != 0
            model : imagesModel
            delegate : ImageButton {
                id : imageButton1
                iconSize : imagesGW.iconSize - rWin.c.style.main.spacing
                text : mediaID ? qsTr("Remove") : qsTr("Uploading")
                source : imageURL
                onClicked : {
                    imagesModel.remove(index)
                }
            }
        }
        ImageButton {
            text : sendMessagePage.video ? qsTr("Video uploaded") : qsTr("Uploading")
            //visible : sendMessagePage.videoURL
            visible : false
        }

        Item {
            height : sendTweetButton.height
            width : parent.width
            AccountComboBox {
                id : accountCB
                label : qsTr("Account")
                anchors.leftMargin : rWin.c.style.main.spacing
                width : parent.width / 2.0
                onSelectedAccountUsernameChanged : {
                    sendMessagePage.messageAccountUsername = selectedAccountUsername
                }
            }
            Button {
                anchors.right : parent.right
                anchors.rightMargin : rWin.c.style.main.spacing
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
                    // gather all media ids
                    var mediaIDs = []
                    for (var i=0; i<imagesModel.count; i++) {
                        var mediaID = imagesModel.get(i).mediaID
                        if (mediaID) {
                            mediaIDs.push(imagesModel.get(i).mediaID)
                        }
                    }
                    rWin.python.call("tsubame.gui.messages.send_message",
                    [sendMessagePage.messageAccountUsername,
                     sendMessagePage.messageText,
                     mediaIDs], function(success){
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

