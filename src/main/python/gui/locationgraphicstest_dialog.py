# from qt.QtWidgets import (
#     QHBoxLayout,
#     QVBoxLayout,
#     QTabWidget,
#     QWidget,
#     QDialog,
# )
#
# from qt.QtCore import (
#     pyqtSignal,
# )

from qt import (
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QDialog,
    pyqtSignal,
)

from gui.locationspecification_view import LocationSvgView


class SvgDisplayTab(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, imagepath, **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        img_layout = QVBoxLayout()

        self.imagedisplay = LocationSvgView(parent=self, specificpath=imagepath)
        self.imagedisplay.svg.setZoomFactor(0.25)
        # self.imagedisplay.setMinimumWidth(400)
        img_layout.addWidget(self.imagedisplay)

        zoom_layout = QVBoxLayout()
        # self.zoom_slider = QSlider(Qt.Orientation.Vertical)
        # self.zoom_slider.setMinimum(1)
        # self.zoom_slider.setMaximum(8)
        # self.zoom_slider.setValue(0)
        # self.zoom_slider.valueChanged.connect(self.zoom)
        # zoom_layout.addWidget(self.zoom_slider)
        # zoom_layout.setAlignment(self.zoom_slider, Qt.AlignmentFlag.AlignHCenter)

        # self.link_button = QPushButton("Link")
        # self.link_button.setCheckable(True)
        # self.link_button.toggled.connect(lambda ischecked: self.linkbutton_toggled.emit(ischecked))
        # zoom_layout.addWidget(self.link_button)
        # zoom_layout.setAlignment(self.link_button, Qt.AlignmentFlag.AlignHCenter)

        main_layout.addLayout(img_layout)
        main_layout.addLayout(zoom_layout)

        self.setLayout(main_layout)

    def zoom(self, scale):
        factor_from_scale = {
            1: 0.25,
            2: 0.33,
            3: 0.5,
            4: 1.0,
            5: 2.0,
            6: 3.0,
            7: 4.0,
            8: 5.0
        }
        self.imagedisplay.svg.setZoomFactor(factor_from_scale[scale])
        # trans_matrix = self.imagedisplay.transform()
        # trans_matrix.reset()
        # trans_matrix = trans_matrix.scale(scale * self.imagedisplay.factor, scale * self.imagedisplay.factor)
        # self.imagedisplay.setTransform(trans_matrix)

        self.zoomfactor_changed.emit(scale)

    def force_zoom(self, scale):
        self.blockSignals(True)
        self.zoom_slider.blockSignals(True)
        self.zoom(scale)
        self.zoom_slider.setValue(scale)
        self.blockSignals(False)
        self.zoom_slider.blockSignals(False)

    def force_link(self, ischecked):
        self.blockSignals(True)
        self.link_button.setChecked(ischecked)
        self.blockSignals(False)


class LocationGraphicsTestDialog(QDialog):

    def __init__(self, app_settings, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        for img_name in app_ctx.temp_test_images.keys():
            self.tabs.addTab(SvgDisplayTab(app_ctx.temp_test_images[img_name]), img_name)

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

