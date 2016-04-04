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
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
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
        self.pushButton.setText(_translate("MainWindow", "Avanza a prova successiva"))
        self.pushButton_2.setText(_translate("MainWindow", "Fine gara!"))
        self.menuGare.setTitle(_translate("MainWindow", "Files"))
        self.menuImpostazioni.setTitle(_translate("MainWindow", "Impostazioni"))
        self.actionNuova_gara.setText(_translate("MainWindow", "Nuova gara..."))
        self.actionCarica.setText(_translate("MainWindow", "Carica gara..."))
        self.actionSalva.setText(_translate("MainWindow", "Salva"))
        self.actionConfigura.setText(_translate("MainWindow", "Bonus"))
        self.actionGenera_rapporto.setText(_translate("MainWindow", "Genera rapporto..."))

