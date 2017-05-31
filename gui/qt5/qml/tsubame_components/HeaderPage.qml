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
    property alias content : contentField.children
    property alias contentParent : contentField
    property alias headerContent : hContent.children
    property alias headerWidth : header.width
    property alias headerOpacity : header.opacity
    property alias backButtonWidth : backButton.width
    property int headerHeight : rWin.headerHeight
    property int bottomPadding : 0
    property real availableHeight : parent.height - bottomPadding - headerHeight
    property alias isFlickable :  pageFlickable.interactive
    // TODO: reenable scroll decorator
    /*
    ScrollDecorator {
         id: scrolldecorator
         flickableItem: pageFlickable
    }
    */

    /*
    Rectangle {
        id : background
        color : "white"
        anchors.fill : parent
        //visible : false
    }
    */

    Flickable {
        id : pageFlickable
        anchors.fill: parent
        contentWidth: parent.width
        contentHeight: (headerHeight + contentField.childrenRect.height + bottomPadding)
        //flickableDirection: Flickable.VerticalFlick
        VerticalScrollDecorator {}
        Item {
            id : contentField
            anchors.top : header.bottom
            //height : childrenRect.height
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
    MIconButton {
        id : backButton
        width : headerHeight * 0.8
        height : headerHeight * 0.8
        anchors.top : parent.top
        anchors.left : parent.left
        anchors.topMargin : rWin.c.style.main.spacing
        anchors.leftMargin : rWin.c.style.main.spacingBig
        iconName : "left_thin.png"
        //iconSource : "image://icons/"+ rWin.theme_id +"/back_small.png"
        opacity : pageFlickable.atYBeginning ? 1.0 : 0.55
        visible : rWin.showBackButton
        onClicked : {
            rWin.pageStack.pop(undefined, !rWin.animate)
        }

        onPressAndHold : {
            rWin.pageStack.pop(null, !rWin.animate)
        }
    }
}
