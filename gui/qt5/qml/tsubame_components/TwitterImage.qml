// TwitterImage.qml
//
// Based on TwitterImage from Twablet by Lucien XU <sfietkonstantin@free.fr>

import QtQuick 2.0
import UC 1.0

MouseArea {
    id: container
    property alias source: image.source
    property alias image: image
    property alias progress: image.progress
    property alias status: image.status

    BackgroundRectangle {
        id: background
        anchors.fill: parent
        opacity: 0.5
        propagateComposedEvents : true
        onClicked : mouse.accepted = false

        Behavior on opacity {
            FadeAnimator {}
        }
    }

    Label {
        id: loadingProgressLabel
        anchors.horizontalCenter : parent.horizontalCenter
        anchors.verticalCenter : parent.verticalCenter
        text : image.status == Image.Error ? qsTr("<b>Image loading failed.</b>") : "<b>" + Math.round(image.progress * 100) + " %</b>"
        visible : image.status == Image.Loading || image.status == Image.Error
    }

    Image {
        id: image
        anchors.fill: parent
        smooth: true
        asynchronous: true
        cache: true
        fillMode: Image.PreserveAspectCrop
        clip: true
        opacity: 0
        sourceSize.width: width
        sourceSize.height: height

        states: State {
            name: "visible"; when: image.status === Image.Ready
            PropertyChanges {
                target: image
                opacity: 1
            }
            PropertyChanges {
                target: background
                opacity: 0
            }
        }

        Behavior on opacity {
            FadeAnimator {}
        }
    }

    /*
    TODO: make use of this (GitHub issue #39)
    Image {
        anchors.centerIn: parent
        width: Theme.iconSizeSmall
        height: Theme.iconSizeSmall
        source: "image://theme/icon-s-high-importance?" + Theme.highlightColor
        visible: image.status === Image.Error
    }*/
}