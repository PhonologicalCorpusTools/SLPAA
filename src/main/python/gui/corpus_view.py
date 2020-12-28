from PyQt5.QtCore import (
    Qt,
    QSize
)

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QListWidget,
    QVBoxLayout
)

from PyQt5.QtGui import (
    QIcon
)


class CorpusList(QListWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CorpusView(QWidget):
    def __init__(self, corpus_title='Untitled', **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # TODO: maybe make this editable
        self.corpus_title = QLabel(corpus_title)
        main_layout.addWidget(self.corpus_title)

        self.corpus_list = CorpusList(parent=self)
        main_layout.addWidget(self.corpus_list)