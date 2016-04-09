# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.currentTrial = QtWidgets.QLineEdit(self.centralwidget)
        self.currentTrial.setEnabled(True)
        self.currentTrial.setStyleSheet("background-color: rgb(220, 220, 220);\n"
"border-color: rgb(0, 0, 0);")
        self.currentTrial.setReadOnly(True)
        self.currentTrial.setObjectName("currentTrial")
        self.horizontalLayout.addWidget(self.currentTrial)
        self.nextTrialButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextTrialButton.setObjectName("nextTrialButton")
        self.horizontalLayout.addWidget(self.nextTrialButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.endButton = QtWidgets.QPushButton(self.centralwidget)
        self.endButton.setObjectName("endButton")
        self.horizontalLayout.addWidget(self.endButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.description = QtWidgets.QLineEdit(self.centralwidget)
        self.description.setMinimumSize(QtCore.QSize(300, 0))
        self.description.setStyleSheet("background-color: rgb(220, 220, 220);\n"
"border-color: rgb(0, 0, 0);")
        self.description.setReadOnly(True)
        self.description.setObjectName("description")
        self.horizontalLayout_2.addWidget(self.description)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.usersCounter = QtWidgets.QLineEdit(self.centralwidget)
        self.usersCounter.setStyleSheet("background-color: rgb(220, 220, 220);\n"
"border-color: rgb(0, 0, 0);")
        self.usersCounter.setReadOnly(True)
        self.usersCounter.setObjectName("usersCounter")
        self.horizontalLayout_2.addWidget(self.usersCounter)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.displayPreview = QtWidgets.QLineEdit(self.centralwidget)
        self.displayPreview.setMinimumSize(QtCore.QSize(300, 0))
        self.displayPreview.setStyleSheet("background-color: rgb(220, 220, 220);\n"
"border-color: rgb(0, 0, 0);")
        self.displayPreview.setReadOnly(True)
        self.displayPreview.setObjectName("displayPreview")
        self.horizontalLayout_3.addWidget(self.displayPreview)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout_4.addWidget(self.tableView)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.markNQ = QtWidgets.QPushButton(self.groupBox)
        self.markNQ.setObjectName("markNQ")
        self.verticalLayout.addWidget(self.markNQ)
        spacerItem1 = QtWidgets.QSpacerItem(20, 64, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.sendToDisplay = QtWidgets.QPushButton(self.groupBox)
        self.sendToDisplay.setObjectName("sendToDisplay")
        self.verticalLayout.addWidget(self.sendToDisplay)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.userNumber = QtWidgets.QLineEdit(self.groupBox)
        self.userNumber.setMaximumSize(QtCore.QSize(150, 16777215))
        self.userNumber.setStyleSheet("background-color: rgb(220, 220, 220);")
        self.userNumber.setReadOnly(True)
        self.userNumber.setObjectName("userNumber")
        self.gridLayout.addWidget(self.userNumber, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.userTrialAverage = QtWidgets.QLineEdit(self.groupBox)
        self.userTrialAverage.setMaximumSize(QtCore.QSize(150, 16777215))
        self.userTrialAverage.setStyleSheet("background-color: rgb(220, 220, 220);")
        self.userTrialAverage.setReadOnly(True)
        self.userTrialAverage.setObjectName("userTrialAverage")
        self.gridLayout.addWidget(self.userTrialAverage, 1, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.userFinalVote = QtWidgets.QLineEdit(self.groupBox)
        self.userFinalVote.setMaximumSize(QtCore.QSize(150, 16777215))
        self.userFinalVote.setStyleSheet("background-color: rgb(220, 220, 220);")
        self.userFinalVote.setReadOnly(True)
        self.userFinalVote.setObjectName("userFinalVote")
        self.gridLayout.addWidget(self.userFinalVote, 2, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)
        self.userBonus = QtWidgets.QLineEdit(self.groupBox)
        self.userBonus.setMaximumSize(QtCore.QSize(150, 16777215))
        self.userBonus.setStyleSheet("background-color: rgb(220, 220, 220);")
        self.userBonus.setReadOnly(True)
        self.userBonus.setObjectName("userBonus")
        self.gridLayout.addWidget(self.userBonus, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem2 = QtWidgets.QSpacerItem(20, 63, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.deselectRow = QtWidgets.QPushButton(self.groupBox)
        self.deselectRow.setObjectName("deselectRow")
        self.verticalLayout.addWidget(self.deselectRow)
        self.horizontalLayout_4.addWidget(self.groupBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuGare = QtWidgets.QMenu(self.menubar)
        self.menuGare.setObjectName("menuGare")
        self.menuImpostazioni = QtWidgets.QMenu(self.menubar)
        self.menuImpostazioni.setObjectName("menuImpostazioni")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNuova_gara = QtWidgets.QAction(MainWindow)
        self.actionNuova_gara.setObjectName("actionNuova_gara")
        self.actionCarica = QtWidgets.QAction(MainWindow)
        self.actionCarica.setObjectName("actionCarica")
        self.actionSalva = QtWidgets.QAction(MainWindow)
        self.actionSalva.setObjectName("actionSalva")
        self.actionConfigura = QtWidgets.QAction(MainWindow)
        self.actionConfigura.setObjectName("actionConfigura")
        self.actionGenera_rapporto = QtWidgets.QAction(MainWindow)
        self.actionGenera_rapporto.setObjectName("actionGenera_rapporto")
        self.menuGare.addAction(self.actionNuova_gara)
        self.menuGare.addAction(self.actionCarica)
        self.menuGare.addAction(self.actionSalva)
        self.menuGare.addSeparator()
        self.menuGare.addAction(self.actionGenera_rapporto)
        self.menuImpostazioni.addAction(self.actionConfigura)
        self.menubar.addAction(self.menuGare.menuAction())
        self.menubar.addAction(self.menuImpostazioni.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Giudice di gara v1.0"))
        self.label.setText(_translate("MainWindow", "Prova corrente"))
        self.nextTrialButton.setText(_translate("MainWindow", "Avanza a prova successiva"))
        self.endButton.setText(_translate("MainWindow", "Fine gara!"))
        self.label_2.setText(_translate("MainWindow", "Descrizione"))
        self.label_3.setText(_translate("MainWindow", "Numero atleti rimanenti"))
        self.label_5.setText(_translate("MainWindow", "Testo sul display"))
        self.groupBox.setTitle(_translate("MainWindow", "Opzioni atleta"))
        self.markNQ.setText(_translate("MainWindow", "Marca non qualificato"))
        self.sendToDisplay.setText(_translate("MainWindow", "Mostra sul display"))
        self.label_4.setText(_translate("MainWindow", "Atleta:"))
        self.label_6.setText(_translate("MainWindow", "Media prova:"))
        self.label_7.setText(_translate("MainWindow", "Voto finale:"))
        self.label_8.setText(_translate("MainWindow", "Bonus:"))
        self.deselectRow.setText(_translate("MainWindow", "Deseleziona"))
        self.menuGare.setTitle(_translate("MainWindow", "Files"))
        self.menuImpostazioni.setTitle(_translate("MainWindow", "Impostazioni"))
        self.actionNuova_gara.setText(_translate("MainWindow", "Nuova gara..."))
        self.actionCarica.setText(_translate("MainWindow", "Carica gara..."))
        self.actionSalva.setText(_translate("MainWindow", "Salva come..."))
        self.actionConfigura.setText(_translate("MainWindow", "Bonus"))
        self.actionGenera_rapporto.setText(_translate("MainWindow", "Genera rapporto..."))

