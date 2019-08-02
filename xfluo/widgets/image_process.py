# #########################################################################
# Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2018. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
import xfluo
from pylab import *
import pyqtgraph
import xfluo.widgets.image_process_actions as actions
import numpy as np

class ImageProcessWidget(QtWidgets.QWidget):

    sliderChangedSig = pyqtSignal(int, name='sliderChangedSig')
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    # shiftSig = pyqtSignal(str, name='sliderChangedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')
    thetaChangedSig = pyqtSignal(np.ndarray, name='thetaChangedSig')
    alignmentChangedSig = pyqtSignal(np.ndarray, np.ndarray, list, name="alignmentChangedSig")
    ySizeChanged = pyqtSignal(int, name='ySizeChanged')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")

    def __init__(self):
        super(ImageProcessWidget, self).__init__()
        self.thetas = []
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.ImageProcessControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget(self)
        self.actions = xfluo.ImageProcessActions()

        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.combo2.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.xUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.xDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.yUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.yDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.normalizeBtn.clicked.connect(self.normalize_params)
        self.ViewControl.cropBtn.clicked.connect(self.cut_params)
        self.ViewControl.gaussian33Btn.clicked.connect(self.actions.gauss33)
        self.ViewControl.gaussian55Btn.clicked.connect(self.actions.gauss55)
        self.ViewControl.captureBackground.clicked.connect(self.copyBG_params)
        self.ViewControl.setBackground.clicked.connect(self.pasteBG_params)
        self.ViewControl.deleteProjection.clicked.connect(self.exclude_params)
        self.ViewControl.testButton.clicked.connect(self.save_analysis)
        self.ViewControl.histogramButton.clicked.connect(self.histo_signal)
        self.imgAndHistoWidget.view.shiftSig.connect(self.shift_process)
        self.actions.dataSig.connect(self.send_data)
        self.actions.thetaSig.connect(self.send_thetas)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.imageSliderChanged)
        
        mainHBox = QtWidgets.QHBoxLayout()
        mainHBox.addWidget(self.ViewControl)
        mainHBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(mainHBox)
        self.x_shifts = None
        self.y_shifts = None
        self.centers = None

        palette = self.imgAndHistoWidget.lcd.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(85, 85, 255))
        # background color
        palette.setColor(palette.Background, QtGui.QColor(0, 170, 255))
        # "light" border
        palette.setColor(palette.Light, QtGui.QColor(255, 255, 0))
        # "dark" border
        palette.setColor(palette.Dark, QtGui.QColor(0, 0, 0))
        # set the palette
        self.imgAndHistoWidget.lcd.setPalette(palette)


    def showImgProcess(self, data, element_names, thetas, fnames, x_shifts, y_shifts, centers):

        self.x_shifts = x_shifts
        self.y_shifts = y_shifts
        self.centers = centers
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.element_names = element_names
        self.fnames = fnames
        self.data = data
        self.thetas = thetas
        self.ViewControl.combo1.clear()
        self.ViewControl.combo2.clear()
        for j in element_names:
            self.ViewControl.combo1.addItem(j)
        num_projections  = data.shape[1]
        for k in arange(num_projections):
            self.ViewControl.combo2.addItem(str(k+1))

        self.elementChanged()
        self.imgAndHistoWidget.sld.setRange(0, num_projections - 1)
        self.ViewControl.combo2.setVisible(False)
        self.imgAndHistoWidget.file_name_title.setText(str(fnames[0]))

    def imageSliderChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        self.updateFileDisplay(self.fnames, index)
        self.fnamesChanged.emit(self.fnames,index)
        self.updateSliderSlot(index)
        self.sliderChangedSig.emit(index)

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.ViewControl.combo2.currentIndex()
        print("TODO: during startup, 'projection' is undefined. ")
        self.updateElementSlot(element, projection)
        self.elementChangedSig.emit(element, projection)

    def updateSliderSlot(self, index):
        angle = round(self.thetas[index])
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.lcd.display(angle)
        self.imgAndHistoWidget.sld.setValue(index)
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :], border='w')

    def updateElementSlot(self, element, projection = None):
        if projection == None:
           projection =  self.imgAndHistoWidget.sld.value()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, projection, :, :], border='w')
        self.ViewControl.combo1.setCurrentIndex(element)
        self.ViewControl.combo2.setCurrentIndex(projection)

    def updateFileDisplay(self, fnames, index):
        self.fnames = fnames
        self.imgAndHistoWidget.file_name_title.setText(str(self.fnames[index]))

    def imgProcessBoxSizeChange(self):
        xSize = self.ViewControl.xSize
        ySize = self.ViewControl.ySize
        self.imgAndHistoWidget.view.xSize = xSize
        self.imgAndHistoWidget.view.ySize = ySize
        self.imgAndHistoWidget.view.ROI.setSize([xSize, ySize])
        x_pos = int(round(self.imgAndHistoWidget.view.x_pos))
        y_pos = int(round(self.imgAndHistoWidget.view.y_pos))
        self.imgAndHistoWidget.view.ROI.setPos([x_pos-xSize/2, y_pos-ySize/2])

    def imageChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :], border='w')

    def shift_process(self, command):
        index = self.imgAndHistoWidget.sld.value()
        if command == 'A':
            self.imgAndHistoWidget.sld.setValue(self.imgAndHistoWidget.sld.value() - 1)
            self.imageSliderChanged()
        if command == 'D':
            self.imgAndHistoWidget.sld.setValue(self.imgAndHistoWidget.sld.value() + 1)
            self.imageSliderChanged()
        if command == 'left':
            self.x_shifts[index] -=1
            self.actions.shiftProjectionLeft(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'right':
            self.x_shifts[index] +=1
            self.actions.shiftProjectionRight(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'up':
            self.y_shifts[index] +=1
            self.actions.shiftProjectionUp(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'down':
            self.y_shifts[index] -=1
            self.actions.shiftProjectionDown(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftLeft':
            self.x_shifts -=1
            self.actions.shiftDataLeft(self.data) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftRight':
            self.x_shifts +=1
            self.actions.shiftDataRight(self.data) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftUp':
            self.y_shifts +=1
            self.actions.shiftDataUp(self.data, self.thetas) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftDown':
            self.y_shifts -=1
            self.actions.shiftDataDown(self.data, self.thetas) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'Delete':
            self.x_shifts = np.delete(self.x_shifts, index)
            self.y_shifts = np.delete(self.y_shifts, index)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
            self.exclude_params()

    def background_value_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.background_value(img)

    def patch_params(self): 
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.patch(self.data, img, element, projection, x_pos, y_pos, x_size, y_size)

    def normalize_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        self.actions.normalize(data, element)
        
    def cut_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.cut(self.data, img, x_pos, y_pos, x_size, y_size)
        self.ySizeChanged.emit(y_size)

    def copyBG_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.copy_background(img)

    def pasteBG_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        self.actions.paste_background(data, element, projection, x_pos, y_pos, x_size, y_size, img)

    def analysis_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.noise_analysis(img)

    def bounding_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        img = data[element, projection, :,:]
        self.actions.bounding_analysis(img)
    
    def save_analysis(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        thetas = self.thetas
        img = data[element, projection, :,:]
        self.actions.save_bound_anlysis(data, element, thetas)

    def exclude_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        thetas = self.thetas
        index = projection    
        self.fnames.pop(index)
        num_files = len(self.fnames)
        temp_thetas = np.delete(thetas, projection, 0)

        if index>0:
            index -= 1
            num_files -= 1
        else:
            num_files -= 1

        self.updateSldRange(index, temp_thetas)
        # projection, self.data, self.thetas = self.actions.exclude_projection(projection, data, thetas)
        self.actions.exclude_projection(projection, data, thetas)
        self.dataChangedSig.emit(self.data)
        self.sldRangeChanged.emit(index, self.data,  self.thetas)
        self.updateFileDisplay(self.fnames, index)
        self.fnamesChanged.emit(self.fnames,index)
        self.imageSliderChanged()

    def data_scale_factor(self):
        #sf = get txtbox value
        
        # return self.data *= sf
        pass


    def histo_signal(self):
        data = self.data
        element_names = self.element_names
        num_elements = data.shape[0]
        num_projections = data.shape[1]
        histo_arr = np.ndarray(shape=(num_elements,num_projections), dtype=float)
        histo_mean = np.ndarray(shape=(num_elements), dtype=float)

        for i in range(num_elements):
            for j in range(num_projections):
                histo_arr[i,j] = np.sum(data[i,j])
            histo_mean[i] = np.mean(histo_arr[i])

        fig = plt.figure(figsize=(5,7))
        #ax1, ax2, ax3 = top right, middle
        ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
        ax2 = plt.subplot2grid((3, 3), (1, 0), colspan=3)
        ax3 = plt.subplot2grid((3, 3), (2, 0), colspan=3)

        ax1.hist(histo_arr[0], num_projections)
        ax2.hist(histo_arr[1], num_projections)
        ax3.hist(histo_arr[2], num_projections)

        ax1.set_title(element_names[0])
        ax2.set_title(element_names[1])
        ax3.set_title(element_names[2])

        for i in range(num_elements):
            print(element_names[i],": ",np.round(histo_mean[i]))

        print("Fe to Ti: ",np.round(histo_mean[1]/histo_mean[0]))
        print("Ti to Se: ",np.round(histo_mean[0]/histo_mean[2]))
        print("Fe to Se: ",np.round(histo_mean[1]/histo_mean[2]))
        # plt.show()

        return



    def updateSldRange(self, index, thetas):
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.sld.setRange(0, len(thetas) -1)
        self.imgAndHistoWidget.lcd.display(thetas[index])
        self.imgAndHistoWidget.sld.setValue(index)
        self.imageChanged()
        # self.imgAndHistoWidget.view.projView.setImage(data[element, projection])

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.imgAndHistoWidget.sld.value()
        x_pos = self.imgAndHistoWidget.view.x_pos
        y_pos = self.imgAndHistoWidget.view.y_pos
        x_size = self.ViewControl.xSize
        y_size = self.ViewControl.ySize
        img = self.data[element, projection, 
            int(round(abs(y_pos)) - y_size/2): int(round(abs(y_pos)) + y_size/2),
            int(round(x_pos) - x_size/2): int(round(x_pos) + x_size/2)]
        return element, projection, x_pos, y_pos, x_size, y_size, img

    def send_data(self, data):
        '''
        This sends a signal one level up indicating that the data array has changed
        and to update adjacent tabs with new data
        '''

        self.dataChangedSig.emit(data)

    def send_thetas(self, thetas):
        '''
        This sends a signal one level up indicating that the data array has changed
        and to update adjacent tabs with new data
        '''

        self.thetaChangedSig.emit(thetas)

