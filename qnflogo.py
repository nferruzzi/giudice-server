#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaraServer
Copyright 2016 Nicola Ferruzzi <nicola.ferruzzi@gmail.com>
License: GPLv3 (see LICENSE)
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QNFLogo(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.pixmap = QPixmap(":/img/logo_rc_esteso.png")

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawPixmap(0, 0, self.pixmap)
