import QtQuick 2.0

Canvas {
    id: canvas
    antialiasing: true
    // move the origin to the bubble arrow
    transformOrigin: Item.Bottom

    property real bubbleWidth : 200
    property real bubbleHeight : 100
    property real bubbleOffset : 30

    width: bubbleWidth
    height: bubbleHeight + bubbleOffset

    property int radius: 10
    property color bubbleColor: Qt.darker("grey", 1.4)

    onRadiusChanged:requestPaint()

    // Sailfish OS destroys the Canvas rendering context
    // when the application is minimised, so wee need
    // to re-render the canvas once the context is again
    // available
    onContextChanged: {
         if (canvas.context) {
            canvas.requestPaint()
         } else {
            return
         }
    }

    onPaint: {
        var ctx = getContext("2d")
        ctx.save()
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.bubbleColor = canvas.fillStyle
        ctx.globalAlpha = 0.6
        ctx.beginPath()
        ctx.moveTo(radius, 0)  // top side
        ctx.lineTo(bubbleWidth-radius, 0)
        // draw top right corner
        ctx.arcTo(bubbleWidth, 0, bubbleWidth, radius, radius);
        ctx.lineTo(bubbleWidth, bubbleHeight-radius)  // right side
        // draw bottom right corner
        ctx.arcTo(bubbleWidth, bubbleHeight, bubbleWidth-radius, bubbleHeight, radius);
        ctx.lineTo((bubbleWidth/2.0)+(bubbleOffset/2.75), bubbleHeight)  // bottom side right
        // bubble triangle/arrow/pointer
        ctx.lineTo(bubbleWidth/2.0, bubbleHeight+bubbleOffset)  // bottom side right
        ctx.lineTo((bubbleWidth/2.0)-(bubbleOffset/2.75), bubbleHeight)  // bottom side right
        ctx.lineTo(radius, bubbleHeight)  // bottom side left
        // draw bottom left corner
        ctx.arcTo(0, bubbleHeight, 0, bubbleHeight-radius, radius)
        ctx.lineTo(0, radius)  // left side
        // draw top left corner
        ctx.arcTo(0, 0, radius, 0, radius)
        ctx.closePath()
        ctx.fill()
        ctx.restore()
    }
}