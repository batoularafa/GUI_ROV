import sys, cv2, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QScrollArea, QCheckBox, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
import pygame 
from math import ceil
import threading
import os
import serial
import time
import queue


class CameraWidget(QLabel):
    def __init__(self, parent, cam, w, h):
        super().__init__(parent)

        # self.setScaledContents (1)

        self.cam = cam
        self.w = w
        self.h = h
        self.cap = cv2.VideoCapture(self.cam)


        self.update()

    def update(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.w, self.h))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_image = QImage(frame.data, self.w, self.h, frame.strides[0], QImage.Format.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(q_image))


class OrientationsWidget (QWidget) : 
    def __init__(self, parent):
        super().__init__(parent)

        self.setMinimumSize (parent.width () // 3, parent.height () // 2)

        layout = QVBoxLayout ()

        self.setLayout (layout)

        self.depthLabel = QLabel (self)
        self.yawLabel = QLabel (self)
        self.pitchLabel = QLabel (self)
        self.rollLabel = QLabel (self)

        layout.addWidget (self.depthLabel)
        layout.addWidget (self.yawLabel)
        layout.addWidget (self.pitchLabel)
        layout.addWidget (self.rollLabel)

        # self.update ()

    def update (self,data) : 
        if data is None:
            pass
        else:
            print("orientation values:",data)
            
            depthReading = random.randint(0, 10)
            yawReading = random.randint(0, 10)
            pitchReading = random.randint(0, 10)
            rollReading = random.randint(0, 10)
            
            self.depthLabel.setText ("Depth: " + str (depthReading))
            self.yawLabel.setText ("Yaw: " + str (yawReading))
            self.pitchLabel.setText ("Pitch: " + str (pitchReading))
            self.rollLabel.setText ("Roll: " + str (rollReading))
  

class ThrustersWidget (QWidget) :
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.setMinimumSize (parent.width () // 3, parent.height () // 4)
        
        # Default colors
        self.square_color = QColor(0, 0, 0)  # Black for center square

        self.circle_colors = [
            QColor(0, 255, 0),  # Top
            QColor(0, 255, 0)
            # ,  # Bottom
            # # QColor(0, 255, 0),  # Left
            # QColor(0, 255, 0)   # Right
        ]

        self.rotated_square_colors = [
            QColor(0, 255, 0),  # Front-left
            QColor(0, 255, 0),  # Front-right
            QColor(0, 255, 0),  # Back-left
            QColor(0, 255, 0)   # Back-right
        ]
        # self.update()

    def set_colors(self, data):
        """Allows changing colors dynamically"""
        if data is None:
            pass
        else:
            print("thrusters values:", data)
           
            frontRightSpeed = random.randint(0, 255)
            backRightSpeed =random.randint(0, 255)
            frontLeftSpeed = random.randint(0, 255)
            backLeftSpeed = random.randint(0, 255)
            upFrontSpeed = random.randint(0, 255)
            upBackSpeed = random.randint(0, 255)

            self.square_color = QColor(0, 0, 0)
            self.circle_colors = [
                QColor(upFrontSpeed, 255 - upFrontSpeed, 0),  # Top
                QColor(upBackSpeed, 255 - upBackSpeed, 0)
                # ,  # Bottom
                # QColor(0, 255, 0),  # Left
                # QColor(0, 255, 0)   # Right
            ]
            self.rotated_square_colors = [
                QColor(frontLeftSpeed, 255 - frontLeftSpeed, 0),  # Front-left
                QColor(frontRightSpeed, 255 - frontRightSpeed, 0),  # Front-right
                QColor(backLeftSpeed, 255 - backLeftSpeed, 0),  # Back-left
                QColor(backRightSpeed, 255 - backRightSpeed, 0)   # Back-right
            ]
    

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get parent size constraints
        max_width = self.parent.width() // 3
        max_height = self.parent.height() // 4
     
        size = min(max_width, max_height)

        # Central square (50% of size)
        square_size = int(size * 0.45)           #B##changing the ratio changes the thrusters size### 
        square_x = (self.width() - square_size) // 2
        square_y = (self.height() - square_size) // 2
      

        # Draw the black center square
        painter.setPen(QPen(self.square_color, 3))
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(square_x, square_y, square_size, square_size)

        # Circles' and Rotated Squares' Positions
        offsets = [
            (square_x + square_size // 2, square_y - square_size // 3),  # Top
            (square_x + square_size // 2, square_y + square_size + square_size // 3)
            # ,  # Bottom
            # (square_x - square_size // 3, square_y + square_size // 2),  # Left
            # (square_x + square_size + square_size // 3, square_y + square_size // 2)  # Right
        ]

        rotated_offsets = [
            (square_x - square_size // 3, square_y - square_size // 3),  # Top-left
            (square_x + square_size + square_size // 3, square_y - square_size // 3),  # Top-right
            (square_x - square_size // 3, square_y + square_size + square_size // 3),  # Bottom-left
            (square_x + square_size + square_size // 3, square_y + square_size + square_size // 3)  # Bottom-right  #B##changed everything to divided by 3 for equal distribution of shapes ###
        ]

        circle_radius = int(square_size * 0.2)

        # Draw Circles with individual colors
        for i, (x, y) in enumerate(offsets):
            painter.setBrush(QBrush(self.circle_colors[i]))
            painter.drawEllipse(x - circle_radius, y - circle_radius, circle_radius * 2, circle_radius * 2)

        # Draw Rotated Squares with individual colors
        for i, (x, y) in enumerate(rotated_offsets):
            painter.setBrush(QBrush(self.rotated_square_colors[i]))
            painter.save()
            painter.translate(x, y)
            painter.rotate(45)  # Rotate by 45 degrees
            painter.drawRect(-circle_radius, -circle_radius, circle_radius * 2, circle_radius * 2)
            painter.restore()

    def updateThrusters (self, data) :
        self.set_colors(data)
        self.update()
class ScriptWidget (QWidget) :
    def __init__(self, desc):
        super().__init__()

        self.desc = desc

        hbox = QHBoxLayout (self)

        hbox.addWidget (QLabel (self.desc))

        self.button = QPushButton ("Run", self)
        self.button.clicked.connect (self.runScript)

        hbox.addWidget (self.button)

    def runScript (self) :
        print (self.desc)


class MainWindow (QMainWindow) :
    def __init__(self) :
        super().__init__()

        #initialize serial communication
        self.ser = serial.Serial('COM5', 115200, timeout=1)
        print("Serial communication initialized")

        self.showMaximized ()
        self.setWindowTitle ("AU Robotics ROV GUI")

        self.state = self.windowState ()

        self.initUI ()

        self.timer = QTimer ()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)

     
        #initialize controller thread
        self.controller_thread = ControllerThread(self, self.ser) #B##pass serial object to controller thread
        self.controller_thread.daemon = True
        self.controller_thread.start()
        

    def initUI (self) :
        
        centralWidget = QWidget ()
        self.setCentralWidget (centralWidget)

        self.leftCameraWidget = CameraWidget (self, 0, self.width () // 3, self.height () // 4)
        self.middleCameraWidget = CameraWidget (self, 1, self.width () // 3, self.height () // 4)
        self.rightCameraWidget = CameraWidget (self, 2, self.width () // 3, self.height () // 4)
        self.orientationsWidget = OrientationsWidget (self)
        self.controllerWidget = QWidget ()
        self.thrustersWidget = ThrustersWidget (self)
        self.tasksWidget = QScrollArea (self)
        self.scriptsWidget = QScrollArea (self)

        self.initTasks ()
        self.initScripts ()

        grid = QGridLayout ()

        grid.setColumnMinimumWidth(0, self.width() // 3)
        grid.setColumnMinimumWidth(1, self.width() // 4) #B##minimized the width of column 1###
        grid.setColumnMinimumWidth(2, self.width() // 3)

        grid.setRowMinimumHeight(0, self.height() // 5) #B##minimized the height of row 0###
        grid.setRowMinimumHeight(1, self.height() // 4)
        grid.setRowMinimumHeight(2, self.height() // 4)
        grid.setRowMinimumHeight(3, self.height() // 4)



        grid.addWidget (self.leftCameraWidget, 0, 0, 2, 1)
        grid.addWidget (self.middleCameraWidget, 0, 1, 2, 1)
        grid.addWidget (self.rightCameraWidget, 0, 2, 2, 1)

        grid.addWidget (self.orientationsWidget, 2, 0, 2, 1)

        grid.addWidget (self.tasksWidget, 2, 1, 1, 1)
        grid.addWidget (self.controllerWidget, 3, 1, 1, 1)

        grid.addWidget (self.scriptsWidget, 2, 2, 1, 1)
        grid.addWidget (self.thrustersWidget, 3, 2, 1, 1)

        centralWidget.setLayout (grid)

    def updateFrame (self) :
        if (self.state != self.windowState ()) :
            self.initUI ()
            self.state = self.windowState ()

        #initialize serial communication
        data = self.serial_comm() 

        self.leftCameraWidget.update ()
        self.middleCameraWidget.update ()
        self.rightCameraWidget.update ()
        self.orientationsWidget.update (data)
        self.thrustersWidget.updateThrusters (data)
        

    def initTasks (self):
        tasksContainer = QWidget ()
        tasksScrollLayout = QVBoxLayout (tasksContainer)

        tasksScrollLayout.addWidget (QCheckBox ("Task 1"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 2"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 3"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 4"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 5"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 6"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 7"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 8"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 9"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 10"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 11"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 12"))
        tasksScrollLayout.addWidget (QCheckBox ("Task 13"))

        self.tasksWidget.setWidget(tasksContainer)

    def initScripts (self) :
        scriptsContainer = QWidget ()
        scriptsScrollLayout = QVBoxLayout (scriptsContainer)

        scriptsScrollLayout.addWidget (ScriptWidget ("Script 1"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 2"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 3"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 4"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 5"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 6"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 7"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 8"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 9"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 10"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 11"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 12"))
        scriptsScrollLayout.addWidget (ScriptWidget ("Script 13"))

        self.scriptsWidget.setWidget(scriptsContainer)

    # method that will handle all serial communication
    def serial_comm(self):
        if self.ser.in_waiting > 0:  # Check if there is data available to read
            data = self.ser.readline().decode('utf-8').strip()  # Decode and strip newline
            return data
        
       

class ControllerThread(threading.Thread):
    def __init__(self, parent,serial):
        super().__init__()
        self.parent = parent
        self.running = True
        self.ser = serial #B#
    
    def run(self): 
        pygame.init()
        pygame.joystick.init()
        controller = pygame.joystick.Joystick(0)
   
        # 2 types of controls: axis and button
        axis = {}
        button = {}

        # Assign initial data values
        # Axes are initialized to 0.0
        for i in range(controller.get_numaxes()):
            axis[i] = 0.0
        # Buttons are initialized to False
        for i in range(controller.get_numbuttons()):
            button[i] = False
        for i in range(controller.get_numhats()):
            button[i] = False    

        # Deadzone values for axes
        deadzone = {0: 0.2, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0, 5: 0}

        # Labels for PS4 controller axes
        AXIS_LEFT_STICK_X = 0
        AXIS_LEFT_STICK_Y = 1
        AXIS_RIGHT_STICK_X = 2
        AXIS_RIGHT_STICK_Y = 3
        AXIS_L2 = 4
        AXIS_R2 = 5

        # Labels for PS4 controller buttons
        # Note that there are 16 buttons
        BUTTON_CROSS = 0
        BUTTON_CIRCLE = 1
        BUTTON_SQUARE = 2
        BUTTON_TRIANGLE = 3

        BUTTON_SHARE = 4
        BUTTON_PS = 5
        BUTTON_OPTIONS = 6

        BUTTON_L3 = 7
        BUTTON_R3 = 8

        BUTTON_L1 = 9
        BUTTON_R1 = 10

        BUTTON_UP = 11
        BUTTON_DOWN = 12
        BUTTON_LEFT = 13
        BUTTON_RIGHT = 14

        BUTTON_PAD = 15

        # L2 and R2 are initialized to -1.0
        axis[4] = -1.0
        axis[5] = -1.0

        # Main loop
        while True:
            # Get events
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    axis[event.axis] = round(event.value, 3)
                elif event.type == pygame.JOYBUTTONDOWN:
                    button[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    button[event.button] = False

            # Apply deadzone
            for i in deadzone:
                if abs(axis[i]) < deadzone[i]:
                    axis[i] = 0

            if 0:
                # Print out results
                os.system('cls')
                # Buttons
                print("Square:", button[BUTTON_SQUARE])
                print("Cross:", button[BUTTON_CROSS])
                print("Circle:", button[BUTTON_CIRCLE])
                print("Triangle:", button[BUTTON_TRIANGLE])
                print("Up:", button[BUTTON_UP])
                print("Down:", button[BUTTON_DOWN])
                print("Right:", button[BUTTON_RIGHT])
                print("Left:", button[BUTTON_LEFT])
                print("L1:", button[BUTTON_L1])
                print("R1:", button[BUTTON_R1])
                print("Share:", button[BUTTON_SHARE])
                print("Options:", button[BUTTON_OPTIONS])
                print("L3:", button[BUTTON_L3])
                print("R3:", button[BUTTON_R3])
                print("PS:", button[BUTTON_PS])
                print("Touch Pad:", button[BUTTON_PAD], "\n")
                # Axes
                print("L3 X:", axis[AXIS_LEFT_STICK_X])
                print("L3 Y:", axis[AXIS_LEFT_STICK_Y])
                print("R3 X:", axis[AXIS_RIGHT_STICK_X])
                print("R3 Y:", axis[AXIS_RIGHT_STICK_Y])
                print("L2:", axis[AXIS_L2])
                print("R2:", axis[AXIS_R2])
            
            else:
                # Serializing data to be sent
                data = ""
                for i in axis:
                    data += "#" + str(i) + "@" + str(axis[i])
                for i in range(ceil(len(button) / 8)):
                    data_i = 0
                    for j in range(8):
                        index = i*8 +j
                        if index<len(button):
                            data_i += 2 ** j * button[index]
                    data += "#" + str(i + len(axis)) + "@" + str(data_i)
                data += "\n"

            # Send controller string serially
            self.ser.write(data.encode())

            # Limited to 30 frames per second
            clock = pygame.time.Clock()
            clock.tick(5)
        


if __name__ == "__main__" :
    app = QApplication (sys.argv)
    mainWindow = MainWindow ()
    mainWindow.show ()
    sys.exit (app.exec_ ())