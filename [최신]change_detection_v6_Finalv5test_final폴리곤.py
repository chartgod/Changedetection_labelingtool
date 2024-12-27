import pandas as pd
import cv2
import numpy as np
import os
import sys
import traceback
from PyQt5.QtCore import (
    Qt, QPoint, QEvent, QTimer, QStringListModel
)
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QBrush, QPolygon, QPixmap, QIntValidator, QCursor, QMouseEvent, QFont, QImage
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QAction, QMessageBox, QPushButton,
    QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QListView, QInputDialog,
    QFileDialog, QMenu, QFontDialog, QSplitter
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import webbrowser
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QTimer

# 전역 예외 처리기
def exception_hook(exctype, value, tb):
    tb_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(tb_msg)
    QMessageBox.critical(None, "오류 발생", tb_msg)
    # 프로그램 종료하지 않음

sys.excepthook = exception_hook

class ImageBox(QWidget):
    def __init__(self):
        super(ImageBox, self).__init__()

        # 라벨 리스트
        self.poly_list = []

        # 이미지 관련 변수들
        self.path = None  # 원본 이미지 경로
        self.scale = 1.0
        self.w = None
        self.h = None
        self.point = QPoint(0, 0)

        # 원본 및 스케일된 이미지
        self.img = None
        self.imgB = None  # QPixmap 형식

        # 상태 플래그들
        self.start_pos = None
        self.end_pos = None
        self.is_left_clicked = False
        self.is_moving = False
        self.setCursor(Qt.PointingHandCursor)
        self.is_drawing = False
        self.line = []
        self.pos = None
        self.is_tempB = False
        self.is_closed = False

        # 추가 변수들
        self.current_class = 1  # 기본 클래스 번호
        self.selected_poly_index = -1  # 선택된 폴리곤 없음

        # 키보드 이벤트 수신 가능하도록 설정
        self.setFocusPolicy(Qt.ClickFocus)

        # 라인 언두/리두 스택
        self.line_redo_stack = []
    def handle_polygon_class_input(self, pos):
        """
        주어진 위치가 포함된 폴리곤을 찾아 소멸, 생성 클래스를 입력받는 대화상자를 표시하는 메서드.
        """
        try:
            for index, poly_dict in enumerate(self.poly_list):
                points = poly_dict['points']
                # points의 길이가 짝수인지 확인
                if len(points) < 4 or len(points) % 2 != 0:
                    print(f"폴리곤 {index}의 points 길이가 올바르지 않습니다: {len(points)}")
                    continue

                poly = QPolygon([QPoint(int(self.get_absolute_coor([[points[i], points[i + 1]]])[0]),
                                        int(self.get_absolute_coor([[points[i], points[i + 1]]])[1]))
                                for i in range(0, len(points), 2)])

                # 폴리곤 내부에 주어진 위치가 있는지 확인
                if poly.containsPoint(pos, Qt.OddEvenFill):
                    # 소멸 클래스 입력 대화상자 열기
                    disappear_class, ok1 = QInputDialog.getInt(
                        self, "소멸 클래스 수정", "소멸 클래스 번호 입력 (0~6):",
                        value=6, min=0, max=6
                    )

                    if ok1:
                        # 0을 입력하면 6으로 처리
                        if disappear_class == 0:
                            disappear_class = 6

                        # 생성 클래스 입력 대화상자 열기
                        appear_class, ok2 = QInputDialog.getInt(
                            self, "생성 클래스 수정", "생성 클래스 번호 입력 (0~6):",
                            value=6, min=0, max=6
                        )

                        if ok2:
                            if appear_class == 0:
                                appear_class = 6

                            # 선택된 폴리곤의 클래스 정보를 소멸/생성 클래스로 업데이트
                            self.poly_list[index]['class'] = (disappear_class, appear_class)

                            # 이미지 라벨 업데이트
                            self.bigbox.image_labels[self.path] = self.poly_list.copy()
                            self.repaint()
                    break  # 탐지된 폴리곤이 처리되었으므로 루프 종료
        except Exception as e:
            print(f"handle_polygon_class_input 오류: {e}")

    def mouseDoubleClickEvent(self, e):
        """
        마우스 더블 클릭 이벤트 처리
        """
        try:
            # 클릭한 좌표를 기준으로 가까운 폴리곤을 찾기
            click_pos = e.pos()
            for index, poly_dict in enumerate(self.poly_list):
                points = poly_dict['points']
                # points의 길이가 짝수인지 확인
                if len(points) < 4 or len(points) % 2 != 0:
                    print(f"폴리곤 {index}의 points 길이가 올바르지 않습니다: {len(points)}")
                    continue

                poly = QPolygon([QPoint(int(self.get_absolute_coor([[points[i], points[i + 1]]])[0]),
                                        int(self.get_absolute_coor([[points[i], points[i + 1]]])[1]))
                                for i in range(0, len(points) - 1, 2)])

                # 폴리곤 내부에 더블 클릭된 위치가 있는지 확인
                if poly.containsPoint(click_pos, Qt.OddEvenFill):
                    # 클래스 입력 대화상자 열기
                    class_number, ok = QInputDialog.getInt(self, "클래스 수정", "새 클래스 번호 입력 (0~6):",
                                                           value=poly_dict['class'], min=0, max=6)
                    if ok:
                        # 0을 입력하면 6으로 처리
                        if class_number == 0:
                            class_number = 6
                        # 선택된 폴리곤의 클래스 업데이트
                        self.poly_list[index]['class'] = class_number
                        # 이미지 라벨 업데이트
                        self.bigbox.image_labels[self.path] = self.poly_list.copy()
                        self.repaint()
                    break
        except Exception as e:
            print(f"mouseDoubleClickEvent 오류: {e}")

    def set_image(self):
        """
        이미지를 설정하고 위젯 크기를 이미지 크기에 맞게 조정
        """
        try:
            img_array = np.fromfile(self.path, np.uint8)  # 한글 경로 문제로 우회
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 이미지 디코딩
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # RGB 순서로 변환
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qimg = QImage(img, width, height, bytesPerLine, QImage.Format_RGB888)
            self.img = QPixmap(qimg)
        except:
            self.img = QPixmap(self.path)

        try:
            # 스케일 값 초기화
            self.scale = 1.0
            # 이미지 크기 초기화
            self.w = self.img.width()
            self.h = self.img.height()

            # 위젯 크기 조정
            self.setMinimumSize(800, 800)

            self.point = QPoint(0, 0)
            self.repaint()
        except Exception as e:
            print(f"set_image 오류: {e}")
            QMessageBox.warning(self, "오류", f"이미지 설정 실패: {e}")

    def paintEvent(self, e):
        """
        페인트 이벤트 수신: 이미지, 폴리곤, 미완성 선, 상태 텍스트를 모두 그리기
        """
        try:
            if self.img:
                painter = QPainter()
                painter.begin(self)

                # 이미지 그리기
                if self.is_tempB and self.imgB:
                    painter.drawPixmap(int(self.point.x()), int(self.point.y()), int(self.w), int(self.h), self.imgB)
                else:
                    painter.drawPixmap(int(self.point.x()), int(self.point.y()), int(self.w), int(self.h), self.img)

                # 완성된 폴리곤 그리기
                for index, poly_dict in enumerate(self.poly_list):
                    points = poly_dict['points']
                    class_number = poly_dict['class']

                    # 클래스 번호에 따른 색상 설정
                    pen = QPen(self.get_class_color(class_number))
                    pen.setWidth(3)

                    # 선택된 폴리곤을 두꺼운 선으로 강조 표시
                    if index == self.selected_poly_index:
                        pen.setWidth(5)  # 선택된 폴리곤 강조

                    painter.setPen(pen)
                    brush = QBrush(self.get_class_color(class_number, alpha=50))
                    painter.setBrush(brush)

                    # points의 길이가 짝수인지 확인
                    if len(points) < 4 or len(points) % 2 != 0:
                        print(f"폴리곤 {index}의 points 길이가 올바르지 않습니다: {len(points)}")
                        continue

                    # 폴리곤 좌표를 QPolygon으로 변환
                    poly = QPolygon()
                    for i in range(0, len(points) - 1, 2):
                        x, y = self.get_absolute_coor([[points[i], points[i + 1]]])
                        if np.isnan(x) or np.isnan(y):
                            continue
                        poly.append(QPoint(int(x), int(y)))
                    painter.drawPolygon(poly)

                # 미완성된 선 그리기 (선택된 클래스 색상)
                if self.is_drawing and self.pos and self.line:
                    pen = QPen(self.get_class_color(self.current_class))
                    pen.setWidth(3)
                    painter.setPen(pen)

                    start_x, start_y = self.get_absolute_coor([[self.line[0], self.line[1]]])
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(QPoint(int(start_x), int(start_y)), 5, 5)  # 시작점 표시

                    # 닫힌 폴리곤을 완성할 경우
                    if self.is_closed:
                        end_x, end_y = self.get_absolute_coor([[self.line[0], self.line[1]]])
                        painter.drawEllipse(QPoint(int(end_x), int(end_y)), 15, 15)

                    # 선 그리기
                    for i in range(0, len(self.line) - 2, 2):
                        x1, y1 = self.get_absolute_coor([[self.line[i], self.line[i + 1]]])
                        x2, y2 = self.get_absolute_coor([[self.line[i + 2], self.line[i + 3]]])
                        if np.isnan(x1) or np.isnan(y1) or np.isnan(x2) or np.isnan(y2):
                            continue
                        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

                    # 마지막 선 그리기 (현재 마우스 위치까지)
                    if self.pos:
                        last_x, last_y = self.get_absolute_coor([[self.line[-2], self.line[-1]]])
                        painter.drawLine(int(last_x), int(last_y), int(self.pos.x()), int(self.pos.y()))

                # 상태 텍스트 그리기 (이미지와 폴리곤 위에)
                font = QFont()
                font.setPointSize(24)
                painter.setFont(font)
                text_x = 10  # 좌측 상단 여백
                text_y = 40  # 텍스트 상단 여백
                if self.is_tempB:
                    painter.setPen(QPen(Qt.red))
                    painter.drawText(text_x, text_y, "변화 후 (After Change)")
                else:
                    painter.setPen(QPen(Qt.blue))
                    painter.drawText(text_x, text_y, "변화 전 (Before Change)")

                painter.end()

            # 라벨 목록 업데이트
            self.bigbox.set_list()

        except Exception as e:
            print(f"paintEvent 오류: {e}")

    def get_class_color(self, class_number, alpha=255):
        # 다중 클래스인 경우 기본 검정색으로 표시
        if isinstance(class_number, tuple):
            return QColor(0, 0, 0, alpha)

        # 클래스 번호에 따른 색상 매핑
        if class_number == 6:  # 객체 없음
            color = QColor(128, 128, 128, alpha)  # 회색
        elif class_number == 1:
            color = QColor(139, 69, 19, alpha)  # 갈색
        elif class_number == 2:
            color = QColor(255, 255, 0, alpha)  # 노란색
        elif class_number == 3:
            color = QColor(144, 238, 144, alpha)  # 연한 녹색
        elif class_number == 4:
            color = QColor(255, 0, 0, alpha)  # 빨간색
        elif class_number == 5:
            color = QColor(0, 0, 255, alpha)  # 파란색
        else:
            color = QColor(0, 0, 0, alpha)  # 기본 검정색
        return color

    def get_absolute_coor(self, coord_list):
        abs_list = []
        for coor in coord_list:
            x1 = self.point.x() + self.scale * coor[0]
            y1 = self.point.y() + self.scale * coor[1]
            abs_list.extend([x1, y1])
        return abs_list

    def mouseMoveEvent(self, e):
        """
        마우스 이동 이벤트 처리
        """
        try:
            # 이미지 이동
            if self.is_left_clicked:
                self.end_pos = e.pos() - self.start_pos
                self.point = self.point + self.end_pos
                self.start_pos = e.pos()
                self.repaint()
                self.is_moving = True

            # 선 그리기 중 마우스 위치 기록
            if self.is_drawing:
                self.pos = e.pos()
                if len(self.line) >= 2:
                    x1 = self.point.x() + self.scale * self.line[0]
                    y1 = self.point.y() + self.scale * self.line[1]
                    if abs(self.pos.x() - x1) < 10 and abs(self.pos.y() - y1) < 10 and len(self.line) > 4:
                        self.is_closed = True
                    else:
                        self.is_closed = False
                self.repaint()
        except Exception as e:
            print(f"mouseMoveEvent 오류: {e}")

    def mousePressEvent(self, e):
        # 플래그 변경
        if e.button() == Qt.LeftButton:
            self.setFocus()
            self.is_left_clicked = True
            self.start_pos = e.pos()

    def mouseReleaseEvent(self, e):
        try:
            # 플래그 변경
            if e.button() == Qt.LeftButton:
                self.is_left_clicked = False
                # 선 또는 점 기록
                if not self.is_moving:
                    # 절대 위치 계산
                    absolute_position = e.pos() - self.point
                    a = absolute_position / self.scale

                    # 선 그리기 시작 또는 종료
                    self.is_drawing = True
                    if self.is_drawing:
                        self.update_line(a)
                self.is_moving = False
            if e.button() == Qt.RightButton and not self.is_moving and self.is_drawing:
                rightMenu = QMenu(self)
                finish_act = QAction(u"Finish", self,
                                    triggered=lambda: self.update_line(None, "finish"))
                cancel_act = QAction(u"Cancel", self,
                                    triggered=lambda: self.update_line(None, "cancel"))
                rightMenu.addAction(finish_act)
                rightMenu.addAction(cancel_act)
                rightMenu.exec_(QCursor.pos())
        except Exception as e:
            print(f"mouseReleaseEvent 오류: {e}")

    def update_line(self, abs, flag="draw"):
        try:
            if flag == "cancel":
                self.line = []
                self.line_redo_stack.clear()
                self.is_drawing = False
                self.repaint()
                self.is_closed = False
            else:
                if flag == "finish":
                    if len(self.line) > 4:
                        # 현재 상태를 undo 스택에 저장
                        self.bigbox.push_undo()
                        self.is_drawing = False
                        self.is_closed = False
                        # 클래스 정보와 함께 폴리곤 저장
                        self.poly_list.append({'points': self.line.copy(), 'class': self.current_class})
                        self.repaint()
                        self.line = []
                        self.line_redo_stack.clear()
                        # 이미지 라벨 업데이트
                        self.bigbox.image_labels[self.path] = self.poly_list.copy()
                        # redo 스택 비우기
                        self.bigbox.redo_stack.clear()

                        # **자동 포인트 추가 기능 해제**
                        self.bigbox.auto_adding_points = False
                        self.bigbox.auto_add_timer.stop()

                    else:
                        # 점이 두 개 이하일 때 취소
                        self.update_line(None, "cancel")
                else:
                    if self.is_closed:
                        self.update_line(None, "finish")
                    else:
                        # 점 업데이트
                        self.line.append(abs.x())
                        self.line.append(abs.y())
                        # 점 추가 시 redo 스택 초기화
                        self.line_redo_stack.clear()
            self.repaint()
        except Exception as e:
            print(f"update_line 오류: {e}")
            QMessageBox.warning(self, "오류", f"선 업데이트 실패: {e}")

    def keyPressEvent(self, event):
        """
        키보드 이벤트 처리
        """
        if event.key() == Qt.Key_S:
            # 현재 마우스 커서 위치를 가져와 폴리곤 클래스 입력 처리
            cursor_pos = QCursor.pos()
            local_pos = self.mapFromGlobal(cursor_pos)

            # 마우스 위치에서 폴리곤 찾기 및 소멸, 생성 클래스 입력
            try:
                for index, poly_dict in enumerate(self.poly_list):
                    points = poly_dict['points']
                    # points의 길이가 짝수인지 확인
                    if len(points) < 4 or len(points) % 2 != 0:
                        print(f"폴리곤 {index}의 points 길이가 올바르지 않습니다: {len(points)}")
                        continue

                    poly = QPolygon([QPoint(
                        int(self.get_absolute_coor([[points[i], points[i + 1]]])[0]),
                        int(self.get_absolute_coor([[points[i], points[i + 1]]])[1])
                    ) for i in range(0, len(points), 2)])

                    # 폴리곤 내부에 마우스 위치가 있는지 확인
                    if poly.containsPoint(local_pos, Qt.OddEvenFill):
                        # 소멸 클래스 입력
                        disappear_class, ok1 = QInputDialog.getInt(
                            self, "소멸 클래스 수정", "소멸 클래스 번호 입력 (0~6):",
                            value=6, min=0, max=6
                        )

                        if ok1:
                            # 0을 입력하면 6으로 처리
                            if disappear_class == 0:
                                disappear_class = 6

                            # 생성 클래스 입력
                            appear_class, ok2 = QInputDialog.getInt(
                                self, "생성 클래스 수정", "생성 클래스 번호 입력 (0~6):",
                                value=6, min=0, max=6
                            )

                            if ok2:
                                if appear_class == 0:
                                    appear_class = 6

                                # 선택된 폴리곤의 클래스 정보를 업데이트
                                self.poly_list[index]['class'] = (disappear_class, appear_class)

                                # 이미지 라벨 업데이트
                                self.bigbox.image_labels[self.path] = self.poly_list.copy()
                                self.repaint()
                        break  # 탐지된 폴리곤이 처리되었으므로 루프 종료
            except Exception as e:
                print(f"S 키 입력 처리 오류: {e}")

        elif event.key() == Qt.Key_A:
            # 현재 마우스 위치에 왼쪽 클릭 이벤트 시뮬레이션
            pos = self.mapFromGlobal(QCursor.pos())
            self.is_moving = False
            synthetic_event = QMouseEvent(QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            self.mouseReleaseEvent(synthetic_event)
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            if self.is_drawing:
                if self.line:
                    self.line_redo_stack.append(self.line[-2:])
                    self.line = self.line[:-2]
                    self.repaint()
            else:
                self.bigbox.undo()
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            if self.is_drawing:
                if self.line_redo_stack:
                    self.line.extend(self.line_redo_stack.pop())
                    self.repaint()
            else:
                self.bigbox.redo()
        else:
            super().keyPressEvent(event)


    def wheelEvent(self, event):
        # 줌 인/아웃 기능 구현
        try:
            angle = event.angleDelta() / 8
            angleY = angle.y()
            zoom_factor = 1.1
            if angleY > 0:
                # 줌 인
                self.scale *= zoom_factor
            else:
                # 줌 아웃
                self.scale /= zoom_factor
            # 이미지 크기 조정
            self.w = self.img.width() * self.scale
            self.h = self.img.height() * self.scale
            self.repaint()
        except Exception as e:
            print(f"wheelEvent 오류: {e}")

class change_detection(QMainWindow):
    def __init__(self, parent=None):
        super(change_detection, self).__init__(parent)
        self.temp_listA = []
        self.temp_listB = []
        self.image_labels = {}  # 이미지별 라벨 저장 딕셔너리

        # Undo 및 Redo 스택
        self.undo_stack = []
        self.redo_stack = []

        # 선택된 이미지 경로를 저장하는 변수 추가
        self.selected_b_image_path = None  # Temporary B 리스트에서 선택된 이미지 경로

        # 윈도우 크기 설정
        self.resize(int(1400*0.8), int(1100*0.8))
        # QTimer 설정: 단일 클릭과 더블 클릭 구분
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.handle_single_click)

        importAct = QAction('Import', self, triggered=self.openimage)
        saveAct = QAction('Save', self, triggered=self.savepoint)
        saveAct.setShortcut('Ctrl+S')
        undoAct = QAction('Undo', self, triggered=self.undo)
        redoAct = QAction('Redo', self, triggered=self.redo)
        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.close)

        bar = self.menuBar()
        file = bar.addMenu("File")
        help_menu = bar.addMenu("Help")
        file.addActions([importAct, saveAct, undoAct, redoAct, exitAct])

        # 웹 브라우저에서 URL을 여는 QAction
        url_act = QAction("URL : https://github.com/chartgod/Changedetection_labelingtool", self)
        url_act.triggered.connect(lambda: webbrowser.open("https://github.com/chartgod/Changedetection_labelingtool"))

        help_menu.addAction("Question : dlgkstn68@naver.com, LEE-SEUNG-HEON")
        help_menu.addAction(url_act)
        # 이미지 박스 설정
        self.box = ImageBox()
        self.box.setMouseTracking(True)
        self.box.bigbox = self

        # 라벨 리스트
        self.LV_label = QListView()
        self.LV_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.LV_label.customContextMenuRequested.connect(self.rightMenuShow2)

        # 더블 클릭 시 select_polygon 호출
        # 클릭 이벤트와 더블 클릭 이벤트 연결
        self.LV_label.clicked.connect(self.start_single_click_timer)
        self.LV_label.doubleClicked.connect(self.handle_double_click)

        # 파일 리스트
        self.LV_A = QListView()
        self.LV_B = QListView()

        # 버튼 및 입력창
        self.import_btn = QPushButton("Import...")
        self.import_btnB = QPushButton("Import...")
        self.label_a = QLabel("변화 전(B 디렉터리)")
        self.label_b = QLabel("변화 후(A 디렉터리)")
        self.save_btn = QPushButton("Save Label")
        self.switch_btn = QPushButton('전환 On')
        self.auto_switch_btn = QPushButton('자동 전환')
        self.class_input_label = QLabel('Class:')
        self.class_input = QLineEdit()
        self.class_input.setText('1')
        self.class_input.setValidator(QIntValidator(0, 6))  # 클래스 0~6 허용

        # 상태 변수들
        self.auto_switching = False
        self.auto_switch_interval = 1000  # 기본 간격(ms)

        # 추가된 상태 변수
        self.auto_adding_points = False
        self.auto_add_interval = 200  # milliseconds
        self.auto_add_timer = QTimer()
        self.auto_add_timer.timeout.connect(self.add_point_at_cursor)

        # 시그널 및 슬롯 연결
        self.setWindowTitle("Change_detection_Tool")
        self.import_btn.clicked.connect(lambda: self.openimage("A"))
        self.import_btnB.clicked.connect(lambda: self.openimage("B"))
        self.LV_A.clicked.connect(self.load_image_pair)
        self.LV_B.clicked.connect(self.load_image_pair)
        self.save_btn.clicked.connect(self.savepoint)
        self.switch_btn.clicked.connect(self.change_switch_btn)
        self.auto_switch_btn.clicked.connect(self.auto_switch_dialog)
        self.class_input.returnPressed.connect(self.update_class)

        # 레이아웃 설정
        H_Overall = QHBoxLayout()
        V_Tool = QVBoxLayout()
        V_Imagebox = QVBoxLayout()
        H_TempBox = QHBoxLayout()

        # 도구 영역
        V_Tool.addWidget(self.save_btn)
        V_Tool.addWidget(self.switch_btn)
        V_Tool.addWidget(self.auto_switch_btn)

        # 클래스 버튼들 가로 배치
        H_ClassButtons = QHBoxLayout()  # H_ClassButtons 선언

        # "객체 없음" 버튼 추가
        self.no_object_btn = QPushButton("객체 없음")
        self.no_object_btn.clicked.connect(lambda: self.update_class_from_button(6))  # 클래스 6으로 설정
        H_ClassButtons.addWidget(self.no_object_btn)

        # 나머지 클래스 버튼들 추가
        self.building_btn = QPushButton("건축물")
        self.building_btn.clicked.connect(lambda: self.update_class_from_button(1))
        H_ClassButtons.addWidget(self.building_btn)
        self.road_btn = QPushButton("도로")
        self.road_btn.clicked.connect(lambda: self.update_class_from_button(2))
        H_ClassButtons.addWidget(self.road_btn)
        self.green_btn = QPushButton("녹지")
        self.green_btn.clicked.connect(lambda: self.update_class_from_button(3))
        H_ClassButtons.addWidget(self.green_btn)
        self.wildfire_btn = QPushButton("산불피해")
        self.wildfire_btn.clicked.connect(lambda: self.update_class_from_button(4))
        H_ClassButtons.addWidget(self.wildfire_btn)
        self.water_btn = QPushButton("수계")
        self.water_btn.clicked.connect(lambda: self.update_class_from_button(5))
        H_ClassButtons.addWidget(self.water_btn)

        V_Tool.addLayout(H_ClassButtons)

        V_Tool.addWidget(self.class_input_label)
        V_Tool.addWidget(self.class_input)
        V_Tool.addLayout(H_TempBox)

        V_Imagebox.addWidget(self.box)

        TempA = QVBoxLayout()
        TempA.addWidget(self.import_btn)
        TempA.addWidget(self.label_a)
        TempA.addWidget(self.LV_A)
        TempB = QVBoxLayout()
        TempB.addWidget(self.import_btnB)
        TempB.addWidget(self.label_b)
        TempB.addWidget(self.LV_B)
        H_TempBox.addLayout(TempA)
        H_TempBox.addLayout(TempB)

        # 오른쪽 패널 구성 (도구 + 라벨 리스트)
        V_RightPanel = QVBoxLayout()
        V_RightPanel.addLayout(V_Tool)
        V_RightPanel.addWidget(self.LV_label)

        right_widget = QWidget()
        right_widget.setLayout(V_RightPanel)

        image_widget = QWidget()
        image_widget.setLayout(V_Imagebox)

        # 스플리터 설정
        H_Splitter = QSplitter(Qt.Horizontal)
        H_Splitter.addWidget(image_widget)
        H_Splitter.addWidget(right_widget)
        H_Splitter.setStretchFactor(0, 3)
        H_Splitter.setStretchFactor(1, 1)
        H_Splitter.setSizes([800, 200])

        main_layout = QHBoxLayout()
        main_layout.addWidget(H_Splitter)
        main_frame = QWidget()
        main_frame.setLayout(main_layout)
        self.setCentralWidget(main_frame)

        # 메인 윈도우가 키보드 이벤트를 받을 수 있도록 설정
        self.setFocusPolicy(Qt.StrongFocus)
        self.showMaximized()
        self.set_list()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            # 자동 포인트 지정 기능 토글
            self.auto_adding_points = not self.auto_adding_points
            if self.auto_adding_points:
                # 타이머 시작
                self.auto_add_timer.start(self.auto_add_interval)
            else:
                # 타이머 중지
                self.auto_add_timer.stop()
        elif event.key() == Qt.Key_Shift:
            if self.box.imgB:
                # 이미지 전환 토글
                self.box.is_tempB = not self.box.is_tempB
                if self.box.is_tempB:
                    self.switch_btn.setText('전환 Off')
                else:
                    self.switch_btn.setText('전환 On')
                self.box.repaint()
            else:
                QMessageBox.information(self, "경고", "Temporary B를 먼저 불러오세요")
        elif event.key() == Qt.Key_A:
            # 현재 커서 위치에 왼쪽 클릭 이벤트 시뮬레이션
            pos = self.box.mapFromGlobal(QCursor.pos())
            self.box.is_moving = False
            # 가짜 이벤트 생성
            synthetic_event = QMouseEvent(QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            self.box.mouseReleaseEvent(synthetic_event)
        elif self.auto_switching and (event.key() in [Qt.Key_Plus, Qt.Key_Equal, Qt.Key_Minus]):
            # 자동 전환 간격 조정
            if event.key() in [Qt.Key_Plus, Qt.Key_Equal]:
                # 0.1초 증가
                self.auto_switch_interval += 100
                self.auto_switch_timer.setInterval(self.auto_switch_interval)
            elif event.key() == Qt.Key_Minus:
                # 0.1초 감소, 최소 100ms
                self.auto_switch_interval = max(100, self.auto_switch_interval - 100)
                self.auto_switch_timer.setInterval(self.auto_switch_interval)
        # 숫자 0~6번 키에 따른 클래스 변경 추가
        elif event.key() == Qt.Key_0 or event.key() == Qt.Key_6:
            self.update_class_from_button(6)
        elif event.key() == Qt.Key_1:
            self.update_class_from_button(1)  # 건축물
        elif event.key() == Qt.Key_2:
            self.update_class_from_button(2)  # 도로
        elif event.key() == Qt.Key_3:
            self.update_class_from_button(3)  # 녹지
        elif event.key() == Qt.Key_4:
            self.update_class_from_button(4)  # 산불피해
        elif event.key() == Qt.Key_5:
            self.update_class_from_button(5)  # 수계
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            if not self.box.is_drawing:
                self.undo()
            else:
                # 선 그리기 중일 때는 ImageBox로 이벤트 전달
                self.box.keyPressEvent(event)
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            if not self.box.is_drawing:
                self.redo()
            else:
                # 선 그리기 중일 때는 ImageBox로 이벤트 전달
                self.box.keyPressEvent(event)
        else:
            # ImageBox로 이벤트 전달
            self.box.keyPressEvent(event)

    def add_point_at_cursor(self):
        # 현재 커서 위치에 포인트 추가
        pos = self.box.mapFromGlobal(QCursor.pos())
        self.box.is_moving = False
        # 가짜 이벤트 생성
        synthetic_event = QMouseEvent(QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.box.mouseReleaseEvent(synthetic_event)
        # Undo 스택에 상태 저장
        self.push_undo()

    def update_class_from_button(self, class_number):
        """
        버튼 클릭 시 해당 클래스 번호로 설정하는 함수
        """
        # 0을 입력하면 6으로 처리
        if class_number == 0:
            class_number = 6
        self.box.current_class = class_number
        self.class_input.setText(str(class_number))

    def update_class(self):
        try:
            class_number = int(self.class_input.text())
            # 0을 입력하면 6으로 처리
            if class_number == 0:
                class_number = 6
            self.box.current_class = class_number
        except Exception as e:
            print(f"update_class 오류: {e}")
            QMessageBox.warning(self, "오류", f"유효하지 않은 클래스 번호: {e}")

    def change_switch_btn(self):
        if self.box.imgB:
            # 이미지 A와 B 전환
            self.box.is_tempB = not self.box.is_tempB
            if self.box.is_tempB:
                self.switch_btn.setText('전환 Off')
            else:
                self.switch_btn.setText('전환 On')
            self.box.repaint()
        else:
            QMessageBox.information(self, "경고", "Temporary B를 먼저 불러오세요")

    def auto_switch_dialog(self):
        if not self.auto_switching:
            # 자동 전환 시작
            time, ok = QInputDialog.getDouble(self, '자동 전환', '초를 입력하세요 (s):', decimals=1, min=0.1)
            if ok:
                self.auto_switch_interval = int(time * 1000)
                # 타이머 설정
                self.auto_switch_timer = QTimer()
                self.auto_switch_timer.timeout.connect(self.toggle_image)
                self.auto_switch_timer.start(self.auto_switch_interval)
                self.auto_switching = True
                self.auto_switch_btn.setText('자동 전환 중지')
        else:
            # 자동 전환 중지
            self.auto_switch_timer.stop()
            self.auto_switching = False
            self.auto_switch_btn.setText('자동 전환')

    def toggle_image(self):
        if self.box.imgB:
            self.box.is_tempB = not self.box.is_tempB
            if self.box.is_tempB:
                self.switch_btn.setText('전환 Off')
            else:
                self.switch_btn.setText('전환 On')
            self.box.repaint()
        else:
            # tempB 이미지가 없을 경우 자동 전환 중지
            self.auto_switch_timer.stop()
            self.auto_switching = False
            self.auto_switch_btn.setText('자동 전환')
            QMessageBox.information(self, "경고", "Temporary B를 먼저 불러오세요")

    def start_single_click_timer(self, index):
        # 단일 클릭의 index를 저장하고 타이머 시작
        self.click_index = index
        self.click_timer.start(200)  # 200ms 후에 단일 클릭으로 간주

    def handle_single_click(self):
        # 단일 클릭 시 폴리곤을 강조 표시
        self.select_polygon(self.click_index, double_click=False)
    def handle_double_click(self, index):
        # 더블 클릭 시 폴리곤 생성/소멸 클래스 입력 창 표시
        self.click_timer.stop()  # 단일 클릭 타이머 취소
        self.select_polygon(index, double_click=True)

    def select_polygon(self, index, double_click=False):
        """
        폴리곤 항목을 클릭하여 강조 표시하고, 더블 클릭 시 클래스 번호 수정 창 표시
        """
        try:
            poly_index = index.row()

            # 선택된 폴리곤 인덱스를 저장하여 강조 표시
            self.box.selected_poly_index = poly_index
            self.box.repaint()  # 폴리곤 강조 표시

            if double_click:
                # 더블 클릭 시 생성 및 소멸 클래스 번호 입력 창 표시
                disappear_class, ok1 = QInputDialog.getInt(
                    self, "소멸 클래스 수정", "소멸 클래스 번호 입력 (0~6):", min=0, max=6
                )

                if ok1:
                    # 0을 입력하면 6으로 처리
                    if disappear_class == 0:
                        disappear_class = 6

                    appear_class, ok2 = QInputDialog.getInt(
                        self, "생성 클래스 수정", "생성 클래스 번호 입력 (0~6):", min=0, max=6
                    )

                    if ok2:
                        if appear_class == 0:
                            appear_class = 6
                        # 선택된 폴리곤의 클래스 정보를 소멸, 생성 클래스 번호로 업데이트
                        self.box.poly_list[poly_index]['class'] = (disappear_class, appear_class)

                        # 이미지 라벨 업데이트
                        self.image_labels[self.box.path] = self.box.poly_list.copy()

                        # 화면 업데이트 및 폴리곤 강조 표시
                        self.set_list()
                        self.box.repaint()

        except Exception as e:
            print(f"select_polygon 오류: {e}")
            QMessageBox.warning(self, "오류", f"클래스 수정 실패: {e}")

    def rightMenuShow2(self, point):
        rightMenu = QMenu(self.LV_label)
        removeAction = QAction(u"Delete", self, triggered=self.removepoint)
        rightMenu.addAction(removeAction)
        rightMenu.exec_(self.LV_label.mapToGlobal(point))

    # 수정된 부분: clear_redo 인자 추가, 기본값 True
    def push_undo(self, clear_redo=True):
        # 현재 상태를 undo 스택에 저장
        self.undo_stack.append(self.box.poly_list.copy())
        # redo 스택 비우기 (clear_redo가 True일 때만)
        if clear_redo:
            self.redo_stack.clear()

    def removepoint(self):
        try:
            selected = self.LV_label.selectedIndexes()
            if not selected:
                return
            # 현재 상태를 undo 스택에 저장
            self.push_undo()
            for i in selected:
                self.box.poly_list.pop(i.row())
            self.box.selected_poly_index = -1  # 선택 인덱스 리셋
            self.repaint()
            # 이미지 라벨 업데이트
            self.image_labels[self.box.path] = self.box.poly_list.copy()
        except Exception as e:
            print(f"removepoint 오류: {e}")
            QMessageBox.warning(self, "오류", f"포인트 삭제 실패: {e}")

    def undo(self):
        try:
            if not self.undo_stack:
                QMessageBox.information(self, "Undo", "되돌릴 작업이 없습니다.")
                return
            # 현재 상태를 redo 스택에 저장
            self.redo_stack.append(self.box.poly_list.copy())
            # undo 스택에서 상태 복원
            self.box.poly_list = self.undo_stack.pop()
            self.image_labels[self.box.path] = self.box.poly_list.copy()
            self.box.selected_poly_index = -1  # 선택 인덱스 리셋
            self.repaint()
        except Exception as e:
            print(f"undo 오류: {e}")
            QMessageBox.warning(self, "오류", f"Undo 실패: {e}")

    def redo(self):
        try:
            if not self.redo_stack:
                QMessageBox.information(self, "Redo", "다시 실행할 작업이 없습니다.")
                return
            # 현재 상태를 undo 스택에 저장, redo 시에는 redo_stack을 비우지 않음
            self.push_undo(clear_redo=False)  # 수정된 부분
            # redo 스택에서 상태 복원
            self.box.poly_list = self.redo_stack.pop()
            self.image_labels[self.box.path] = self.box.poly_list.copy()
            self.box.selected_poly_index = -1  # 선택 인덱스 리셋
            self.repaint()
        except Exception as e:
            print(f"redo 오류: {e}")
            QMessageBox.warning(self, "오류", f"Redo 실패: {e}")

    def load_image_pair(self, qModelIndex):
        try:
            index = qModelIndex.row()
            # 인덱스가 두 리스트의 범위 내에 있는지 확인
            if index < len(self.temp_listA) and index < len(self.temp_listB):
                # 현재 라벨 저장
                if self.box.path:
                    self.image_labels[self.box.path] = self.box.poly_list.copy()
                # undo 및 redo 스택 초기화
                self.undo_stack.clear()
                self.redo_stack.clear()

                # 새로운 이미지 경로 설정
                self.box.path = self.temp_listA[index]
                self.box.set_image()

                # 새로운 이미지에 대한 라벨 초기화
                if self.box.path in self.image_labels:
                    self.box.poly_list = self.image_labels[self.box.path].copy()  # 기존 라벨이 있을 경우 복원
                else:
                    self.box.poly_list = []  # 기존 라벨이 없을 경우 초기화
                    self.load_labels_from_file()

                # Temporary B 이미지 설정
                self.selected_b_image_path = self.temp_listB[index]
                try:
                    img_array = np.fromfile(self.selected_b_image_path, np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    height, width, channel = img.shape
                    bytesPerLine = 3 * width
                    qimg = QImage(img, width, height, bytesPerLine, QImage.Format_RGB888)
                    self.box.imgB = QPixmap(qimg)
                except:
                    self.box.imgB = QPixmap(self.selected_b_image_path)

                self.switch_btn.setText('전환 On')
                self.box.is_tempB = False
                self.box.repaint()
                self.set_list()
            else:
                QMessageBox.warning(self, "오류", "Base Image와 Temporary B의 이미지 수가 다릅니다.")
        except Exception as e:
            print(f"load_image_pair 오류: {e}")
            QMessageBox.warning(self, "오류", f"이미지 로드 실패: {e}")

    def openimage(self, flag):
        try:
            # 현재 라벨 저장
            if self.box.path:
                self.image_labels[self.box.path] = self.box.poly_list.copy()
            # undo 및 redo 스택 초기화
            self.undo_stack.clear()
            self.redo_stack.clear()
            imgNames, _ = QFileDialog.getOpenFileNames(self, "파일 선택", "",
                                                      "이미지 파일 (*.png *.jpg *.bmp);;모든 파일 (*)")
            if flag == "A":
                self.temp_listA = imgNames
            else:
                self.temp_listB = imgNames
            self.set_list()
            # 두 리스트 모두 로드되었을 때
            if self.temp_listA and self.temp_listB:
                if len(self.temp_listA) != len(self.temp_listB):
                    QMessageBox.warning(self, "오류", "Base Image와 Temporary B의 이미지 수가 다릅니다.")
                else:
                    # 첫 번째 이미지 쌍 로드
                    self.box.path = self.temp_listA[0]
                    self.box.set_image()
                    if self.box.path in self.image_labels:
                        self.box.poly_list = self.image_labels[self.box.path].copy()
                    else:
                        self.load_labels_from_file()
                    self.selected_b_image_path = self.temp_listB[0]
                    try:
                        img_array = np.fromfile(self.selected_b_image_path, np.uint8)
                        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        height, width, channel = img.shape
                        bytesPerLine = 3 * width
                        qimg = QImage(img, width, height, bytesPerLine, QImage.Format_RGB888)
                        self.box.imgB = QPixmap(qimg)
                    except:
                        self.box.imgB = QPixmap(self.selected_b_image_path)
                    self.switch_btn.setText('전환 On')
                    self.box.is_tempB = False
                    self.box.repaint()
                    self.set_list()
        except Exception as e:
            print(f"openimage 오류: {e}")
            QMessageBox.warning(self, "오류", f"이미지 열기 실패: {e}")

    def savepoint(self):
        try:
            if not self.image_labels:
                QMessageBox.information(self, "경고", "저장할 레이블이 없습니다.")
                return
            for image_path in self.image_labels.keys():
                poly_list = self.image_labels.get(image_path, [])
                (filepath, filename) = os.path.split(image_path)
                csv_filename = os.path.splitext(filename)[0][:-2] + "_Label.csv"
                label_dir = os.path.join(filepath, "label")
                if not os.path.exists(label_dir):
                    os.makedirs(label_dir)

                csv_filepath = os.path.join(label_dir, csv_filename)

                # 병합 로직 없이 현재 poly_list만 저장
                with open(csv_filepath, 'w', encoding='utf_8_sig') as f:
                    for poly_dict in poly_list:
                        class_info = poly_dict['class']

                        # 소멸 및 생성 클래스 저장 (공백으로 구분)
                        if isinstance(class_info, tuple):
                            disappear_class = class_info[0]
                            appear_class = class_info[1]

                            # 클래스 번호 변환
                            disappear_class_save = 6 if disappear_class in (0, 6) else disappear_class
                            appear_class_save = 6 if appear_class in (0, 6) else appear_class

                            f.write(f"{disappear_class_save} {appear_class_save}\n")
                        else:
                            # 단일 클래스인 경우
                            class_save = 6 if class_info in (0, 6) else class_info
                            f.write(f"{class_save}\n")

                        # 좌표 저장
                        points = poly_dict['points']
                        point_str = ','.join(map(str, points))
                        f.write(f"{point_str}\n")

            QMessageBox.information(self, "저장", "성공적으로 저장되었습니다.")
            self.set_list()
        except Exception as e:
            print(f"savepoint 오류: {e}")
            QMessageBox.warning(self, "오류", f"포인트 저장 실패: {e}")


    def load_labels_from_file(self):
        """
        CSV 파일에서 라벨 데이터를 읽어와 poly_list에 저장
        """
        (label_path, filename) = os.path.split(self.box.path)
        csv_filename = os.path.splitext(filename)[0][:-2] + "_Label.csv"
        csv_filepath = os.path.join(label_path, "label", csv_filename)

        if os.path.exists(csv_filepath):
            poly_list = []  # 폴리곤 리스트 초기화

            try:
                with open(csv_filepath, 'r', encoding='utf_8_sig') as f:
                    content = f.readlines()  # 모든 줄 읽기

                i = 0
                while i < len(content):
                    # 클래스 정보 읽기
                    class_info = content[i].strip()
                    i += 1  # 다음 줄로 이동
                    if not class_info:
                        continue  # 빈 줄 건너뛰기

                    # 클래스 정보 파싱
                    class_parts = [
                        int(part.strip()) for part in class_info.replace(',', ' ').split()
                        if part.strip().lstrip('-').isdigit()
                    ]
                    if len(class_parts) == 1:
                        # 단일 클래스
                        class_number = class_parts[0]
                        if class_number == 0:
                            class_number = 6  # 클래스 번호가 0이면 6으로 변환
                    elif len(class_parts) == 2:
                        # 생성/소멸 클래스
                        disappear_class = class_parts[0]
                        appear_class = class_parts[1]
                        disappear_class = 6 if disappear_class == 0 else disappear_class
                        appear_class = 6 if appear_class == 0 else appear_class
                        class_number = (disappear_class, appear_class)
                    else:
                        print(f"유효하지 않은 클래스 정보: {class_info}")
                        continue

                    # 폴리곤 좌표 읽기
                    if i < len(content):
                        points_str = content[i].strip()
                        i += 1  # 다음 줄로 이동
                        if not points_str:
                            continue  # 빈 줄 건너뛰기

                        # 좌표 문자열에서 음수 값을 포함하여 숫자 추출
                        points = [
                            int(coord) for coord in points_str.replace(',', ' ').split()
                            if coord.strip().lstrip('-').isdigit()
                        ]

                        # 좌표 유효성 검사 (최소 2개 이상의 좌표가 있어야 폴리곤이 유효함)
                        if len(points) < 4 or len(points) % 2 != 0:
                            print(f"폴리곤의 좌표 데이터가 올바르지 않습니다: {points}")
                            continue

                        # 유효한 데이터 추가
                        poly_list.append({'points': points, 'class': class_number})

                # poly_list 업데이트
                self.box.poly_list = poly_list
                self.image_labels[self.box.path] = poly_list

            except Exception as e:
                print(f"CSV 파일 읽기 오류: {e}")
                QMessageBox.warning(self, "오류", f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")

    def set_list(self):
        """
        리스트 업데이트 메서드, 선택된 클래스와 폴리곤 좌표 표시
        """
        try:
            # 폴리곤 정보 업데이트
            poly_info = []
            for poly_dict in self.box.poly_list:
                class_info = poly_dict['class']
                points = poly_dict['points']

                if isinstance(class_info, tuple):
                    # 생성/소멸 클래스 번호 처리
                    disappear_class = class_info[0]
                    appear_class = class_info[1]

                    # 클래스 번호 변환
                    if disappear_class == 0 or disappear_class == 6:
                        disappear_class_display = 6
                    else:
                        disappear_class_display = disappear_class

                    if appear_class == 0 or appear_class == 6:
                        appear_class_display = 6
                    else:
                        appear_class_display = appear_class

                    poly_info.append(f"Class {disappear_class_display} Class {appear_class_display}: {points}")
                else:
                    # 클래스 번호가 0 또는 6이면 6으로 표시
                    if class_info == 0 or class_info == 6:
                        class_display = 6
                    else:
                        class_display = class_info
                    poly_info.append(f"Class {class_display}: {points}")

            # Base Image와 Temporary B 리스트 굵게 표시 적용
            self.LV_A.setModel(self.create_bold_model(self.temp_listA, self.box.path))
            self.LV_B.setModel(self.create_bold_model(self.temp_listB, self.selected_b_image_path))
            self.LV_label.setModel(QStringListModel(poly_info))

        except Exception as e:
            print(f"set_list 오류: {e}")

    def create_bold_model(self, file_list, selected_file):
        """
        리스트에서 선택된 파일을 굵게 처리하는 모델 생성
        """
        model = QStandardItemModel()
        for file in file_list:
            item = QStandardItem(file)
            if file == selected_file:
                # 굵게 표시
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            model.appendRow(item)
        return model

    def repaint(self):
        self.box.repaint()
        self.set_list()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', '정말 종료하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.auto_switching:
                self.auto_switch_timer.stop()
            if self.auto_adding_points:
                self.auto_add_timer.stop()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = change_detection()
    win.show()
    win.setFocus()
    sys.exit(app.exec_())
