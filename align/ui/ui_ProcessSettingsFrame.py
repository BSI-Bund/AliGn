# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ProcessSettingsFrameijIWCz.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QProgressBar, QPushButton, QSizePolicy, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_ProcessSettingsFrame(object):
    def setupUi(self, ProcessSettingsFrame):
        if not ProcessSettingsFrame.objectName():
            ProcessSettingsFrame.setObjectName(u"ProcessSettingsFrame")
        ProcessSettingsFrame.resize(789, 169)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ProcessSettingsFrame.sizePolicy().hasHeightForWidth())
        ProcessSettingsFrame.setSizePolicy(sizePolicy)
        ProcessSettingsFrame.setMinimumSize(QSize(0, 158))
        ProcessSettingsFrame.setAutoFillBackground(False)
        self.gridLayout_2 = QGridLayout(ProcessSettingsFrame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.groupBox = QGroupBox(ProcessSettingsFrame)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.layoutWidget = QWidget(self.groupBox)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 241, 91))
        self.formLayout_2 = QFormLayout(self.layoutWidget)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.formLayout_2.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.lbl_peak_at = QLabel(self.layoutWidget)
        self.lbl_peak_at.setObjectName(u"lbl_peak_at")
        self.lbl_peak_at.setStyleSheet(u"")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.lbl_peak_at)

        self.dsb_peak_at = QSpinBox(self.layoutWidget)
        self.dsb_peak_at.setObjectName(u"dsb_peak_at")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.dsb_peak_at.sizePolicy().hasHeightForWidth())
        self.dsb_peak_at.setSizePolicy(sizePolicy2)
        self.dsb_peak_at.setReadOnly(True)
        self.dsb_peak_at.setMinimum(0)
        self.dsb_peak_at.setMaximum(10000000)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.dsb_peak_at)

        self.lbl_cut_area_start = QLabel(self.layoutWidget)
        self.lbl_cut_area_start.setObjectName(u"lbl_cut_area_start")
        self.lbl_cut_area_start.setMargin(0)

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.lbl_cut_area_start)

        self.dsb_cut_area_start = QSpinBox(self.layoutWidget)
        self.dsb_cut_area_start.setObjectName(u"dsb_cut_area_start")
        sizePolicy2.setHeightForWidth(self.dsb_cut_area_start.sizePolicy().hasHeightForWidth())
        self.dsb_cut_area_start.setSizePolicy(sizePolicy2)
        self.dsb_cut_area_start.setMaximum(10000000)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.dsb_cut_area_start)

        self.lbl_cut_area_end = QLabel(self.layoutWidget)
        self.lbl_cut_area_end.setObjectName(u"lbl_cut_area_end")
        self.lbl_cut_area_end.setMargin(0)

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.lbl_cut_area_end)

        self.dsb_cut_area_end = QSpinBox(self.layoutWidget)
        self.dsb_cut_area_end.setObjectName(u"dsb_cut_area_end")
        sizePolicy2.setHeightForWidth(self.dsb_cut_area_end.sizePolicy().hasHeightForWidth())
        self.dsb_cut_area_end.setSizePolicy(sizePolicy2)
        self.dsb_cut_area_end.setMaximum(10000000)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.dsb_cut_area_end)


        self.horizontalLayout.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(ProcessSettingsFrame)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(ProcessSettingsFrame)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.groupBox_2.setFlat(False)
        self.layoutWidget_2 = QWidget(self.groupBox_2)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(10, 20, 281, 91))
        self.formLayout = QFormLayout(self.layoutWidget_2)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.formLayout.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.lbl_process_traces = QLabel(self.layoutWidget_2)
        self.lbl_process_traces.setObjectName(u"lbl_process_traces")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.lbl_process_traces)

        self.sb_process_traces = QSpinBox(self.layoutWidget_2)
        self.sb_process_traces.setObjectName(u"sb_process_traces")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.sb_process_traces.sizePolicy().hasHeightForWidth())
        self.sb_process_traces.setSizePolicy(sizePolicy4)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.sb_process_traces)


        self.horizontalLayout.addWidget(self.groupBox_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.progressBar = QProgressBar(ProcessSettingsFrame)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.gridLayout.addWidget(self.progressBar, 0, 0, 1, 1)

        self.btn_start_stop_batch = QPushButton(ProcessSettingsFrame)
        self.btn_start_stop_batch.setObjectName(u"btn_start_stop_batch")
        self.btn_start_stop_batch.setEnabled(False)

        self.gridLayout.addWidget(self.btn_start_stop_batch, 0, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(ProcessSettingsFrame)

        QMetaObject.connectSlotsByName(ProcessSettingsFrame)
    # setupUi

    def retranslateUi(self, ProcessSettingsFrame):
        ProcessSettingsFrame.setWindowTitle(QCoreApplication.translate("ProcessSettingsFrame", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("ProcessSettingsFrame", u"Cut Settings", None))
        self.lbl_peak_at.setText(QCoreApplication.translate("ProcessSettingsFrame", u"Peak at:", None))
        self.lbl_cut_area_start.setText(QCoreApplication.translate("ProcessSettingsFrame", u"Cut area start:", None))
        self.lbl_cut_area_end.setText(QCoreApplication.translate("ProcessSettingsFrame", u"Cut area end:", None))
        self.groupBox_3.setTitle("")
        self.groupBox_2.setTitle(QCoreApplication.translate("ProcessSettingsFrame", u"Batch Settings", None))
        self.lbl_process_traces.setText(QCoreApplication.translate("ProcessSettingsFrame", u"Number of traces to process", None))
        self.btn_start_stop_batch.setText(QCoreApplication.translate("ProcessSettingsFrame", u"Start Batch", None))
    # retranslateUi

