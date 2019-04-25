//MediaGrid.qml
//
// Based on MediaGrid from Twablet by Lucien XU <sfietkonstantin@free.fr>


import QtQuick 2.0
import UC 1.0

Grid {
    id: mediaGrid
    property var mediaList : null
    visible: mediaList != null
    property real imageWidth: mediaGrid.width
    property real imageHeight: mediaGrid.width * 2 / 3
    property bool isSingle: mediaGrid.mediaList != null && mediaGrid.mediaList.length == 1
    function computeSizes() {
        switch (mediaGrid.mediaList.length) {
        case 0:
            break
        case 1:
            mediaGrid.columns = 1
            mediaGrid.rows = 1
            mediaGrid.imageWidth = mediaGrid.width
            mediaGrid.imageHeight = mediaGrid.width * 2 / 3
            break
        case 2:
            mediaGrid.columns = 2
            mediaGrid.rows = 1
            mediaGrid.imageWidth = (mediaGrid.width / 2) - (mediaGrid.spacing / 2)
            mediaGrid.imageHeight = mediaGrid.width / 2
            break
        case 3:
            mediaGrid.columns = 3
            mediaGrid.rows = 1
            mediaGrid.imageWidth = (mediaGrid.width / 3) - (mediaGrid.spacing / 3)
            mediaGrid.imageHeight = mediaGrid.width / 3
            break
        case 4:
            mediaGrid.columns = 2
            mediaGrid.rows = 2
            mediaGrid.imageWidth = (mediaGrid.width / 2) - (mediaGrid.spacing / 2)
            mediaGrid.imageHeight = (mediaGrid.width / 2) - (mediaGrid.spacing / 2)
            break
        default: // message >4 images, default to to columns and corresponding number of rows
            mediaGrid.columns = 2
            mediaGrid.rows = Math.ceil(mediaGrid.messageList.length / 2)
            mediaGrid.imageWidth = (mediaGrid.width / 2) - (mediaGrid.spacing / 2)
            mediaGrid.imageHeight = (mediaGrid.width / 2) - (mediaGrid.spacing / 2)
            break
        }
    }
    columns: 1
    rows: 1
    clip: true

    Component.onCompleted: if (mediaGrid.mediaList) {computeSizes()}
    onWidthChanged: if (mediaGrid.mediaList) {computeSizes()}

    Repeater {
        model: mediaGrid.mediaList
        // TODO: support for not-Twitter media attached to Tweets
        delegate: TwitterImage {
            property real ratio: modelData.sizes.small.h / modelData.sizes.small.w
            //property real mediaHeight: container.enabled ? mediaGrid.imageHeight : width * ratio
            property real mediaHeight: mediaGrid.imageHeight
            //property real mediaHeight: width * ratio
            width: mediaGrid.imageWidth
            height: mediaGrid.isSingle ? mediaHeight : mediaGrid.imageHeight
            // TODO: switch suffix based on requested image size
            //       - should be doable as we known what size corresponds to which suffix
            source: modelData.media_url_https + ":large"
            video: modelData.type == "video" || modelData.type == "animated_gif"

            onClicked : {
                rWin.log.debug("image clicked: " + index)
                if (video) {
                    rWin.log.debug("image is video thumbnail")
                    // lets just use the first variant, we can implement
                    // sorting by quality later
                    var videoUrl = modelData.video_info.variants[0].url
                    var mediaPage = rWin.loadPage("VideoPage", {
                        "videoUrl" : videoUrl,
                        "previewImageUrl" : modelData.media_url_https + ":large"
                    })
                    rWin.log.debug("VIDEO URL")
                    rWin.log.debug(videoUrl)
                } else {
                    var mediaPage = rWin.loadPage("ImageBrowserPage", {
                        "mediaList" : mediaGrid.mediaList,
                        "imageIndex" : index
                    })
                }
                rWin.pushPageInstance(mediaPage)
            }
        }
    }
}