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
    // Twitter media ids go there & need to be integers
    ListModel {
        id : imagesModel
    }

    property int _job_id : 0
    function getJobId() {
        _job_id++
        return _job_id
    }

    property int maxImages : 4
    property int maxVideos : 1

    property string videoMediaID : ""
    property string videoURL : ""
    property int videoJobId : -1
    property string videoStatusText : ""
    // once we add an image we can't add a video and vice versa
    property bool canAddImage : messageAccountUsername &&
                                videoURL == "" &&
                                imagesModel.count < 4
    property bool canAddVideo : messageAccountUsername &&
                                imagesModel.count == 0 &&
                                !videoURL

    property bool readyToSend : messageText && messageAccountUsername
    property bool sending : false

    PlatformImagePicker {
        id : imagePicker
        selectMultiple : true
        property bool armed: false
        onSelectedFilesChanged : {
            // looks like we sometimes get some false alerts here,
            // so add arming & check for results length
            if (!armed) {
                return
            }
            if (selectedFiles.length) {
                imageChosen(selectedFiles)
            }
        }
    }

    PlatformVideoPicker {
        id : videoPicker
        selectMultiple : false
        property bool armed: false
        onSelectedFilesChanged : {
            // looks like we sometimes get some false alerts here,
            // so add arming & check for results length
            if (!armed) {
                return
            }
            if (selectedFiles.length) {
                videoChosen(selectedFiles)
            }
        }
    }

    function chooseImage() {
        // choose an image
        videoPicker.armed = false
        imagePicker.armed = true
        imagePicker.run()
    }

    function imageChosen(imageURLs) {
        // add the images to our model,
        // while making sure they fit
        var slots = maxImages - imagesModel.count
        var iterations = Math.min(slots, imageURLs.length)
        for (var i=0; i<iterations; i++) {
            var imageURL = imageURLs[i]
            var jobId = getJobId()
            imagesModel.append({"imageURL" : imageURL, "mediaID" : "", "jobId" : jobId, "statusText" : qsTr("Waiting")})
            uploadMedia(imageURL, "TWEET_IMAGE", jobId)
        }
    }

    function chooseVideo() {
        // choose a video
        imagePicker.armed = false
        videoPicker.armed = true
        videoPicker.run()
    }

    function videoChosen(videoURLs) {
        var URL = videoURLs[0]
        var jobId = getJobId()
        videoURL = URL
        videoStatusText = qsTr("Uploading...")
        videoJobId = jobId
        uploadMedia(URL, "TWEET_VIDEO", jobId)
    }

    function uploadMedia(imageURL, mediaCategory, jobIndex) {
        // upload one media item and return resulting media id
        rWin.python.call("tsubame.gui.upload.upload_media_async",
                         [messageAccountUsername, imageURL, mediaCategory, jobIndex])
    }

    Component.onCompleted : {
        // connect to upload status handler
        rWin.python.setHandler("mediaUploadStatus", function(uploadStatus) {
            // first match the job to a known image or video upload
            var jobId = uploadStatus[0]
            var messageType = uploadStatus[1]
            // check video first
            if (jobId == videoJobId) {
                // handle video
                if (messageType == "SUCCESS") {
                    videoMediaID = uploadStatus[2]
                } else if (messageType == "PROGRESS") {
                    videoStatusText = Math.round(uploadStatus[2] * 100) + " %"
                } else if (messageType == "FINALIZING") {
                    videoStatusText = qsTr("Finalizing")
                } else if (messageType == "ERROR") {
                    videoStatusText = qsTr("Upload failed")
                    if (uploadStatus[2]) {
                            rWin.notify(qsTr("Upload failed:") + " " + uploadStatus[2])
                    }
                }
            } else {
                // we need to check the image list view
                for (var i=0; i<imagesModel.count; i++) {
                    if (jobId == imagesModel.get(i).jobId) {
                        if (messageType == "SUCCESS") {
                            imagesModel.setProperty(i, "mediaID", uploadStatus[2])
                        } else if (messageType == "UPLOADING") {
                           imagesModel.setProperty(i, "statusText", qsTr("Uploading..."))
                        } else if (messageType == "PROGRESS") {
                            imagesModel.setProperty(i, "statusText", Math.round(uploadStatus[2] * 100) + " %")
                        } else if (messageType == "FINALIZING") {
                           imagesModel.setProperty(i, "statusText", qsTr("Finalizing"))
                        } else if (messageType == "ERROR") {
                            imagesModel.setProperty(i, "statusText", qsTr("Upload failed"))
                            if (uploadStatus[2]) {
                                    rWin.notify(qsTr("Upload failed:") + " " + uploadStatus[2])
                            }
                        }
                        break
                    }
                }

            }
        })
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
                text : qsTr("Add images")
                visible : sendMessagePage.canAddImage
                onClicked : {
                    chooseImage()
                }
            }
            Button {
                text : qsTr("Add video")
                visible : sendMessagePage.canAddVideo
                onClicked : {
                    chooseVideo()
                }
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
                text : mediaID ? qsTr("Remove") : statusText
                source : imageURL
                onClicked : {
                    imagesModel.remove(index)
                }
            }
        }
        VideoButton {
            id : videoButton
            anchors.horizontalCenter : parent.horizontalCenter
            text : videoMediaID ? qsTr("Remove") : sendMessagePage.videoStatusText
            visible : sendMessagePage.videoURL
            iconSize: parent.width / 4
            source : videoURL
            property real uploadProgress : 0
            loops : 20
            onClicked : {
                sendMessagePage.videoMediaID = ""
                sendMessagePage.videoJobId = ""
                sendMessagePage.videoURL = ""
            }
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
                    if (imagesModel.count) {
                        for (var i=0; i<imagesModel.count; i++) {
                            var mediaID = imagesModel.get(i).mediaID
                            if (mediaID) {
                                mediaIDs.push(imagesModel.get(i).mediaID)
                            }
                        }
                    } else if (videoMediaID) {
                        mediaIDs.push(videoMediaID)
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

