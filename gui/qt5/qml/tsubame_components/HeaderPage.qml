import QtQuick 2.0
import UC 1.0

/* base page, includes:
   * a header, with a
    * back button
    * page name
    * optional tools button
 useful for things like track logging menus,
 about menus, compass pages, point pages, etc.
*/

Page {
    id : headerPage
    property alias content : contentField.children
    property alias contentParent : contentField
    property alias headerContent : hContent.children
    property alias headerWidth : header.width
    property alias headerOpacity : header.opacity
    property alias headerVisible : header.visible
    property alias backButtonWidth : backButton.width
    property alias backButtonVisible : backButton.visible
    property alias topLevelContent : topLevel.children
    property int headerHeight : rWin.headerHeight
    property alias isFlickable :  pageFlickable.interactive

    // this property governs if the page should be destroyed
    // once it leaves the stack
    property bool destroyOnPop : true

    onIsOnPageStackChanged : {
        if (destroyOnPop && wasOnPageStack && !isOnPageStack) {
            // Pop-on-destroy is enabled, the page already was
            // on the stack before (and thus fully initialized
            // and visible) and has just left the stack.
            // This means the page can be safely garbage collected
            // and we need to do that as apparently neither the
            // QQC2 or Silica page stacks will not do it for us.
            headerPage.destroy()
        }
    }

    Rectangle {
        id : background
        color : rWin.theme.color.list_view_background
        anchors.fill : parent
    }

    PlatformFlickable {
        id : pageFlickable
        anchors.fill: parent
        contentWidth: parent.width
        VerticalScrollDecorator {}
        Item {
            id : contentField
            anchors.top : header.bottom
            anchors.bottom : parent.bottom
            anchors.left : parent.left
            anchors.right : parent.right
        }
        PageHeaderBackground {
            id : header
            Item {
                id : hContent
                width : rWin.platform.needs_back_button ?
                headerWidth - backButton.width - rWin.c.style.main.spacingBig :
                headerWidth
                anchors.right : parent.right
                anchors.top : parent.top
                height : headerHeight
            }
        }
    }
    // Top level content is above the flickable and the header,
    // but still bellow the back button (if any).

    Item {
        id : topLevel
        anchors.fill: parent
    }
    MIconButton {
        id : backButton
        width : headerHeight * 0.8
        height : headerHeight * 0.8
        anchors.top : parent.top
        anchors.left : parent.left
        anchors.topMargin : (headerHeight - height) / 2.0
        anchors.leftMargin : rWin.c.style.main.spacingBig
        iconName : "left_thin.png"
        opacity : pageFlickable.atYBeginning ? 1.0 : 0.55
        visible : rWin.showBackButton
        onClicked : {
            rWin.pageStack.pop(undefined, !rWin.animate)
        }
        onPressAndHold : {
            rWin.pageStack.pop(null, !rWin.animate)
        }
    }
    MouseArea {
        anchors.fill : parent
        acceptedButtons: Qt.BackButton
        onClicked: {
            rWin.pageStack.pop(undefined, !rWin.animate)
        }
        onPressAndHold : {
            rWin.pageStack.pop(null, !rWin.animate)
        }
    }
}
