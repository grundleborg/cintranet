import QtQuick 2.0

Rectangle {
    id: borderRect
    width: 400
    height: 190

    color: "#cccccc"
    border.width: 5
    border.color: "#333333"
    radius: 10

    signal closeClicked();
    signal backClicked();

    Text {
        id: titleLabel
        text: qsTr("Ticket Details")
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 20
    }

    Text {
        id: ticketNumberInput
        height: 20
        text: qsTr("")
        anchors.top: parent.top
        anchors.topMargin: 69
        anchors.left: parent.left
        anchors.leftMargin: 145
        anchors.right: parent.right
        anchors.rightMargin: 20
        font.pixelSize: 16
        font.bold: false
    }

    Text {
        id: ticketNumberLabel
        text: qsTr("Ticket Number:")
        anchors.top: parent.top
        anchors.topMargin: 67
        anchors.left: parent.left
        anchors.leftMargin: 20
        font.bold: true
        font.pixelSize: 16
    }

    Button {
        id: backButton
        x: 469
        y: 176
        text: "Back"
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        widthPadding: 40
        heightPadding: 20
        onClicked: {
            backClicked()
        }
    }

    Button {
        id: closeButton
        x: 469
        y: 176
        text: "Close"
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        widthPadding: 40
        heightPadding: 20
        onClicked: {
            closeClicked()
        }
    }
}