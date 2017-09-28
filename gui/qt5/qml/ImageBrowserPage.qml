// ImageBrowserPage.qml
//
// Based on ImageBrowser from Twablet by Lucien XU <sfietkonstantin@free.fr>

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id: imageBrowser
    headerText : "Image " + (imageIndex + 1) + "/" + view.count
    headerVisible : false
    headerMenu : TopMenu {
        id : customTopMenu
        MenuItem {
            text : qsTr("Download image")
            onClicked : {
                imageBrowser.downloadImage()
            }
        }
    }
    property var mediaList : []
    property alias imageIndex : view.currentIndex

    content :
    Item {
        id : menuAndListViewContainer
        anchors.left : parent.left
        anchors.right : parent.right
        anchors.bottom : parent.bottom
        ThemedListView {
            id: view
            property real imageWidth: Math.max(imageBrowser.width, imageBrowser.height)
            //anchors.fill : parent
            anchors.left : parent.left
            anchors.right : parent.right
            anchors.bottom : parent.bottom
            height : imageBrowser.height
            //height : imageBrowser.height
            model: imageBrowser.mediaList
            orientation: Qt.Horizontal
            highlightRangeMode: ListView.StrictlyEnforceRange
            cacheBuffer: 4 * view.imageWidth
            snapMode: ListView.SnapOneItem

            delegate: TwitterImage {
                id: image
                width : view.width
                height : view.height
                image.sourceSize.width: view.imageWidth
                image.sourceSize.height: view.imageWidth
                image.fillMode: Image.PreserveAspectFit
                source: modelData.media_url_https + ":large"
            }
        }
    }

    function downloadImage() {
        rWin.log.info("starting image download")
        var imageData = imageBrowser.mediaList[imageBrowser.imageIndex]
        var url = imageData.media_url_https + ":large"
        rWin.python.call("tsubame.gui.download.download_image", [url], function(download_success){
            if (download_success) {
                rWin.notify(qsTr("Image downloaded."), 2000)
            } else {
                rWin.notify(qsTr("Image download failed."), 3000)
            }
        })
    }
}

