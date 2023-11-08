from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QDialog,
    QScrollArea,
    QGraphicsView,
    QGraphicsScene,
    QPushButton
)

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QRect,
    QUrl
)

from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtSvg import QSvgWidget, QSvgRenderer, QGraphicsSvgItem

from gui.locationspecification_view import LocationSvgView_webengine, LocationSvgView_qsvg


class SvgDisplayTab_webengine(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, imagepath, **kwargs):
        super().__init__(**kwargs)
        main_layout = QHBoxLayout()

        self.svg = QWebEngineView()
        imageurl = QUrl.fromLocalFile(imagepath)
        self.svg.load(imageurl)
        main_layout.addWidget(self.svg)
        zoomfactorbutton = QPushButton("zoom factor")
        zoomfactorbutton.clicked.connect(lambda checked: print("zoom factor:", self.svg.zoomFactor()))
        main_layout.addWidget(zoomfactorbutton)
        # self.svg.show()
        self.setLayout(main_layout)
        print("zoom factor:", self.svg.zoomFactor())


    # def __init__(self, imagepath, **kwargs):
    #     super().__init__(**kwargs)
    #
    #     main_layout = QHBoxLayout()
    #
    #     img_layout = QVBoxLayout()
    #
    #     self.imagedisplay = LocationSvgView_webengine(parent=self, specificpath=imagepath)
    #     self.imagedisplay.svg.setZoomFactor(0.25)
    #     # self.imagedisplay.setMinimumWidth(400)
    #     img_layout.addWidget(self.imagedisplay)
    #
    #     zoom_layout = QVBoxLayout()
    #     # self.zoom_slider = QSlider(Qt.Vertical)
    #     # self.zoom_slider.setMinimum(1)
    #     # self.zoom_slider.setMaximum(8)
    #     # self.zoom_slider.setValue(0)
    #     # self.zoom_slider.valueChanged.connect(self.zoom)
    #     # zoom_layout.addWidget(self.zoom_slider)
    #     # zoom_layout.setAlignment(self.zoom_slider, Qt.AlignHCenter)
    #
    #     # self.link_button = QPushButton("Link")
    #     # self.link_button.setCheckable(True)
    #     # self.link_button.toggled.connect(lambda ischecked: self.linkbutton_toggled.emit(ischecked))
    #     # zoom_layout.addWidget(self.link_button)
    #     # zoom_layout.setAlignment(self.link_button, Qt.AlignHCenter)
    #
    #     main_layout.addLayout(img_layout)
    #     main_layout.addLayout(zoom_layout)
    #
    #     self.setLayout(main_layout)

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

    # def force_zoom(self, scale):
    #     self.blockSignals(True)
    #     self.zoom_slider.blockSignals(True)
    #     self.zoom(scale)
    #     self.zoom_slider.setValue(scale)
    #     self.blockSignals(False)
    #     self.zoom_slider.blockSignals(False)
    #
    # def force_link(self, ischecked):
    #     self.blockSignals(True)
    #     self.link_button.setChecked(ischecked)
    #     self.blockSignals(False)

