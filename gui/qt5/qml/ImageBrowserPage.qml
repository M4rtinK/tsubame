// ImageBrowserPage.qml
//
// Based on ImageBrowser from Twablet by Lucien XU <sfietkonstantin@free.fr>

import QtQuick 2.0
import UC 1.0
import "tsubame_components"

BasePage {
    id: imageBrowser
    headerText : "Image " + (imageIndex + 1) + "/" + view.count
    property var mediaList : []
    property alias imageIndex : view.currentIndex

    topLevelContent : ThemedListView {
        id: view
        property real imageWidth: Math.max(view.width, view.height)
        //anchors.fill : parent
        anchors.left : parent.left
        anchors.right : parent.right
        anchors.bottom : parent.bottom
        height : (imageBrowser.headerVisible) ? imageBrowser.height - imageBrowser.headerHeight : imageBrowser.height
        //height : imageBrowser.height
        model: imageBrowser.mediaList
        orientation: Qt.Horizontal
        highlightRangeMode: ListView.StrictlyEnforceRange
        cacheBuffer: 4 * view.imageWidth
        snapMode: ListView.SnapOneItem

        delegate: TwitterImage {
            id: image
            //anchors.fill: parent
            width : view.width
            height : view.height
            image.sourceSize.width: view.imageWidth
            image.sourceSize.height: view.imageWidth
            image.fillMode: Image.PreserveAspectFit
            source: modelData.media_url_https + ":large"
            onClicked : {
                imageBrowser.headerVisible = !imageBrowser.headerVisible
                view.positionViewAtIndex(view.currentIndex, ListView.Contain)
            }
        }
    }
}

