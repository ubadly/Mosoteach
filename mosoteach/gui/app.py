"""
慕课堂助手GUI界面
"""

import os
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                            QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QLineEdit,
                            QStackedWidget, QListWidget, QMessageBox,
                            QFrame, QSizePolicy, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor
from qt_material import apply_stylesheet

from mosoteach.core.moso import Loginer, LoginError, Course
from mosoteach.utils.tools import setup_logging

setup_logging()

class StyledFrame(QFrame):
    """自定义样式的框架"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            StyledFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)

class LoginWidget(QWidget):
    """登录界面"""
    login_success = pyqtSignal(object)  # 登录成功信号，传递cookies

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 创建登录框架
        login_frame = StyledFrame()
        login_frame.setMaximumWidth(240)  # 限制最大宽度
        login_frame.setFixedHeight(180)    # 固定高度
        login_layout = QVBoxLayout(login_frame)
        login_layout.setSpacing(8)
        login_layout.setContentsMargins(12, 12, 12, 12)
        
        # 标题
        title = QLabel("蓝墨云班课助手")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2196F3; margin-bottom: 8px;")
        login_layout.addWidget(title)
        
        # 账号输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("手机号/邮箱")
        self.username_input.setFixedWidth(200)
        self.username_input.setFixedHeight(28)
        self.username_input.returnPressed.connect(self.handle_login)
        login_layout.addWidget(self.username_input, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(200)
        self.password_input.setFixedHeight(28)
        self.password_input.returnPressed.connect(self.handle_login)
        login_layout.addWidget(self.password_input, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setFixedWidth(80)
        self.login_button.setFixedHeight(28)
        self.login_button.clicked.connect(self.handle_login)
        
        # 按钮容器用于居中显示
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(self.login_button)
        button_container.addStretch()
        login_layout.addLayout(button_container)
        
        # 设置样式
        self.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                color: white;
                padding: 4px 8px;
                font-size: 12px;
                margin-bottom: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 12px;
                margin-top: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #455A64;
                color: #B0BEC5;
            }
        """)
        
        # 创建一个水平布局来居中显示登录框
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(login_frame)
        center_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return

        try:
            self.login_button.setEnabled(False)
            self.login_button.setText("登录中...")
            
            login_client = Loginer(username, password)
            login_client.login
            cookies = login_client.get_cookies
            self.login_success.emit(cookies)
        except LoginError as e:
            QMessageBox.critical(self, "登录失败", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生未知错误: {str(e)}")
        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("登录")


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.moso = None  # 初始化为None
        
        # 设置窗口属性
        self.setWindowTitle('蓝墨云班课助手')
        self.setGeometry(100, 100, 400, 300)  # 设置初始大小
        self.setMinimumSize(400, 300)  # 设置最小尺寸
        self.center_window()  # 居中窗口
        
        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 创建登录页面
        self.login_widget = LoginWidget()
        self.login_widget.login_success.connect(self.handle_login_success)
        self.stacked_widget.addWidget(self.login_widget)
        
        # 创建主内容页面
        self.content_widget = ContentWidget()
        self.stacked_widget.addWidget(self.content_widget)
        
        # 应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #263238;
            }
        """)
        
    def center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
    def handle_login_success(self, cookies):
        """处理登录成功后的操作"""
        self.moso = Course(cookies)
        self.content_widget.moso = self.moso  # 传递moso对象给ContentWidget
        self.setGeometry(100, 100, 1000, 800)  # 调整窗口大小
        self.setMinimumSize(800, 600)  # 设置最小尺寸
        self.center_window()  # 重新居中
        self.stacked_widget.setCurrentWidget(self.content_widget)  # 切换到主界面
        self.content_widget.refresh_courses()  # 刷新课程列表

    def toggle_select_all(self):
        all_selected = True
        for i in range(self.content_widget.resource_list.count()):
            if not self.content_widget.resource_list.item(i).isSelected():
                all_selected = False
                break
        
        for i in range(self.content_widget.resource_list.count()):
            self.content_widget.resource_list.item(i).setSelected(not all_selected)
        
        self.content_widget.select_all_button.setText('取消全选' if not all_selected else '全选')

    def brush_resources(self):
        selected_items = self.content_widget.resource_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请选择要刷课的资源")
            return
            
        try:
            self.content_widget.brush_button.setEnabled(False)
            self.content_widget.brush_button.setText("刷课中...")
            
            total = len(selected_items)
            completed = 0
            
            for item in selected_items:
                resource = item.data(Qt.ItemDataRole.UserRole)
                if resource:
                    try:
                        course_id = resource.get('course_id')
                        self.moso.complete_resource(course_id, resource)
                        completed += 1
                        item.setText(f"✓ {item.text()}")  # 添加完成标记
                        QApplication.processEvents()  # 更新UI
                    except Exception as e:
                        self.logger.error(f"资源完成失败: {str(e)}", exc_info=True)
                        
            if completed == total:
                QMessageBox.information(self, "成功", f"已完成 {completed} 个资源的刷课！")
            else:
                QMessageBox.warning(self, "完成", f"完成 {completed}/{total} 个资源的刷课，部分资源可能失败")
                
        except Exception as e:
            self.logger.error(f"刷课失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"刷课失败: {str(e)}")
        finally:
            self.content_widget.brush_button.setEnabled(True)
            self.content_widget.brush_button.setText("开始刷课")

    def refresh_courses(self):
        """刷新课程列表"""
        try:
            if not self.moso:
                self.logger.error("moso对象未初始化")
                return
                
            self.content_widget.course_list.clear()
            self.content_widget.resource_list.clear()
            self.content_widget.resources_cache.clear()  # 清除资源缓存
            
            courses = self.moso.join_class_list
            if not courses:
                self.logger.warning("未获取到课程列表")
                return
                
            for course in courses:
                if isinstance(course, dict):
                    # 从嵌套的course字典中获取课程信息
                    course_info = course.get('course', {})
                    name = course_info.get('name', 'Unknown')
                    cid = course.get('id', 'Unknown')
                    term = course.get('term_title', '')
                    clazz = course.get('clazz', {}).get('name', '')
                    
                    # 显示课程信息
                    display_text = f"{name}"
                    if term:
                        display_text += f" ({term})"
                    if clazz:
                        display_text += f" - {clazz}"
                    
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, cid)
                    self.content_widget.course_list.addItem(item)
                
        except Exception as e:
            self.logger.error(f"刷新课程失败: {e}", exc_info=True)
            QMessageBox.warning(self, "错误", f"刷新课程失败: {e}")


class ContentWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.moso = None
        self.courses = []
        self.resources_cache = {}  # 保留资源缓存
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # 创建顶部工具栏
        top_frame = StyledFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setSpacing(10)
        
        # 刷新按钮
        self.refresh_button = QPushButton('刷新列表')
        self.refresh_button.setIcon(QIcon.fromTheme('view-refresh'))
        self.refresh_button.clicked.connect(self.refresh_courses)
        top_layout.addWidget(self.refresh_button)
        
        # 添加弹性空间
        top_layout.addStretch()
        
        # 全选按钮（仅用于资源列表）
        self.select_all_button = QPushButton('全选资源')
        self.select_all_button.clicked.connect(self.toggle_select_all)
        top_layout.addWidget(self.select_all_button)
        
        # 刷课按钮
        self.brush_button = QPushButton('开始刷课')
        self.brush_button.clicked.connect(self.brush_resources)
        top_layout.addWidget(self.brush_button)
        
        self.content_layout.addWidget(top_frame)
        
        # 创建列表框架
        list_frame = StyledFrame()
        list_layout = QVBoxLayout(list_frame)
        list_layout.setSpacing(10)
        
        # 课程列表标签
        course_label = QLabel("课程列表：")
        course_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        list_layout.addWidget(course_label)
        
        # 课程列表
        self.course_list = QListWidget()
        self.course_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)  # 设置为单选模式
        self.course_list.currentItemChanged.connect(self.handle_course_selection)  # 使用currentItemChanged信号
        self.course_list.setMinimumHeight(200)
        self.course_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QListWidget::item {
                color: white;
                padding: 6px;
                margin: 2px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: rgba(33, 150, 243, 0.6);
                border: none;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        list_layout.addWidget(self.course_list)
        
        # 资源列表标签
        resource_label = QLabel("资源列表（按住Ctrl多选）：")
        resource_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        list_layout.addWidget(resource_label)
        
        # 资源列表
        self.resource_list = QListWidget()
        self.resource_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # 资源列表保持多选
        self.resource_list.setMinimumHeight(300)
        self.resource_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QListWidget::item {
                color: white;
                padding: 6px;
                margin: 2px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: rgba(33, 150, 243, 0.6);
                border: none;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        list_layout.addWidget(self.resource_list)
        
        self.content_layout.addWidget(list_frame)

    def handle_course_selection(self, current, previous):
        """处理课程选择"""
        if not current:
            self.resource_list.clear()
            return

        course_id = current.data(Qt.ItemDataRole.UserRole)
        course_name = current.text()

        # 检查缓存
        if course_id not in self.resources_cache:
            try:
                # 显示加载提示
                self.resource_list.clear()
                loading_item = QListWidgetItem("正在加载资源...")
                loading_item.setFlags(loading_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                loading_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.resource_list.addItem(loading_item)
                
                # 禁用刷课和全选按钮
                self.brush_button.setEnabled(False)
                self.select_all_button.setEnabled(False)
                
                # 更新UI
                QApplication.processEvents()
                
                # 加载资源
                resources = self.moso.get_resources(course_id)
                self.resources_cache[course_id] = resources

            except Exception as e:
                self.logger.error(f"加载资源失败: {e}")
                QMessageBox.warning(self, "错误", f"加载资源失败: {e}")
                return
            finally:
                # 恢复按钮状态
                self.brush_button.setEnabled(True)
                self.select_all_button.setEnabled(True)

        # 显示资源
        self.resource_list.clear()
        resources = self.resources_cache.get(course_id, [])
        
        if resources:
            for resource in resources:
                resource_item = QListWidgetItem(f"{resource['name']}（{resource['type']}）")
                resource_item.setData(Qt.ItemDataRole.UserRole, resource)
                self.resource_list.addItem(resource_item)
        else:
            empty_item = QListWidgetItem("暂无可刷课的资源")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.resource_list.addItem(empty_item)

    def toggle_select_all(self):
        all_selected = True
        for i in range(self.resource_list.count()):
            if not self.resource_list.item(i).isSelected():
                all_selected = False
                break
        
        for i in range(self.resource_list.count()):
            self.resource_list.item(i).setSelected(not all_selected)
        
        self.select_all_button.setText('取消全选' if not all_selected else '全选')

    def brush_resources(self):
        selected_items = self.resource_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请选择要刷课的资源")
            return
            
        try:
            self.brush_button.setEnabled(False)
            self.brush_button.setText("刷课中...")
            
            total = len(selected_items)
            completed = 0
            
            for item in selected_items:
                resource = item.data(Qt.ItemDataRole.UserRole)
                if resource:
                    try:
                        course_id = resource.get('course_id')
                        self.moso.complete_resource(course_id, resource)
                        completed += 1
                        item.setText(f"✓ {item.text()}")  # 添加完成标记
                        QApplication.processEvents()  # 更新UI
                    except Exception as e:
                        self.logger.error(f"资源完成失败: {str(e)}", exc_info=True)
                        
            if completed == total:
                QMessageBox.information(self, "成功", f"已完成 {completed} 个资源的刷课！")
            else:
                QMessageBox.warning(self, "完成", f"完成 {completed}/{total} 个资源的刷课，部分资源可能失败")
                
        except Exception as e:
            self.logger.error(f"刷课失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"刷课失败: {str(e)}")
        finally:
            self.brush_button.setEnabled(True)
            self.brush_button.setText("开始刷课")

    def refresh_courses(self):
        """刷新课程列表"""
        try:
            if not self.moso:
                self.logger.error("moso对象未初始化")
                return
                
            self.course_list.clear()
            self.resource_list.clear()
            self.resources_cache.clear()  # 清除资源缓存
            
            courses = self.moso.join_class_list
            if not courses:
                self.logger.warning("未获取到课程列表")
                return
                
            for course in courses:
                if isinstance(course, dict):
                    # 从嵌套的course字典中获取课程信息
                    course_info = course.get('course', {})
                    name = course_info.get('name', 'Unknown')
                    cid = course.get('id', 'Unknown')
                    term = course.get('term_title', '')
                    clazz = course.get('clazz', {}).get('name', '')
                    
                    # 显示课程信息
                    display_text = f"{name}"
                    if term:
                        display_text += f" ({term})"
                    if clazz:
                        display_text += f" - {clazz}"
                    
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, cid)
                    self.course_list.addItem(item)
                
        except Exception as e:
            self.logger.error(f"刷新课程失败: {e}", exc_info=True)
            QMessageBox.warning(self, "错误", f"刷新课程失败: {e}")


def run_gui():
    """运行GUI应用"""
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MainWindow()
    window.show()
    return app.exec()

def start_gui():
    """启动图形界面（兼容旧版本）"""
    return run_gui()

if __name__ == "__main__":
    sys.exit(run_gui())
