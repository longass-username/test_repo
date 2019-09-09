from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from random import randint
from time import sleep
import sys

class Window(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()
       
    def initUI(self):
        self.board = Board(self)
        self.setCentralWidget(self.board)
        
        self.statusbar = self.statusBar()
        self.board.msg2Statusbar[str].connect(self.statusbar.showMessage)
        
        self.initMenuBar()
        
        self.resize(500, 500)
        self.move(1200, 300)
        self.setWindowTitle('Snake')
        self.board.start()
        self.show()
        
    def initMenuBar(self):
        simple_diff = QAction('Simple', self)
        simple_diff.triggered.connect(self.simple_diff_change)
        medium_diff = QAction('Medium', self)
        medium_diff.triggered.connect(self.medium_diff_change)
        hard_diff = QAction('Hard', self)
        hard_diff.triggered.connect(self.hard_diff_change)
        standart_map = QAction('Standart', self)
        standart_map.triggered.connect(self.standart_map_change)
        line_map = QAction('Line', self)
        line_map.triggered.connect(self.line_map_change)
        cross_map = QAction('Cross', self)
        cross_map.triggered.connect(self.cross_map_change)
        
        menubar = self.menuBar()
        difficulty_menu = menubar.addMenu('Difficulty')
        difficulty_menu.addAction(simple_diff)
        difficulty_menu.addAction(medium_diff)
        difficulty_menu.addAction(hard_diff)
        map_menu = menubar.addMenu('Map')
        map_menu.addAction(standart_map)
        map_menu.addAction(line_map)
        map_menu.addAction(cross_map)
    
    def standart_map_change(self):
        self.board.walls = []
        
    def line_map_change(self):
        self.board.walls = []
        for i in range(25):
            self.board.walls.append([12,i])
    
    def cross_map_change(self):
        self.board.walls = []
        for i in range(25):
            self.board.walls.append([12,i])
        for i in range(25):
            self.board.walls.append([i,12])
       
    def simple_diff_change(self):
        self.board.SPEED = 350
        self.board.timer.stop()
        self.board.start()
    
    def medium_diff_change(self):
        self.board.SPEED = 150
        self.board.timer.stop()
        self.board.start()
        
    def hard_diff_change(self):
        self.board.SPEED = 50
        self.board.timer.stop()
        self.board.start()
        
        
class Board(QFrame):
    
    msg2Statusbar = pyqtSignal(str)
    
    SPEED = 150
    WIDTHINBLOCKS = 25
    HEIGHTINBLOCKS = 25
    
    def __init__(self, parent):
        super().__init__(parent)
        self.timer = QBasicTimer()
        self.snake = [[0,0]]
        self.food = [[10,9]]
        self.walls = []
        self.direction = 3
        self.can_turn = True
        self.new_game = True
        self.grow_snake = False
        self.game_over_screen = False
        self.setFocusPolicy(Qt.StrongFocus)
    
    def start(self):
        self.timer.start(self.SPEED, self)
        self.msg2Statusbar.emit('Score: ' + str(len(self.snake) - 1))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        field = self.contentsRect()
        
        self.draw_field(painter, field)
        
        for coord in self.food:
            self.draw_rect(painter,
                           coord[0] * self.square_width() ,
                           coord[1] * self.square_height(),
                           QColor(0xFF0000))
            
        for coord in self.snake:
            self.draw_rect(painter,
                           coord[0] * self.square_width() ,
                           coord[1] * self.square_height(),
                           QColor(0x000000))
            
        for coord in self.walls:
            self.draw_rect(painter,
                           coord[0] * self.square_width() ,
                           coord[1] * self.square_height(),
                           QColor(0x8c8c8c))
            
        if self.game_over_screen == True:
            self.draw_text(painter, event, 'GAME OVER')
            
    def draw_text(self, painter, event, text):
        painter.setPen(QColor(255, 51, 0))
        painter.setFont(QFont('Decorative', 50, 60))
        painter.drawText(event.rect(), Qt.AlignCenter, text)
    
    def draw_field(self, painter, field):
        brush = QBrush(Qt.Dense6Pattern)
        brush.setColor(QColor(0x39F239))
        painter.setBrush(brush)
        painter.drawRect(0,
                         0,
                         field.right(),
                         field.bottom())
    
    def draw_rect(self, painter, x, y, color):
        painter.fillRect(x,
                         y,
                         self.square_width(),
                         self.square_height(),
                         color)
    
    def drop_food(self):
        for i in range((len(self.snake) // 15 ) - len(self.food) + 1):
            tmp = [randint(1, Board.WIDTHINBLOCKS - 2), randint(1, Board.HEIGHTINBLOCKS - 2)]
            for coord in self.snake:
                if coord == tmp:
                    self.drop_food()
            for coord in self.walls:
                if coord == tmp:
                    self.drop_food()
            self.food.append(tmp)
                
    def is_food_eaten(self):
        for coord in self.food:
            if coord == self.snake[0]:
                self.food.remove(coord)
                self.drop_food()
                self.grow_snake = True
        
    def is_dead(self):
        if len(self.snake) >= 3:
            for i in range(1, len(self.snake)):
                if self.snake[0] == self.snake[i]:
                    self.timer.stop()
                    self.game_over_screen = True
                    self.repeat_msg_box()
                    self.update()
        if self.walls != []:
            for coord in self.walls:
                if self.snake[0] == coord:
                    self.timer.stop()
                    self.game_over_screen = True
                    self.repeat_msg_box()
                    self.update()
    
    def repeat_msg_box(self):
        self.update()
        sleep(0.2)
        reply = QMessageBox.question(self, 'Message',
            "Do you want to replay?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.snake = [[0,0]]
            self.food = [[10,9]]
            self.direction = 3
            self.can_turn = True
            self.new_game == True
            self.grow_snake = False
            self.game_over_screen = False
            self.start()
        else:
            qApp.quit()
           
    def move_obj(self):
        
        self.can_turn = True
        cur_x,cur_y = self.snake[0]
        
        if self.direction == 1:
            cur_x -= 1
            if cur_x < 0:
                cur_x = Board.WIDTHINBLOCKS - 1
        elif self.direction == 2:
            cur_x += 1
            if cur_x >= Board.WIDTHINBLOCKS:
                cur_x = 0
        elif self.direction == 3:
            cur_y += 1
            if cur_y >= Board.HEIGHTINBLOCKS:
                cur_y = 0
        elif self.direction == 4:
            cur_y -= 1
            if cur_y < 0:
                cur_y = Board.HEIGHTINBLOCKS - 1
        
        self.snake.insert(0,[cur_x,cur_y])
        
        if self.grow_snake == True:
            self.grow_snake = False
        else:
            self.snake.pop()
            
        self.msg2Statusbar.emit('Score: ' + str(len(self.snake) - 1))
        self.new_game = False
            
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            if self.direction != 2 and self.can_turn == True:
                self.direction = 1
                self.can_turn = False
        elif key == Qt.Key_Right:
            if self.direction != 1 and self.can_turn == True:
                self.direction = 2
                self.can_turn = False
        elif key == Qt.Key_Down:
            if self.direction != 4 and self.can_turn == True:
                self.direction = 3
                self.can_turn = False
        elif key == Qt.Key_Up:
            if self.direction != 3 and self.can_turn == True:
                self.direction = 4
                self.can_turn = False
        elif key == Qt.Key_P:
            self.timer.stop()
        elif key == Qt.Key_Space:
            self.start()
    
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.new_game == False:
                self.is_dead()
            self.move_obj()
            self.is_food_eaten()
            self.update()
    
    def square_width(self):
        return self.contentsRect().width() / Board.WIDTHINBLOCKS

    def square_height(self):
        return self.contentsRect().height() / Board.HEIGHTINBLOCKS       
      
if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())