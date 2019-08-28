import sys, csv
from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem

# Load the UI file
UIClass, QtBaseClass = uic.loadUiType("InvScreen.ui")

# Class to handle the GUI of the program
class InvGUI(UIClass, QtBaseClass):
    # default class variables
    filePath = ""
    row = -1

    # Constructs the GUI
    def __init__(self):
        UIClass.__init__(self)
        QtBaseClass.__init__(self)
        self.setupUi(self)
        self.setWindowTitle('Inventory Management Program')  # set the title of the program window
        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)  # disable windows maximize button
        self.setFixedSize(836, 566)  # fixed windows size to avoid ugly resizing

        # Show open file page and let the user open csv file and proceed to next page
        self.stackedWidget.setCurrentIndex(0)
        self.openFileButton.clicked.connect(self.OpenFile)

        # Connect cellClicked event to a function displaying its related values
        self.tableWidget.cellClicked.connect(self.ClickedCell)

        # Connect search button to search item name in QTableWidget
        self.searchButton.clicked.connect(self.Search)
        self.searchObj.returnPressed.connect(self.Search)

        # Connect save button to save new quantity of the item
        self.changeItemButton.clicked.connect(self.ChangeInfo)

        # Connect add item button to function that adds new item and saves it
        self.addItemButton.clicked.connect(self.AddNewItem)

        # Connect delete item button to function that deletes selected row
        self.deleteItemButton.clicked.connect(self.DeleteItem)

    # Opens a single .csv file
    def OpenFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        InvGUI.filePath = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV(*.csv)', options=options)

        # If file is opened successfully, parse the data into the QTableView
        if InvGUI.filePath[0] != '':
            try:
                # parse the csv file
                with open(InvGUI.filePath[0], newline='') as csvFile:
                    self.tableWidget.setRowCount(0)
                    self.tableWidget.setColumnCount(5)
                    file = csv.reader(csvFile, delimiter=',', quotechar='|')

                    for rowData in file:
                        row = self.tableWidget.rowCount()
                        self.tableWidget.insertRow(row)

                        for column, colData in enumerate(rowData):
                            item = QTableWidgetItem(colData)
                            self.tableWidget.setItem(row, column, item)

                # Move to next page
                self.stackedWidget.setCurrentIndex(1)

            except:
                # If file is not loaded, display message
                warningMsg = QMessageBox()
                warningMsg.setIcon(QMessageBox.Warning)
                warningMsg.setWindowTitle('ERROR')
                warningMsg.setText('파일을 불러오지 못하였습니다.')
                warningMsg.exec_()

    # Displays data of the clicked row
    def ClickedCell(self, row, col):
        InvGUI.row = row
        self.itemCode.setText(self.tableWidget.item(InvGUI.row, 0).text())
        self.itemName.setText(self.tableWidget.item(InvGUI.row, 1).text())
        self.price1.setText(self.tableWidget.item(InvGUI.row, 2).text())
        self.price2.setText(self.tableWidget.item(InvGUI.row, 3).text())
        self.price3.setText(self.tableWidget.item(InvGUI.row, 4).text())

        print("Row selected: ", InvGUI.row + 1)
        print("Column selected: ", col + 1)

    # Search and display corresponding content
    def Search(self):
        toSearch = self.searchObj.text()
        print("Searching: ", toSearch)

        # Searching for the item, with case insensitive format
        # NOTE: instead of searching specific row, it searches the whole table widget
        items = self.tableWidget.findItems(toSearch, QtCore.Qt.MatchFixedString)
        if items:
            for item in items:
                InvGUI.row = item.row()

                # When found, display the results
                self.itemCode.setText(self.tableWidget.item(InvGUI.row, 0).text())
                self.itemName.setText(self.tableWidget.item(InvGUI.row, 1).text())
                self.price1.setText(self.tableWidget.item(InvGUI.row, 2).text())
                self.price2.setText(self.tableWidget.item(InvGUI.row, 3).text())
                self.price3.setText(self.tableWidget.item(InvGUI.row, 4).text())
                self.tableWidget.selectRow(InvGUI.row)  # highlight corresponding row
                print("Row selected: ", InvGUI.row + 1)

        else:
            # When not found, display error message
            results = '존재하지 않는 항목입니다.'
            QMessageBox.information(self, 'Search Results', results)

    # Changes the information of the item selected
    def ChangeInfo(self):
        # Prompt user with confirmation box before saving
        confirmSave = QMessageBox.question(self, 'Confirmation', "변경 사항을 저장 하시겠습니다?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # If user clicks yes, apply changes and save file
        if confirmSave == QMessageBox.Yes:
            # Make sure a row is selected before proceeding
            if InvGUI.row == -1:
                warningMsg = QMessageBox()
                warningMsg.setIcon(QMessageBox.Warning)
                warningMsg.setWindowTitle('ERROR')
                warningMsg.setText('수정 할 항목을 선택해 주세요.')
                warningMsg.exec_()

            else:
                # Change table widget content with user inputs
                if self.changeID.text() != "":
                    self.tableWidget.setItem(InvGUI.row, 0, QTableWidgetItem(self.changeID.text()))

                if self.changePrice1.text() != "":
                    self.tableWidget.setItem(InvGUI.row, 2, QTableWidgetItem(self.changePrice1.text()))

                if self.changePrice2.text() != "":
                    self.tableWidget.setItem(InvGUI.row, 3, QTableWidgetItem(self.changePrice2.text()))

                if self.changePrice3.text() != "":
                    self.tableWidget.setItem(InvGUI.row, 4, QTableWidgetItem(self.changePrice3.text()))

                # Call function to save file of what table widget has now
                InvGUI.SaveFile(self)

                # Display changes to the corresponding GUI elements
                self.itemCode.setText(self.tableWidget.item(InvGUI.row, 0).text())
                self.price1.setText(self.tableWidget.item(InvGUI.row, 2).text())
                self.price2.setText(self.tableWidget.item(InvGUI.row, 3).text())
                self.price3.setText(self.tableWidget.item(InvGUI.row, 4).text())

    # Add new row with given item name with its information and save its changes to the file
    def AddNewItem(self):
        # Prompt user with confirmation box before adding
        confirmAdd = QMessageBox.question(self, 'Confirmation', "추가 하시겠습니다?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # If user clicks yes, add new item and save file
        if confirmAdd == QMessageBox.Yes:

            # Make sure item name is not empty string
            if self.newItemName.text() == "" or self.newItemCode.text() == "":
                warningMsg = QMessageBox()
                warningMsg.setIcon(QMessageBox.Warning)
                warningMsg.setWindowTitle('ERROR')
                warningMsg.setText('품목에 대한 모든 정보를 입력해 주세요.')
                warningMsg.exec_()

            else:
                # Adding new row with user inputs
                InvGUI.row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(InvGUI.row)
                self.tableWidget.setItem(InvGUI.row, 0, QTableWidgetItem(self.newItemCode.text()))
                self.tableWidget.setItem(InvGUI.row, 1, QTableWidgetItem(self.newItemName.text()))
                self.tableWidget.setItem(InvGUI.row, 2, QTableWidgetItem(self.newPrice1.text()))
                self.tableWidget.setItem(InvGUI.row, 3, QTableWidgetItem(self.newPrice2.text()))
                self.tableWidget.setItem(InvGUI.row, 4, QTableWidgetItem(self.newPrice3.text()))

                # Call function to save file of what table widget has now
                InvGUI.SaveFile(self)

                # Display changes to the corresponding GUI elements
                self.itemCode.setText(self.tableWidget.item(InvGUI.row, 0).text())
                self.itemName.setText(self.tableWidget.item(InvGUI.row, 1).text())
                self.price1.setText(self.tableWidget.item(InvGUI.row, 2).text())
                self.price2.setText(self.tableWidget.item(InvGUI.row, 3).text())
                self.price3.setText(self.tableWidget.item(InvGUI.row, 4).text())
                self.tableWidget.selectRow(InvGUI.row)  # highlight corresponding row

    # Delete selected row and save its changes to the file
    def DeleteItem(self):
        # Prompt user with confirmation box before deleting
        confirmDelete = QMessageBox.question(self, 'Confirmation', "선택 항목을 완전히 삭제 하시겠습니다?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # If user clicks yes, delete selected row and save file
        if confirmDelete == QMessageBox.Yes:
            # Make sure a row is selected before proceeding
            if InvGUI.row == -1:
                warningMsg = QMessageBox()
                warningMsg.setIcon(QMessageBox.Warning)
                warningMsg.setWindowTitle('ERROR')
                warningMsg.setText('삭제 할 항목을 선택해 주세요.')
                warningMsg.exec_()

            else:
                self.tableWidget.removeRow(InvGUI.row)  # delete row from table widget

                # Call function to save file of what table widget has now
                InvGUI.SaveFile(self)

                # Set row to -1
                InvGUI.row = -1

                # Display changes to the corresponding GUI elements
                self.itemCode.setText("-")
                self.itemName.setText("-")
                self.price1.setText("-")
                self.price2.setText("-")
                self.price3.setText("-")

    # Save function that saves to the opened csv file of what current table widget contains
    def SaveFile(self):
        try:
            # Save to the same csv file by opening it again
            with open(InvGUI.filePath[0], newline='', mode='w') as csvFile:
                writer = csv.writer(csvFile)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)

                # Reset all user enter field
                self.newItemCode.setText("")
                self.newItemName.setText("")
                self.newPrice1.setText("")
                self.newPrice2.setText("")
                self.newPrice3.setText("")
                self.changeID.setText("")
                self.changePrice1.setText("")
                self.changePrice2.setText("")
                self.changePrice3.setText("")

                # Inform user data was successfully saved
                confirmMsg = QMessageBox()
                confirmMsg.setIcon(QMessageBox.Information)
                confirmMsg.setWindowTitle('Confirmation')
                confirmMsg.setText("저장 되었습니다!")
                confirmMsg.exec_()

        except:
            # If file is not loaded, display message
            warningMsg = QMessageBox()
            warningMsg.setIcon(QMessageBox.Warning)
            warningMsg.setWindowTitle('ERROR')
            warningMsg.setText('저장 오류가 발생하였습니다.')
            warningMsg.exec_()


app = QtWidgets.QApplication(sys.argv)
window = InvGUI()
window.show()
sys.exit(app.exec_())
