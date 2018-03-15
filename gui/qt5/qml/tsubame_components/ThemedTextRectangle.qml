// ThemedBackgroundRectangle.qml
// A background rectangle that respects the modRana theme.
import UC 1.0

ThemedBackgroundRectangle {
    property alias label : innerLabel
    Label {
        id : innerLabel
        anchors.verticalCenter : parent.verticalCenter
        anchors.horizontalCenter : parent.horizontalCenter
        width : parent.width - rWin.c.style.main.spacing * 2
        wrapMode : Text.Wrap
        textFormat : Text.StyledText
    }
}