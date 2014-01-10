import QtQuick 2.0

Rectangle {
    id: wrapper
    width: 1024
    height: 768

    focus: true

    property string currentBuffer: "";
    signal gotPunterIdentifier(string identifierType, string identifier);
    signal addedToCart(string ticketId);
    signal removedFromCart(int index);
    signal changedCurrentEvent(string eventId);
    signal saleCompleted();
    signal saleVoided();
    signal cardLinkPerformed(string cid);
    signal cardLinkCancelled();

    function doCardLink() {
        wrapper.state = 'shaded';
        cardLinkDialog.focusCidInput();
        cardLinkDialog.clearCidInput();
    }

    function unknownPunterQueried() {
        customerWrapperBlink.start();
    }

    function setCurrentEvent(newCE) {
        currentEvent = newCE;
    }

    Keys.onPressed: {
        if (event.key > 0x01000000) return; // ignore weird keys
        var keyChar = String.fromCharCode(event.key);
        if ((event.modifiers & Qt.ShiftModifier) === 0) {
            keyChar = keyChar.toLowerCase();
        } else {
            keyChar = keyChar.toUpperCase();
        }

        if (keyChar == "?") {
            currentBuffer = "";
        }
        if (keyChar == ";") {
            console.log("Read card data:", currentBuffer + keyChar);
            gotPunterIdentifier("swipecard", currentBuffer + keyChar);
            currentBuffer = "";
            event.accepted = true;
            return;
        }

        currentBuffer += keyChar;
        event.accepted = true;
    }
    Keys.onReturnPressed: {
        if (currentBuffer.length > 0)
            gotPunterIdentifier("unknown", currentBuffer);
        currentBuffer = "";
        event.accepted = true;
    }
    Keys.onEnterPressed: {
        if (currentBuffer.length > 0)
            gotPunterIdentifier("unknown", currentBuffer);
        currentBuffer = "";
        event.accepted = true;
    }
    Keys.onEscapePressed: {
        currentBuffer = "";
        event.accepted = true;
    }

    property string currentEvent: "none";

    function formatCost(price, dontShowFree) {
        if (!dontShowFree && price === 0) return "Free!";
        return "£" + (price/100).toFixed(2);
    }
    function totalCost(model) {
        return model.totalPrice();
        var c = 0;
        for (var i = 0; i < model.count; i++) {
            c += model.get(i).salePrice;
        }
        return c;
    }

    Rectangle {
        id: headerWrapper
        height: 60
        color: "#052443"
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0

        Image {
            id: headerLogo
            width: 266
            height: 58
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 1
            sourceSize.height: 57
            sourceSize.width: 266
            source: "logocrop.png"
        }

        Text {
            id: headerText
            x: 303
            y: 8
            color: "#ffffff"
            text: qsTr("Point of Sale")
            anchors.left: parent.left
            anchors.leftMargin: 303
            anchors.top: parent.top
            anchors.topMargin: 8
            font.pixelSize: 32
        }
    }

    Rectangle {
        id: cartWrapper
        x: 500
        y: 60
        width: 300
        height: 472
        color: "#cccccc"
        anchors.top: parent.top
        anchors.topMargin: 60
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 60
        anchors.right: parent.right
        anchors.rightMargin: 0

        Button {
            id: voidButton
            text: "Void"
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            anchors.leftMargin: 10
            onClicked: {
                saleVoided();
                cartLabel.refresh();
            }
        }
        Button {
            id: saleButton
            text: "Confirm"
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            anchors.rightMargin: 10
            onClicked: {
                saleCompleted();
                cartLabel.refresh();
            }
            widthPadding: 100
        }

        Text {
            id: cartLabel
            text: "Cart (<i>" + formatCost(totalCost(cartView.model), true) + "</i>)"
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.top: parent.top
            anchors.topMargin: 6
            font.pixelSize: 22

            function refresh() {
                cartLabel.text = "Cart (<i>" + formatCost(totalCost(cartView.model), true) + "</i>)";
            }
        }

        ListView {
            id: cartView
            anchors.rightMargin: 10
            anchors.leftMargin: 10
            x: 5
            anchors.bottomMargin: 50
            anchors.topMargin: 50
            anchors.fill: parent
            model: cartModel
            delegate: Item {
                x: 5
                height: 40
                Row {
                    id: row1
                    spacing: 10

                    Rectangle {
                        width: cartView.width
                        height: 40
                        color: "#00000000"

                        Text {
                            text: name + " (<i>" + formatCost(salePrice) + "</i>)"
                            id: nameTag
                        }
                        Text {
                            id: eventNameTag
                            text: eventName
                            anchors.top: nameTag.bottom
                            font.pixelSize: 12
                        }

                        Rectangle {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            y: 0
                            height: 20
                            width: 20
                            color: "red"

                            Text {
                                anchors.fill: parent
                                text: "x"
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    removedFromCart(index);
                                    cartLabel.refresh();
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: footerWrapper
        x: 0
        y: 540
        height: 60
        color: "#052443"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        anchors.right: parent.right

        Rectangle {
            id: customerWrapperWrapper
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            width: customerWrapper.width + (customerWrapper.anchors.leftMargin * 2)
            color: "#00000000"

            SequentialAnimation {
                id: customerWrapperBlink
                running: false
                loops: 3
                NumberAnimation { target: customerWrapperWrapper; property: "opacity"; to: 0; duration: 200; }
                NumberAnimation { target: customerWrapperWrapper; property: "opacity"; to: 1.0; duration: 200; }
            }

            MouseArea {
                id: customerMouseArea
                anchors.fill: parent
                onClicked: {
                    // TODO
                }
            }

            Rectangle {
                id: customerWrapper
                x: 13
                y: 16
                width: customerLabel.width + customerText.width + 10
                height: customerLabel.height
                color: "#00000000"
                anchors.top: parent.top
                anchors.topMargin: 16
                anchors.left: parent.left
                anchors.leftMargin: 13

                Text {
                    color: "#ffffff"
                    id: customerLabel
                    text: qsTr("Customer:")
                    font.bold: true
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    font.pixelSize: 20
                }

                Text {
                    color: "#ffffff"
                    id: customerText
                    x: 0
                    text: punterName
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    font.pixelSize: 20
                }
            }
        }

        Text {
            id: cidEntryText
            x: 472
            y: 22
            color: "#ffffff"
            text: currentBuffer
            font.family: "Courier 10 Pitch"
            anchors.right: parent.right
            anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignRight
            font.pixelSize: 20
        }
    }

    Rectangle {
        id: ticketSelectionWrapper
        color: "#ffffff"
        anchors.right: parent.right
        anchors.rightMargin: 300
        anchors.left: parent.left
        anchors.leftMargin: 200
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 60
        anchors.top: parent.top
        anchors.topMargin: 60

        Text {
            id: availableTicketsLabel
            x: 504
            y: 6
            text: qsTr("Available Tickets")
            anchors.topMargin: 6
            anchors.top: parent.top
            anchors.left: parent.left
            font.pixelSize: 22
            anchors.leftMargin: 10
        }

        GridView {
            id: ticketSelectionView
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 50
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.top: parent.top
            anchors.topMargin: 50
            model: ticketSelectionModel
            cellWidth: (parent.width / 2) - 20
            cellHeight: (parent.height / 2) - 80
            delegate: Item {
                id: ticketDelegate
                x: 5
                TicketButton {
                    id: ticketButton
                    text: name + "<br><i>" + formatCost(salePrice) + "</i>"
                    height: ticketSelectionView.cellHeight
                    width: ticketSelectionView.cellWidth
                    backgroundColor: bgColor
                    opacity: applicable
                    onClicked: {
                        if (!parent.opacity) return;
                        addedToCart(ticketId);
                        cartLabel.refresh();
                    }
                }
            }
        }
    }

    Rectangle {
        id: eventsWrapper
        y: 61
        width: 200
        height: 472
        color: "#cccccc"
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottomMargin: 60
        anchors.topMargin: 60
        anchors.bottom: parent.bottom
        anchors.top: parent.top
        Text {
            id: eventsLabel
            text: qsTr("Events")
            anchors.topMargin: 6
            anchors.top: parent.top
            anchors.left: parent.left
            font.pixelSize: 22
            anchors.leftMargin: 10
        }

        ListView {
            id: eventsView
            interactive: false
            anchors.topMargin: 50
            anchors.bottomMargin: 50
            anchors.fill: parent
            model: eventsModel
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            highlight: Rectangle {
                color: "black"; radius: 5
            }

            delegate: Item {
                x: 5
                height: 80
                Row {
                    id: row2
                    spacing: 10

                    Rectangle {
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                changedCurrentEvent(eventId);
                                currentEvent = eventId;
                            }
                        }

                        width: 160
                        height: 70
                        color: (currentEvent == eventId) ? "white" : "#00000000"
                        border.width: 5
                        border.color: "black"
                        radius: 5

                        Text {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.leftMargin: 7
                            anchors.rightMargin: 7
                            anchors.verticalCenter: parent.verticalCenter
                            horizontalAlignment: Text.AlignHCenter
                            id: itemText
                            text: name
                            wrapMode: Text.WordWrap
                            width: parent.width
                            font.italic: currentEvent == eventId
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: shadeRectangle
        x: 0
        y: 0
        anchors.fill: parent
        color: "#ffffff"
        anchors.topMargin: 60
        opacity: 0
    }
    states: [
        State {
            name: "shaded"

            PropertyChanges {
                target: shadeRectangle
                opacity: 0.7
            }
            PropertyChanges {
                target: cardLinkDialog
                opacity: 1
            }
        }
    ]

    transitions: [
        Transition {
            from: "*"; to: "*"
            NumberAnimation {
                properties: "opacity"
                duration: 200
            }
        }
    ]

    CardLinkDialog {
        id: cardLinkDialog
        x: 0
        y: 0
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        opacity: 0
        onLinkClicked: {
            wrapper.state = '';
            wrapper.focus = true;
            cardLinkPerformed(cid)
        }
        onCancelClicked: {
            wrapper.state = '';
            wrapper.focus = true;
            cardLinkCancelled()
        }
    }
}
