# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QScrollArea, QSizePolicy,
    QSpacerItem, QStatusBar, QToolButton, QVBoxLayout,
    QWidget)
from . import resources_rc

class Ui_main(object):
    def setupUi(self, main):
        if not main.objectName():
            main.setObjectName(u"main")
        main.resize(795, 459)
        main.setStyleSheet(u"QMainWindow{\n"
"	background-color: #1d3c51;\n"
"}\n"
"\n"
"QWidget#scroll_area_contents{\n"
"	background-color: #152e3e;\n"
"}\n"
"\n"
"/*QAbstractButton{\n"
"	background-color: #fdfdfd;\n"
"	border: 1px solid #d0d0d0;\n"
"	border-radius: 2px;\n"
"}\n"
"\n"
"QAbstractButton:hover{\n"
"	background-color: #e0eef9;\n"
"	border: 1px solid #0078d4;\n"
"}\n"
"\n"
"QAbstractButton:pressed{\n"
"	background-color: #cce4f7;\n"
"	border: 1px solid #005499;\n"
"}*/\n"
"\n"
"QScrollArea{\n"
"	background-color: #152e3e;;\n"
"}")
        self.centralwidget = QWidget(main)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.toolbar = QWidget(self.centralwidget)
        self.toolbar.setObjectName(u"toolbar")
        self.horizontalLayout = QHBoxLayout(self.toolbar)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.btn_grafico = QToolButton(self.toolbar)
        self.btn_grafico.setObjectName(u"btn_grafico")
        icon = QIcon()
        icon.addFile(u":/main/icons/graphic_mode.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_grafico.setIcon(icon)
        self.btn_grafico.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.btn_grafico)

        self.btn_tabla = QToolButton(self.toolbar)
        self.btn_tabla.setObjectName(u"btn_tabla")
        icon1 = QIcon()
        icon1.addFile(u":/main/icons/table_mode.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_tabla.setIcon(icon1)
        self.btn_tabla.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.btn_tabla)

        self.le_filtrar = QLineEdit(self.toolbar)
        self.le_filtrar.setObjectName(u"le_filtrar")
        self.le_filtrar.setMinimumSize(QSize(0, 30))
        font = QFont()
        font.setFamilies([u"Inter"])
        font.setPointSize(11)
        self.le_filtrar.setFont(font)
        self.le_filtrar.setStyleSheet(u"background-color: white;\n"
"color: black;")
        self.le_filtrar.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.le_filtrar)


        self.horizontalLayout_3.addWidget(self.toolbar)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setPixmap(QPixmap(u":/main/images/liai_logo.png"))

        self.horizontalLayout_3.addWidget(self.label)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.scroll_area = QScrollArea(self.centralwidget)
        self.scroll_area.setObjectName(u"scroll_area")
        font1 = QFont()
        font1.setFamilies([u"Ink Free"])
        self.scroll_area.setFont(font1)
        self.scroll_area.setStyleSheet(u"border-radius: 10px;\n"
"")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_contents = QWidget()
        self.scroll_area_contents.setObjectName(u"scroll_area_contents")
        self.scroll_area_contents.setGeometry(QRect(0, 0, 773, 327))
        self.scroll_area.setWidget(self.scroll_area_contents)

        self.verticalLayout.addWidget(self.scroll_area)

        main.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(main)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 795, 26))
        main.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(main)
        self.statusbar.setObjectName(u"statusbar")
        main.setStatusBar(self.statusbar)

        self.retranslateUi(main)

        QMetaObject.connectSlotsByName(main)
    # setupUi

    def retranslateUi(self, main):
        main.setWindowTitle(QCoreApplication.translate("main", u"LIAI Concreto", None))
        self.btn_grafico.setText(QCoreApplication.translate("main", u"1", None))
        self.btn_tabla.setText(QCoreApplication.translate("main", u"2", None))
        self.label.setText("")
    # retranslateUi

