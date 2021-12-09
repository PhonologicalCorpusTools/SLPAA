from PyQt5.QtCore import (
    Qt,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QAbstractAnimation,
    QEvent,
    pyqtSignal,
    QRect
)
from PyQt5.QtWidgets import (
    QWidget,
    QScrollArea,
    QFrame,
    QToolButton,
    QGridLayout,
    QSizePolicy,
    QTabBar,
    QLineEdit,
    QMessageBox,
    QPushButton
)
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush
)


class CollapsibleSection(QWidget):
    def __init__(self, title='', animationDuration=300, **kwargs):
        """
        Ref: http://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
        """

        super().__init__(**kwargs)

        self.animationDuration = animationDuration
        self.toggleAnimation = QParallelAnimationGroup()
        self.contentArea = QScrollArea()
        self.headerLine = QFrame()
        self.toggleButton = QToolButton()
        self.mainLayout = QGridLayout()

        self.toggleButton.setStyleSheet('QToolButton { border: none; }')
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.setText(str(title))
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.headerLine.setFrameShape(QFrame.HLine)
        self.headerLine.setFrameShadow(QFrame.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.contentArea.setStyleSheet('QScrollArea { background-color: white; border: none; }')
        self.contentArea.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed) # todo kv was expading, fixed

        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

        # let the entire widget grow and shrink with its content
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

        # don't waste space
        self.mainLayout.setVerticalSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        row = 0
        self.mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, Qt.AlignLeft)
        self.mainLayout.addWidget(self.headerLine, row, 2, 1, 1)

        row += 1
        self.mainLayout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)

        def start_animation(checked):
            arrow_type = Qt.DownArrow if checked else Qt.RightArrow
            direction = QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward
            self.toggleButton.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        self.toggleButton.clicked.connect(start_animation)

    def setContentLayout(self, contentLayout):
        # Not sure if this is equivalent to self.contentArea.destroy()
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)

        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = 800 # todo kv: was contentLayout.sizeHint().height()

        for i in range(self.toggleAnimation.animationCount()-1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedHeight)
            spoilerAnimation.setEndValue(collapsedHeight + contentHeight)

        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)


# Ref: https://stackoverflow.com/questions/8707457/pyqt-editable-tab-labels
class EditableTabBar(QTabBar):
    plus_clicked = pyqtSignal(int)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setDocumentMode(True)
        self.setTabsClosable(True)

        self.editor = QLineEdit(self)
        self.editor.setWindowFlags(Qt.Popup)
        self.editor.setFocusProxy(self)
        self.editor.editingFinished.connect(self.handle_editing_finished)
        self.editor.installEventFilter(self)

    def eventFilter(self, widget, event):
        if (event.type() == QEvent.MouseButtonPress and not self.editor.geometry().contains(event.globalPos())) or \
                (event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape):
            self.editor.hide()
            return True
        return QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.edit_tab(index)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.currentIndex() == self.count()-1:
            self.plus_clicked.emit(self.currentIndex())

    def edit_tab(self, index):
        rect = self.tabRect(index)
        self.editor.setFixedSize(rect.size())
        self.editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self.editor.setText(self.tabText(index))
        if not self.editor.isVisible():
            self.editor.show()

    def handle_editing_finished(self):
        index = self.currentIndex()
        if index >= 0:
            if self.editor.text() in self.get_tab_names():
                QMessageBox.critical(parent=self, title='Name Error', text='Please use a name that has not been used!')
                return
            self.editor.hide()
            self.setTabText(index, self.editor.text())

    def get_tab_names(self):
        return [self.tabText(i) for i in range(self.count()-1)]  # -1 because the last tab is just '+'


# Ref: https://stackoverflow.com/questions/56806987/switch-button-in-pyqt
class ToggleSwitch(QPushButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        super().paintEvent(event)

        label = 'Dominant' if self.isChecked() else 'Weak'
        bg_color = Qt.green if self.isChecked() else Qt.red

        radius = 17
        width = 130
        center = self.rect().center()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QColor(0, 0, 0))

        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)