class SvgDisplayTab_qsvg(QScrollArea):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, imagepath, **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        img_layout = QHBoxLayout()

        # self.svgwidget = QSvgWidget(imagepath, parent=self)
        # self.svgwidget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        # self.svgwidget.setFixedSize(self.svgwidget.renderer().defaultSize())
        if 'violet' in imagepath:
            svgwidget = QSvgWidget(imagepath, parent=self)
            svgwidget.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
            # svgwidget.setFixedSize(svgwidget.renderer().defaultSize()/4)
            self.setFixedSize(svgwidget.renderer().defaultSize()/4)
            dsize = svgwidget.renderer().defaultSize()
            dwidth = dsize.width()
            dheight = dsize.height()
            self.setWidget(svgwidget)
            # violetitem = QGraphicsSvgItem()
            # violetitem.setSharedRenderer(svgwidget.renderer())
            # violetitem.setElementId("Highlight")
            svgwidget.renderer().setViewBox(QRect(0+int(dwidth/4), 0, dwidth, dheight))
            # scn = QGraphicsScene()
            # scn.addItem(violetitem)
            # vw = QGraphicsView(scn)
            # img_layout.addWidget(vw)
            # transmatrix = vw.transform()
            # transmatrix.scale(0.7, 1.5)
            # vw.setTransform(transmatrix)
            print("bounds on element 'Highlight':", svgwidget.renderer().boundsOnElement('Highlight'))
        elif 'yellow' in imagepath:
            self.svgwidget = QSvgWidget(imagepath, parent=self)
            # self.svgwidget.setGeometry(100, 100, 100, 100)
            img_layout.addWidget(self.svgwidget)
        elif 'green' in imagepath:
            renderer = QSvgRenderer(imagepath, parent=self)
            greenitem = QGraphicsSvgItem()
            greenitem.setSharedRenderer(renderer)
            scn = QGraphicsScene()
            scn.addItem(greenitem)
            vw = QGraphicsView(scn)
            img_layout.addWidget(vw)


        # self.setFixedSize(self.svgwidget.renderer().defaultSize())
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    #     self.imagedisplay = LocationSvgView_qsvg(parent=self, specificpath=imagepath)
    #     self.imagedisplay.svg.setZoomFactor(0.25)
    #     # self.imagedisplay.setMinimumWidth(400)
    #     img_layout.addWidget(self.imagedisplay)
    #
    #     zoom_layout = QVBoxLayout()
    #     # self.zoom_slider = QSlider(Qt.Vertical)
    #     # self.zoom_slider.setMinimum(1)
    #     # self.zoom_slider.setMaximum(8)
    #     # self.zoom_slider.setValue(0)
    #     # self.zoom_slider.valueChanged.connect(self.zoom)
    #     # zoom_layout.addWidget(self.zoom_slider)
    #     # zoom_layout.setAlignment(self.zoom_slider, Qt.AlignHCenter)
    #
    #     # self.link_button = QPushButton("Link")
    #     # self.link_button.setCheckable(True)
    #     # self.link_button.toggled.connect(lambda ischecked: self.linkbutton_toggled.emit(ischecked))
    #     # zoom_layout.addWidget(self.link_button)
    #     # zoom_layout.setAlignment(self.link_button, Qt.AlignHCenter)
    #
        main_layout.addLayout(img_layout)
    #     main_layout.addLayout(zoom_layout)
    #
    #     self.setLayout(main_layout)
    #
    # def zoom(self, scale):
    #     factor_from_scale = {
    #         1: 0.25,
    #         2: 0.33,
    #         3: 0.5,
    #         4: 1.0,
    #         5: 2.0,
    #         6: 3.0,
    #         7: 4.0,
    #         8: 5.0
    #     }
    #     self.imagedisplay.svg.setZoomFactor(factor_from_scale[scale])
    #     # trans_matrix = self.imagedisplay.transform()
    #     # trans_matrix.reset()
    #     # trans_matrix = trans_matrix.scale(scale * self.imagedisplay.factor, scale * self.imagedisplay.factor)
    #     # self.imagedisplay.setTransform(trans_matrix)
    #
    #     self.zoomfactor_changed.emit(scale)
    #
    # def force_zoom(self, scale):
    #     self.blockSignals(True)
    #     self.zoom_slider.blockSignals(True)
    #     self.zoom(scale)
    #     self.zoom_slider.setValue(scale)
    #     self.blockSignals(False)
    #     self.zoom_slider.blockSignals(False)
    #
    # def force_link(self, ischecked):
    #     self.blockSignals(True)
    #     self.link_button.setChecked(ischecked)
    #     self.blockSignals(False)


class LocationGraphicsTestDialogOLD(QDialog):

    def __init__(self, app_settings, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        for img_name in app_ctx.temp_test_images.keys():
            self.tabs.addTab(SvgDisplayTab_webengine(app_ctx.temp_test_images[img_name]), img_name)

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)


class LocationGraphicsTestDialog(QDialog):

    def __init__(self, app_settings, app_ctx, whichtype, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.whichtype = whichtype  # 'webengine' or 'qsvg'

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        for img_name in app_ctx.temp_test_images.keys():
            if self.whichtype == 'webengine':
                self.tabs.addTab(SvgDisplayTab_webengine(app_ctx.temp_test_images[img_name]), img_name)
            elif self.whichtype == 'qsvg':
                self.tabs.addTab(SvgDisplayTab_qsvg(app_ctx.temp_test_images[img_name]), img_name)

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

