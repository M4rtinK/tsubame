// VideoPage.qml
//
// Video playback page.

import QtQuick 2.0
import QtMultimedia 5.6
import UC 1.0
import "tsubame_components"

BasePage {
    id: videoPage
    headerVisible : false
    headerMenu : TopMenu {
        id : customTopMenu
        MenuItem {
            text : qsTr("Download video")
            onClicked : {
                videoPage.downloadVideo()
            }
        }
    }
    property string videoUrl : ""

    content : Item {
        height : videoPage.height
        anchors.right : parent.right
        anchors.left : parent.left
        anchors.bottom : parent.bottom
        MediaPlayer {
            id : mediaPlayer
            source : videoPage.videoUrl
            audioRole : MediaPlayer.VideoRole
            // TODO: start playing only once play is pressed
            autoLoad : true
            autoPlay : true
            // sound off by default
            muted : true
        }
        VideoOutput {
            id : videoOutput
            source : mediaPlayer
            anchors.fill : parent
        }
        ThemedBackgroundRectangle {
            id: playRectangle
            width : 48 * rWin.c.style.m
            height : 48 * rWin.c.style.m
            cornerRadius : width * 0.5 // lets make this into a circle
            borderWidth : 4 * rWin.c.style.m
            anchors.right : parent.right
            anchors.rightMargin : 16 * rWin.c.style.m
            anchors.bottom : parent.bottom
            anchors.bottomMargin : 16 * rWin.c.style.m
            Label {
                id: muteEmoji
                text: mediaPlayer.muted ? "🔇️" : "🔈"
                anchors.horizontalCenter : parent.horizontalCenter
                anchors.verticalCenter : parent.verticalCenter
            }
            onClicked : {
                // redirect clicks to the main mouse area
                mediaPlayer.muted = !mediaPlayer.muted
            }
        }

    }
    function downloadVideo() {
        rWin.log.debug("not implemented yet!")
        /*
        rWin.log.info("starting video download")
        var imageData = imageBrowser.mediaList[imageBrowser.imageIndex]
        var url = imageData.media_url_https + ":large"
        rWin.python.call("tsubame.gui.download.download_image", [url], function(download_success){
            if (download_success) {
                rWin.notify(qsTr("Image downloaded."), 2000)
            } else {
                rWin.notify(qsTr("Image download failed."), 3000)
            }
        })*/
    }
}

