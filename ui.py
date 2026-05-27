# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
主界面模块
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit, QMessageBox,
    QSpinBox, QDateEdit, QHeaderView, QMenu, QAction, QStatusBar,
    QToolBar, QDockWidget, QFrame, QGridLayout, QGroupBox, QSplitter,
    QWizard, QWizardPage, QListWidget, QListWidgetItem, QCalendarWidget,
    QProgressBar, QDialogButtonBox, QDoubleSpinBox, QRadioButton
)
from PyQt5.QtCore import Qt, QTimer, QDate, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette

import config
from database import init_database, get_db, backup_database
from auth import UserAuth, UserManager, Permission
from equipment import EquipmentManager
from inout import InOutManager
from inventory import InventoryManager
from report import ReportManager
from logger import Logger, log_info, log_operation


class LoginDialog(QDialog):
    """登录对话框"""

    def __init__(self):
        super().__init__()
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("校园体育器材出入库管理系统 - 登录")
        self.setFixedSize(620, 420)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 35, 50, 35)
        layout.setSpacing(22)

        title = QLabel("校园体育器材出入库管理系统")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1890ff;")
        layout.addWidget(title)

        subtitle = QLabel("Equipment Management System")
        subtitle.setFont(QFont("Microsoft YaHei", 13))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #86909c;")
        layout.addWidget(subtitle)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setSpacing(18)

        label_font = QFont("Microsoft YaHei", 14)

        username_label = QLabel("用户名:")
        username_label.setFont(label_font)
        username_label.setStyleSheet("color: #2c3e50;")

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setFixedHeight(42)
        self.username_edit.setFixedWidth(230)
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 15px;
                font-family: Microsoft YaHei;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1890ff;
                outline: none;
            }
        """)
        form_layout.addRow(username_label, self.username_edit)

        password_label = QLabel("密  码:")
        password_label.setFont(label_font)
        password_label.setStyleSheet("color: #2c3e50;")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setFixedHeight(42)
        self.password_edit.setFixedWidth(230)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 15px;
                font-family: Microsoft YaHei;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1890ff;
                outline: none;
            }
        """)
        form_layout.addRow(password_label, self.password_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(22)

        self.login_btn = QPushButton("登 录")
        self.login_btn.setFixedHeight(44)
        self.login_btn.setFixedWidth(130)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                font-family: Microsoft YaHei;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """)
        self.login_btn.clicked.connect(self.do_login)

        self.cancel_btn = QPushButton("取 消")
        self.cancel_btn.setFixedHeight(44)
        self.cancel_btn.setFixedWidth(130)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 15px;
                font-family: Microsoft YaHei;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        register_label = QLabel("首次使用请使用管理员账号: admin / admin123")
        register_label.setAlignment(Qt.AlignCenter)
        register_label.setStyleSheet("color: #94a3b8; font-size: 12px; font-family: Microsoft YaHei;")
        layout.addWidget(register_label)

        self.setLayout(layout)

        self.username_edit.returnPressed.connect(self.do_login)
        self.password_edit.returnPressed.connect(self.do_login)

    def do_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return

        user, msg = UserAuth.login(username, password)
        if user:
            self.current_user = user
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", msg)

    def get_user(self):
        return self.current_user


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self.init_ui()
        self.apply_styles()
        self.load_dashboard_data()

        if user['role'] == 'admin':
            self.init_admin_menu()

        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 15px;
                font-weight: bold;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
            QPushButton[role="danger"] {
                background-color: #ff4d4f;
            }
            QPushButton[role="danger"]:hover {
                background-color: #ff7875;
            }
            QPushButton[role="success"] {
                background-color: #52c41a;
            }
            QPushButton[role="success"]:hover {
                background-color: #73d13d;
            }
            QLabel {
                font-size: 13px;
            }
            QLabel[role="title"] {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            QLabel[role="subtitle"] {
                font-size: 14px;
                color: #666;
            }
            QLabel[role="info"] {
                font-size: 24px;
                font-weight: bold;
                color: #1890ff;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e6f7ff;
            }
            QHeaderView::section {
                background-color: #fafafa;
                padding: 8px;
                border: none;
                border-right: 1px solid #f0f0f0;
                border-bottom: 1px solid #f0f0f0;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                background-color: #fafafa;
                border: 1px solid #e8e8e8;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1890ff;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 6px 10px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                border-color: #40a9ff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QStatusBar {
                background-color: #fafafa;
            }
        """)

    def init_ui(self):
        self.setWindowTitle(f"校园体育器材出入库管理系统 - {self.current_user['real_name']}({self.current_user['role']})")
        self.setMinimumSize(1200, 800)

        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_central_widget()

    def create_menu_bar(self):
        menubar = self.menuBar()

        system_menu = menubar.addMenu("系统管理")

        if self.current_user['role'] == 'admin':
            user_management_action = QAction("用户管理", self)
            user_management_action.triggered.connect(self.show_user_management)
            system_menu.addAction(user_management_action)

            backup_action = QAction("数据备份", self)
            backup_action.triggered.connect(self.do_backup)
            system_menu.addAction(backup_action)

            restore_action = QAction("恢复数据", self)
            restore_action.triggered.connect(self.show_restore_dialog)
            system_menu.addAction(restore_action)

            system_menu.addSeparator()

        change_password_action = QAction("修改密码", self)
        change_password_action.triggered.connect(self.show_change_password)
        system_menu.addAction(change_password_action)

        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self.logout)
        system_menu.addAction(logout_action)

        equipment_menu = menubar.addMenu("器材管理")
        equipment_list_action = QAction("器材列表", self)
        equipment_list_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        equipment_menu.addAction(equipment_list_action)

        if self.current_user['role'] == 'admin':
            add_equipment_action = QAction("添加器材", self)
            add_equipment_action.triggered.connect(self.show_add_equipment)
            equipment_menu.addAction(add_equipment_action)

        inventory_menu = menubar.addMenu("库存管理")
        inventory_action = QAction("库存查询", self)
        inventory_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        inventory_menu.addAction(inventory_action)

        if self.current_user['role'] == 'admin':
            check_action = QAction("库存盘点", self)
            check_action.triggered.connect(self.show_inventory_check)
            inventory_menu.addAction(check_action)

        record_menu = menubar.addMenu("出入库管理")
        stock_in_action = QAction("器材入库", self)
        stock_in_action.triggered.connect(self.show_stock_in)
        record_menu.addAction(stock_in_action)

        stock_out_action = QAction("器材出库", self)
        stock_out_action.triggered.connect(self.show_stock_out)
        record_menu.addAction(stock_out_action)

        record_list_action = QAction("出入库记录", self)
        record_list_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        record_menu.addAction(record_list_action)

        report_menu = menubar.addMenu("报表统计")
        dashboard_action = QAction("数据面板", self)
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        report_menu.addAction(dashboard_action)

        statistics_action = QAction("统计报表", self)
        statistics_action.triggered.connect(self.show_statistics)
        report_menu.addAction(statistics_action)

        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于系统", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setFixedHeight(50)
        self.addToolBar(toolbar)

        if self.current_user['role'] == 'admin':
            add_eq_btn = QPushButton("添加器材")
            add_eq_btn.clicked.connect(self.show_add_equipment)
            toolbar.addWidget(add_eq_btn)

            check_btn = QPushButton("库存盘点")
            check_btn.clicked.connect(self.show_inventory_check)
            toolbar.addWidget(check_btn)

        toolbar.addSeparator()

        stock_in_btn = QPushButton("入库登记")
        stock_in_btn.clicked.connect(self.show_stock_in)
        toolbar.addWidget(stock_in_btn)

        stock_out_btn = QPushButton("出库登记")
        stock_out_btn.clicked.connect(self.show_stock_out)
        toolbar.addWidget(stock_out_btn)

        toolbar.addSeparator()

        refresh_btn = QPushButton("刷新数据")
        refresh_btn.clicked.connect(self.load_dashboard_data)
        toolbar.addWidget(refresh_btn)

    def create_status_bar(self):
        self.statusBar().showMessage("就绪")

    def create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        self.dashboard_tab = self.create_dashboard_tab()
        self.equipment_tab = self.create_equipment_tab()
        self.inventory_tab = self.create_inventory_tab()
        self.record_tab = self.create_record_tab()

        self.tab_widget.addTab(self.dashboard_tab, "数据面板")
        self.tab_widget.addTab(self.equipment_tab, "器材管理")
        self.tab_widget.addTab(self.inventory_tab, "库存管理")
        self.tab_widget.addTab(self.record_tab, "出入库记录")

        main_layout.addWidget(self.tab_widget)
        central_widget.setLayout(main_layout)

    def create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
                padding: 0;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        
        total_rows = len(config.EQUIPMENT_TYPES) + 1
        for row in range(total_rows):
            grid.setRowStretch(row, 1)

        header_cell_style = """
            QWidget {
                border-bottom: 2px solid #e0e0e0;
                border-right: 1px solid #f0f0f0;
            }
            QLabel {
                font-family: Microsoft YaHei, PingFang SC;
                font-size: 28px;
                font-weight: 600;
                color: #555;
                padding: 18px 0;
            }
        """
        
        data_cell_style = """
            QWidget {
                border-bottom: 1px solid #f0f0f0;
                border-right: 1px solid #f0f0f0;
            }
        """

        name_h = QLabel("器材类型")
        name_h.setStyleSheet("""
            QLabel {
                font-family: Microsoft YaHei, PingFang SC;
                font-size: 28px;
                font-weight: 600;
                color: #555;
                padding: 18px 0;
            }
        """)
        name_h.setAlignment(Qt.AlignCenter)
        header_widget = QWidget()
        header_widget.setStyleSheet(header_cell_style)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(name_h)
        grid.addWidget(header_widget, 0, 0)
        
        asset_h = QLabel("资产总数")
        asset_h.setStyleSheet("""
            QLabel {
                font-family: Microsoft YaHei, PingFang SC;
                font-size: 28px;
                font-weight: 600;
                color: #555;
                padding: 18px 0;
            }
        """)
        asset_h.setAlignment(Qt.AlignCenter)
        header_widget = QWidget()
        header_widget.setStyleSheet(header_cell_style)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(asset_h)
        grid.addWidget(header_widget, 0, 1)
        
        stock_h = QLabel("库存数量")
        stock_h.setStyleSheet("""
            QLabel {
                font-family: Microsoft YaHei, PingFang SC;
                font-size: 28px;
                font-weight: 600;
                color: #555;
                padding: 18px 0;
            }
        """)
        stock_h.setAlignment(Qt.AlignCenter)
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                border-bottom: 2px solid #e0e0e0;
            }
        """)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(stock_h)
        grid.addWidget(header_widget, 0, 2)

        self.type_labels = {}
        self.type_asset_labels = {}
        for i, (type_code, type_name) in enumerate(config.EQUIPMENT_TYPES):
            row = i + 1

            name_label = QLabel(type_name)
            name_label.setStyleSheet("""
                QLabel {
                    font-family: Microsoft YaHei, PingFang SC;
                    font-size: 26px;
                    color: #333;
                    padding: 18px 5px;
                }
            """)
            name_label.setAlignment(Qt.AlignCenter)
            cell_widget = QWidget()
            if i == len(config.EQUIPMENT_TYPES) - 1:
                cell_widget.setStyleSheet("""
                    QWidget {
                        border-right: 1px solid #f0f0f0;
                    }
                """)
            else:
                cell_widget.setStyleSheet(data_cell_style)
            cell_layout = QVBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.addWidget(name_label)
            grid.addWidget(cell_widget, row, 0)

            asset_label = QLabel("0")
            asset_label.setStyleSheet("""
                QLabel {
                    font-family: Microsoft YaHei, PingFang SC;
                    font-size: 26px;
                    font-weight: 600;
                    color: #1890ff;
                    padding: 18px 5px;
                }
                QLabel:hover {
                    color: #40a9ff;
                    cursor: pointer;
                    text-decoration: underline;
                }
            """)
            asset_label.setAlignment(Qt.AlignCenter)
            asset_label.mousePressEvent = lambda event, t=type_code, n=type_name: self.show_specification_detail(t, n, 'asset')
            self.type_asset_labels[type_code] = asset_label
            cell_widget = QWidget()
            if i == len(config.EQUIPMENT_TYPES) - 1:
                cell_widget.setStyleSheet("""
                    QWidget {
                        border-right: 1px solid #f0f0f0;
                    }
                """)
            else:
                cell_widget.setStyleSheet(data_cell_style)
            cell_layout = QVBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.addWidget(asset_label)
            grid.addWidget(cell_widget, row, 1)

            stock_label = QLabel("0")
            stock_label.setStyleSheet("""
                QLabel {
                    font-family: Microsoft YaHei, PingFang SC;
                    font-size: 26px;
                    font-weight: 600;
                    color: #52c41a;
                    padding: 18px 5px;
                }
                QLabel:hover {
                    color: #73d13d;
                    cursor: pointer;
                    text-decoration: underline;
                }
            """)
            stock_label.setAlignment(Qt.AlignCenter)
            stock_label.mousePressEvent = lambda event, t=type_code, n=type_name: self.show_specification_detail(t, n, 'stock')
            self.type_labels[type_code] = stock_label
            cell_widget = QWidget()
            cell_widget.setStyleSheet("")
            cell_layout = QVBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.addWidget(stock_label)
            grid.addWidget(cell_widget, row, 2)

        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        card_layout.addWidget(grid_widget)

        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(30, 30, 30, 30)
        wrapper_layout.addWidget(card)
        wrapper_layout.addStretch()
        layout.addWidget(wrapper)

        widget.setLayout(layout)
        return widget

    def create_equipment_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title = QLabel("器材信息管理")
        title.setProperty("role", "title")
        title_layout.addWidget(title)
        title_layout.addStretch()

        if self.current_user['role'] == 'admin':
            add_btn = QPushButton("添加器材")
            add_btn.clicked.connect(self.show_add_equipment)
            title_layout.addWidget(add_btn)

        layout.addLayout(title_layout)

        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("类型:"))
        self.equipment_type_combo = QComboBox()
        self.equipment_type_combo.addItem("全部", "")
        for type_code, type_name in config.EQUIPMENT_TYPES:
            self.equipment_type_combo.addItem(type_name, type_code)
        search_layout.addWidget(self.equipment_type_combo)

        search_layout.addWidget(QLabel("关键词:"))
        self.equipment_search_edit = QLineEdit()
        self.equipment_search_edit.setPlaceholderText("输入编号或名称搜索")
        self.equipment_search_edit.setFixedWidth(200)
        search_layout.addWidget(self.equipment_search_edit)

        search_btn = QPushButton("查询")
        search_btn.clicked.connect(self.search_equipment)
        search_layout.addWidget(search_btn)

        export_btn = QPushButton("导出")
        export_btn.clicked.connect(self.export_equipment)
        search_layout.addWidget(export_btn)

        layout.addLayout(search_layout)

        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(10)
        self.equipment_table.setHorizontalHeaderLabels([
            "ID", "器材编号", "名称", "类型", "规格", "数量", "单位",
            "采购日期", "供应商", "操作"
        ])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.cellClicked.connect(self.on_equipment_cell_clicked)
        layout.addWidget(self.equipment_table)

        self.equipment_pager = QHBoxLayout()
        self.equipment_page_label = QLabel("第 1 页，共 0 页")
        self.equipment_pager.addWidget(self.equipment_page_label)
        self.equipment_pager.addStretch()

        prev_btn = QPushButton("上一页")
        prev_btn.clicked.connect(lambda: self.load_equipment_page(self.equipment_current_page - 1))
        self.equipment_pager.addWidget(prev_btn)

        next_btn = QPushButton("下一页")
        next_btn.clicked.connect(lambda: self.load_equipment_page(self.equipment_current_page + 1))
        self.equipment_pager.addWidget(next_btn)

        layout.addLayout(self.equipment_pager)

        self.equipment_current_page = 1
        self.equipment_total_page = 1

        widget.setLayout(layout)
        self.load_equipment_data()
        return widget

    def create_inventory_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("库存管理")
        title.setProperty("role", "title")
        layout.addWidget(title)

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels([
            "器材编号", "名称", "类型", "当前库存", "最后更新时间", "操作"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.inventory_table)

        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("刷新库存")
        refresh_btn.clicked.connect(self.load_inventory_data)
        button_layout.addWidget(refresh_btn)

        if self.current_user['role'] == 'admin':
            adjust_btn = QPushButton("库存调整")
            adjust_btn.clicked.connect(self.show_inventory_adjustment)
            button_layout.addWidget(adjust_btn)

        layout.addLayout(button_layout)

        widget.setLayout(layout)
        self.load_inventory_data()
        return widget

    def create_record_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title = QLabel("出入库记录")
        title.setProperty("role", "title")
        title_layout.addWidget(title)
        title_layout.addStretch()

        stock_in_btn = QPushButton("入库登记")
        stock_in_btn.clicked.connect(self.show_stock_in)
        title_layout.addWidget(stock_in_btn)

        stock_out_btn = QPushButton("出库登记")
        stock_out_btn.clicked.connect(self.show_stock_out)
        title_layout.addWidget(stock_out_btn)

        layout.addLayout(title_layout)

        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("类型:"))
        self.record_type_combo = QComboBox()
        self.record_type_combo.addItem("全部", "")
        self.record_type_combo.addItem("入库", "in")
        self.record_type_combo.addItem("出库", "out")
        search_layout.addWidget(self.record_type_combo)

        search_layout.addWidget(QLabel("器材类型:"))
        self.record_equipment_type_combo = QComboBox()
        self.record_equipment_type_combo.addItem("全部", "")
        for type_code, type_name in config.EQUIPMENT_TYPES:
            self.record_equipment_type_combo.addItem(type_name, type_code)
        search_layout.addWidget(self.record_equipment_type_combo)

        search_layout.addWidget(QLabel("日期:"))
        self.record_start_date = QDateEdit()
        self.record_start_date.setCalendarPopup(True)
        self.record_start_date.setDate(QDate.currentDate().addMonths(-1))
        search_layout.addWidget(self.record_start_date)

        search_layout.addWidget(QLabel("至"))
        self.record_end_date = QDateEdit()
        self.record_end_date.setCalendarPopup(True)
        self.record_end_date.setDate(QDate.currentDate())
        search_layout.addWidget(self.record_end_date)

        search_btn = QPushButton("查询")
        search_btn.clicked.connect(self.search_records)
        search_layout.addWidget(search_btn)

        export_btn = QPushButton("导出")
        export_btn.clicked.connect(self.export_records)
        search_layout.addWidget(export_btn)

        layout.addLayout(search_layout)

        self.record_table = QTableWidget()
        self.record_table.setColumnCount(11)
        self.record_table.setHorizontalHeaderLabels([
            "记录编号", "器材编号", "器材名称", "类型", "操作类型",
            "数量", "操作前", "操作后", "操作人", "操作时间", "用途"
        ])
        self.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.record_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.record_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.record_table)

        self.record_pager = QHBoxLayout()
        self.record_page_label = QLabel("第 1 页，共 0 页")
        self.record_pager.addWidget(self.record_page_label)
        self.record_pager.addStretch()

        prev_btn = QPushButton("上一页")
        prev_btn.clicked.connect(lambda: self.load_record_page(self.record_current_page - 1))
        self.record_pager.addWidget(prev_btn)

        next_btn = QPushButton("下一页")
        next_btn.clicked.connect(lambda: self.load_record_page(self.record_current_page + 1))
        self.record_pager.addWidget(next_btn)

        layout.addLayout(self.record_pager)

        self.record_current_page = 1

        widget.setLayout(layout)
        self.load_record_data()
        return widget

    def load_dashboard_data(self):
        try:
            data = ReportManager.get_dashboard_data()

            for type_code, info in data['type_summary'].items():
                if type_code in self.type_labels:
                    self.type_labels[type_code].setText(str(info['quantity']))
                if type_code in self.type_asset_labels:
                    self.type_asset_labels[type_code].setText(str(info['asset_total']))

            self.statusBar().showMessage(f"数据已刷新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            self.statusBar().showMessage(f"数据加载失败: {str(e)}")

    def load_equipment_data(self, page=1):
        try:
            equipment_type = self.equipment_type_combo.currentData()
            keyword = self.equipment_search_edit.text().strip()

            equipments, total = EquipmentManager.get_all_equipments(
                page=page,
                page_size=20,
                equipment_type=equipment_type if equipment_type else None,
                keyword=keyword
            )

            self.equipment_current_page = page
            self.equipment_total_page = (total + 19) // 20 if total > 0 else 1

            self.equipment_table.setRowCount(len(equipments))

            for i, eq in enumerate(equipments):
                self.equipment_table.setItem(i, 0, QTableWidgetItem(str(eq['id'])))
                self.equipment_table.setItem(i, 1, QTableWidgetItem(eq['equipment_code']))
                self.equipment_table.setItem(i, 2, QTableWidgetItem(eq['name']))

                type_name = dict(config.EQUIPMENT_TYPES).get(eq['type'], eq['type'])
                self.equipment_table.setItem(i, 3, QTableWidgetItem(type_name))
                self.equipment_table.setItem(i, 4, QTableWidgetItem(eq['specification'] or ''))
                self.equipment_table.setItem(i, 5, QTableWidgetItem(str(eq['quantity'])))
                self.equipment_table.setItem(i, 6, QTableWidgetItem(eq['unit']))

                purchase_date = eq['purchase_date']
                if purchase_date:
                    if hasattr(purchase_date, 'strftime'):
                        purchase_date = purchase_date.strftime('%Y-%m-%d')
                self.equipment_table.setItem(i, 7, QTableWidgetItem(str(purchase_date) if purchase_date else ''))
                self.equipment_table.setItem(i, 8, QTableWidgetItem(eq['supplier'] or ''))

                # 创建操作按钮
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                action_layout.setSpacing(5)
                
                if self.current_user['role'] == 'admin':
                    # 编辑按钮
                    edit_btn = QPushButton("编辑")
                    edit_btn.setProperty("row", i)
                    edit_btn.setProperty("equipment_id", eq['id'])
                    edit_btn.setProperty("action", "edit")
                    edit_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1890ff;
                            color: white;
                            border: none;
                            padding: 4px 12px;
                            border-radius: 3px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #40a9ff;
                        }
                    """)
                    edit_btn.clicked.connect(lambda _, row=i, eid=eq['id']: self.on_equipment_action(row, eid, "edit"))
                    action_layout.addWidget(edit_btn)
                    
                    # 删除按钮
                    delete_btn = QPushButton("删除")
                    delete_btn.setProperty("row", i)
                    delete_btn.setProperty("equipment_id", eq['id'])
                    delete_btn.setProperty("action", "delete")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #ff4d4f;
                            color: white;
                            border: none;
                            padding: 4px 12px;
                            border-radius: 3px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #ff7875;
                        }
                    """)
                    delete_btn.clicked.connect(lambda _, row=i, eid=eq['id']: self.on_equipment_action(row, eid, "delete"))
                    action_layout.addWidget(delete_btn)
                else:
                    # 查看按钮
                    view_btn = QPushButton("查看")
                    view_btn.setProperty("row", i)
                    view_btn.setProperty("equipment_id", eq['id'])
                    view_btn.setProperty("action", "view")
                    view_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #52c41a;
                            color: white;
                            border: none;
                            padding: 4px 12px;
                            border-radius: 3px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #73d13d;
                        }
                    """)
                    view_btn.clicked.connect(lambda _, row=i, eid=eq['id']: self.on_equipment_action(row, eid, "view"))
                    action_layout.addWidget(view_btn)
                
                action_layout.addStretch()
                self.equipment_table.setCellWidget(i, 9, action_widget)

            self.equipment_page_label.setText(f"第 {page} 页，共 {self.equipment_total_page} 页，总计 {total} 条")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载器材数据失败: {str(e)}")

    def load_equipment_page(self, page):
        if page < 1:
            page = 1
        if page > self.equipment_total_page:
            page = self.equipment_total_page
        self.load_equipment_data(page)

    def search_equipment(self):
        self.load_equipment_data(1)

    def load_inventory_data(self):
        try:
            summary = InventoryManager.get_inventory_summary()
            details = InventoryManager.get_inventory_details()

            self.inventory_table.setRowCount(len(details))

            for i, eq in enumerate(details):
                self.inventory_table.setItem(i, 0, QTableWidgetItem(eq['equipment_code']))
                self.inventory_table.setItem(i, 1, QTableWidgetItem(eq['name']))
                self.inventory_table.setItem(i, 2, QTableWidgetItem(dict(config.EQUIPMENT_TYPES).get(eq['type'], eq['type'])))
                self.inventory_table.setItem(i, 3, QTableWidgetItem(str(eq['quantity'])))
                self.inventory_table.setItem(i, 4, QTableWidgetItem(
                    eq['updated_at'].strftime('%Y-%m-%d %H:%M') if hasattr(eq['updated_at'], 'strftime') else str(eq['updated_at'])[:16]))
                self.inventory_table.setItem(i, 5, QTableWidgetItem("查看详情"))

        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载库存数据失败: {str(e)}")

    def load_record_data(self, page=1):
        try:
            record_type = self.record_type_combo.currentData()
            equipment_type = self.record_equipment_type_combo.currentData()
            
            start_date = self.record_start_date.date().toString("yyyy-MM-dd")
            end_date = self.record_end_date.date().toString("yyyy-MM-dd")
            
            if start_date == "Invalid Date":
                start_date = None
            if end_date == "Invalid Date":
                end_date = None
            
            if end_date:
                end_date = end_date + " 23:59:59"

            records, total = InOutManager.get_records(
                page=page,
                page_size=20,
                record_type=record_type if record_type else None,
                equipment_type=equipment_type if equipment_type else None,
                start_date=start_date if start_date else None,
                end_date=end_date if end_date else None
            )

            self.record_current_page = page
            self.record_total_page = (total + 19) // 20 if total > 0 else 1

            self.record_table.setRowCount(len(records))

            for i, record in enumerate(records):
                self.record_table.setItem(i, 0, QTableWidgetItem(record['record_no']))
                self.record_table.setItem(i, 1, QTableWidgetItem(record['equipment_code']))
                self.record_table.setItem(i, 2, QTableWidgetItem(record['equipment_name']))
                self.record_table.setItem(i, 3, QTableWidgetItem(dict(config.EQUIPMENT_TYPES).get(record['equipment_type'], record['equipment_type'])))
                self.record_table.setItem(i, 4, QTableWidgetItem("入库" if record['record_type'] == 'in' else "出库"))
                self.record_table.setItem(i, 5, QTableWidgetItem(str(record['quantity'])))
                self.record_table.setItem(i, 6, QTableWidgetItem(str(record['before_quantity'])))
                self.record_table.setItem(i, 7, QTableWidgetItem(str(record['after_quantity'])))
                self.record_table.setItem(i, 8, QTableWidgetItem(record['operator_name']))
                self.record_table.setItem(i, 9, QTableWidgetItem(
                    record['operate_time'].strftime('%Y-%m-%d %H:%M') if hasattr(record['operate_time'], 'strftime') else str(record['operate_time'])[:16]))
                self.record_table.setItem(i, 10, QTableWidgetItem(record['purpose'] or ''))

            self.record_page_label.setText(f"第 {page} 页，共 {self.record_total_page} 页，总计 {total} 条")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载记录数据失败: {str(e)}")

    def load_record_page(self, page):
        if page < 1:
            page = 1
        if page > self.record_total_page:
            page = self.record_total_page
        self.load_record_data(page)

    def search_records(self):
        self.load_record_data(1)

    def show_add_equipment(self):
        dialog = AddEquipmentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_equipment_data(1)
            self.load_inventory_data()
            self.load_dashboard_data()

    def on_equipment_cell_clicked(self, row, col):
        # 这里可以处理单元格点击，但我们已经直接在按钮上绑定了事件
        pass

    def on_equipment_action(self, row, equipment_id, action):
        if action == "edit":
            self.edit_equipment_by_id(equipment_id)
        elif action == "delete":
            self.delete_equipment_by_id(equipment_id)
        elif action == "view":
            self.view_equipment(equipment_id)

    def edit_equipment_by_id(self, equipment_id):
        dialog = EditEquipmentDialog(self, equipment_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_equipment_data(self.equipment_current_page)

    def delete_equipment_by_id(self, equipment_id):
        reply = QMessageBox.question(self, "确认", "确定要删除该器材吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = EquipmentManager.delete_equipment(equipment_id, self.current_user['id'])
            if success:
                QMessageBox.information(self, "成功", msg)
                self.load_equipment_data(self.equipment_current_page)
            else:
                QMessageBox.warning(self, "失败", msg)

    def view_equipment(self, equipment_id):
        try:
            equipment = EquipmentManager.get_equipment_by_id(equipment_id)
            if not equipment:
                QMessageBox.warning(self, "错误", "未找到该器材")
                return
            
            type_name = dict(config.EQUIPMENT_TYPES).get(equipment['type'], equipment['type'])
            info_text = f"""器材编号: {equipment['equipment_code']}
器材名称: {equipment['name']}
器材类型: {type_name}
规格: {equipment['specification'] or '-'}
数量: {equipment['quantity']} {equipment['unit']}
采购日期: {str(equipment['purchase_date'] or '-')}
供应商: {equipment['supplier'] or '-'}"""
            QMessageBox.information(self, "器材详情", info_text)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"查看器材信息失败: {str(e)}")

    def edit_equipment(self):
        row = self.equipment_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请选择要编辑的器材")
            return

        equipment_id = int(self.equipment_table.item(row, 0).text())
        dialog = EditEquipmentDialog(self, equipment_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_equipment_data(self.equipment_current_page)

    def delete_equipment(self):
        row = self.equipment_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请选择要删除的器材")
            return

        reply = QMessageBox.question(self, "确认", "确定要删除该器材吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            equipment_id = int(self.equipment_table.item(row, 0).text())
            success, msg = EquipmentManager.delete_equipment(equipment_id, self.current_user['id'])
            if success:
                QMessageBox.information(self, "成功", msg)
                self.load_equipment_data(self.equipment_current_page)
            else:
                QMessageBox.warning(self, "失败", msg)

    def show_stock_in(self):
        dialog = StockInDialog(self, self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            self.load_dashboard_data()
            self.load_inventory_data()
            self.load_record_data(1)

    def show_stock_out(self):
        dialog = StockOutDialog(self, self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            self.load_dashboard_data()
            self.load_inventory_data()
            self.load_record_data(1)

    def show_inventory_check(self):
        dialog = InventoryCheckDialog(self, self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            self.load_inventory_data()
            self.load_dashboard_data()

    def show_inventory_adjustment(self):
        dialog = InventoryAdjustmentDialog(self, self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            self.load_inventory_data()
            self.load_dashboard_data()

    def show_user_management(self):
        dialog = UserManagementDialog(self)
        dialog.exec_()

    def show_change_password(self):
        dialog = ChangePasswordDialog(self, self.current_user)
        dialog.exec_()

    def show_statistics(self):
        dialog = StatisticsDialog(self)
        dialog.exec_()

    def show_about(self):
        QMessageBox.about(self, "关于",
                         "校园体育器材出入库管理系统\n\n"
                         f"版本: {config.APP_VERSION}\n"
                         f"作者: {config.APP_AUTHOR}\n\n"
                         "用于管理篮球、排球、羽毛球拍、乒乓球拍、网球拍等体育器材的出入库")

    def export_equipment(self):
        try:
            filepath = ReportManager.export_equipment_report()
            if filepath:
                QMessageBox.information(self, "成功", f"器材报表已导出:\n{filepath}")
            else:
                QMessageBox.warning(self, "失败", "导出失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")

    def export_records(self):
        try:
            record_type = self.record_type_combo.currentData()
            equipment_type = self.record_equipment_type_combo.currentData()
            start_date = self.record_start_date.date().toString("yyyy-MM-dd")
            end_date = self.record_end_date.date().toString("yyyy-MM-dd")

            filepath = ReportManager.export_record_report(
                record_type=record_type if record_type else None,
                equipment_type=equipment_type if equipment_type else None,
                start_date=start_date,
                end_date=end_date
            )
            if filepath:
                QMessageBox.information(self, "成功", f"出入库记录已导出:\n{filepath}")
            else:
                QMessageBox.warning(self, "失败", "导出失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")

    def do_backup(self):
        try:
            filepath = backup_database()
            if filepath:
                QMessageBox.information(self, "成功", f"数据备份成功:\n{filepath}")
            else:
                QMessageBox.warning(self, "失败", "备份失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"备份失败: {str(e)}")

    def show_restore_dialog(self):
        from PyQt5.QtWidgets import QFileDialog
        import os

        try:
            backup_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择备份文件",
                config.BACKUP_DIR,
                "数据库备份文件 (*.db)"
            )

            if not backup_path:
                return

            backup_filename = os.path.basename(backup_path)

            confirm = QMessageBox.question(self, "确认恢复",
                                        f"确定要从备份文件恢复数据吗？\n\n备份文件: {backup_filename}\n\n注意：恢复后当前数据将被覆盖！",
                                        QMessageBox.Ok | QMessageBox.Cancel)

            if confirm == QMessageBox.Ok:
                from database import restore_database
                success, msg = restore_database(backup_path)

                if success:
                    QMessageBox.information(self, "成功", "数据恢复成功！\n\n请重新启动程序以应用更改。")
                else:
                    QMessageBox.warning(self, "失败", msg)

        except Exception as e:
            QMessageBox.warning(self, "错误", f"恢复数据失败: {str(e)}")

    def show_specification_detail(self, equipment_type, type_name, detail_type):
        details = EquipmentManager.get_specification_details_by_type(equipment_type, detail_type)
        
        if not details:
            QMessageBox.information(self, "规格详情", f"{type_name}暂无规格数据")
            return
        
        dialog = QDialog(self)
        
        if detail_type == 'asset':
            dialog.setWindowTitle(f"{type_name} - 资产总数详情")
            title_text = f"{type_name} 资产总数明细"
            col_name = "资产总数"
        else:
            dialog.setWindowTitle(f"{type_name} - 库存数量详情")
            title_text = f"{type_name} 库存数量明细"
            col_name = "库存数量"
        
        dialog.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;")
        layout.addWidget(title)
        
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["规格", col_name])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(details))
        
        total = 0
        for i, detail in enumerate(details):
            table.setItem(i, 0, QTableWidgetItem(detail['specification'] or '无规格'))
            if detail_type == 'asset':
                table.setItem(i, 1, QTableWidgetItem(str(detail['asset_total'])))
                total += detail['asset_total']
            else:
                table.setItem(i, 1, QTableWidgetItem(str(detail['total_quantity'])))
                total += detail['total_quantity']
        
        table.insertRow(len(details))
        table.setItem(len(details), 0, QTableWidgetItem("合计"))
        table.setItem(len(details), 1, QTableWidgetItem(str(total)))
        
        layout.addWidget(table)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def init_admin_menu(self):
        pass

    def update_time(self):
        self.statusBar().showMessage(
            f"当前用户: {self.current_user['real_name']} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def logout(self):
        reply = QMessageBox.question(self, "确认", "确定要退出登录吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            UserAuth.logout(self.current_user['id'], self.current_user['username'])
            self.close()


class AddEquipmentDialog(QDialog):
    """添加器材对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("添加器材")
        self.setFixedSize(500, 550)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.type_combo = QComboBox()
        for type_code, type_name in config.EQUIPMENT_TYPES:
            self.type_combo.addItem(type_name, type_code)
        form_layout.addRow("器材类型:", self.type_combo)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入器材名称")
        form_layout.addRow("器材名称:", self.name_edit)

        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("留空将自动生成")
        form_layout.addRow("器材编号:", self.code_edit)

        self.spec_edit = QLineEdit()
        self.spec_edit.setPlaceholderText("请输入规格型号")
        form_layout.addRow("规格型号:", self.spec_edit)

        self.unit_edit = QLineEdit()
        self.unit_edit.setText("个")
        form_layout.addRow("单位:", self.unit_edit)

        self.purchase_date_edit = QDateEdit()
        self.purchase_date_edit.setCalendarPopup(True)
        self.purchase_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("采购日期:", self.purchase_date_edit)

        self.supplier_edit = QLineEdit()
        self.supplier_edit.setPlaceholderText("请输入供应商")
        form_layout.addRow("供应商:", self.supplier_edit)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("¥ ")
        form_layout.addRow("采购价格:", self.price_spin)

        self.remarks_edit = QTextEdit()
        self.remarks_edit.setPlaceholderText("请输入备注信息")
        self.remarks_edit.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remarks_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定添加")
        ok_btn.clicked.connect(self.do_add)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.on_type_changed(0)

    def on_type_changed(self, index):
        type_code = self.type_combo.itemData(index)
        self.name_edit.setPlaceholderText(f"请输入{self.type_combo.currentText()}名称")

    def do_add(self):
        type_code = self.type_combo.itemData(self.type_combo.currentIndex())
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()
        spec = self.spec_edit.text().strip()
        unit = self.unit_edit.text().strip()
        purchase_date = self.purchase_date_edit.date().toString("yyyy-MM-dd")
        supplier = self.supplier_edit.text().strip()
        price = self.price_spin.value()
        remarks = self.remarks_edit.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "提示", "请输入器材名称")
            return

        if not code:
            code = EquipmentManager.generate_equipment_code(type_code)

        reply = QMessageBox.question(
            self, "确认", 
            "器材初始数量为0，如需添加库存请使用【入库登记】功能。\n\n确定要添加该器材吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        from database import get_db
        db = get_db()
        current_user = None
        try:
            from PyQt5.QtWidgets import QApplication
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, MainWindow):
                    current_user = widget.current_user
                    break
        except:
            pass

        success, msg = EquipmentManager.add_equipment(
            code, name, type_code, spec, 0, unit,
            purchase_date, supplier, price, remarks,
            current_user['id'] if current_user else 1
        )

        if success:
            QMessageBox.information(self, "成功", "器材添加成功！如需添加库存，请使用【入库登记】功能。")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class EditEquipmentDialog(QDialog):
    """编辑器材对话框"""

    def __init__(self, parent=None, equipment_id=None):
        super().__init__(parent)
        self.equipment_id = equipment_id
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("编辑器材")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        form_layout.addRow("器材名称:", self.name_edit)

        self.spec_edit = QLineEdit()
        form_layout.addRow("规格型号:", self.spec_edit)

        self.supplier_edit = QLineEdit()
        form_layout.addRow("供应商:", self.supplier_edit)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("¥ ")
        form_layout.addRow("采购价格:", self.price_spin)

        self.remarks_edit = QTextEdit()
        self.remarks_edit.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remarks_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("保存")
        ok_btn.clicked.connect(self.do_save)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_data(self):
        equipment = EquipmentManager.get_equipment_by_id(self.equipment_id)
        if equipment:
            self.name_edit.setText(equipment['name'])
            self.spec_edit.setText(equipment['specification'] or '')
            self.supplier_edit.setText(equipment['supplier'] or '')
            self.price_spin.setValue(float(equipment['purchase_price'] or 0))
            self.remarks_edit.setPlainText(equipment['remarks'] or '')

    def do_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入器材名称")
            return

        success, msg = EquipmentManager.update_equipment(
            self.equipment_id,
            name=name,
            specification=self.spec_edit.text().strip(),
            supplier=self.supplier_edit.text().strip(),
            purchase_price=self.price_spin.value(),
            remarks=self.remarks_edit.toPlainText().strip()
        )

        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class StockInDialog(QDialog):
    """入库对话框"""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.current_user = user
        self.init_ui()
        self.load_equipment()

    def init_ui(self):
        self.setWindowTitle("器材入库")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.equipment_combo = QComboBox()
        self.equipment_combo.setMinimumContentsLength(20)
        form_layout.addRow("选择器材:", self.equipment_combo)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 99999)
        self.quantity_spin.setValue(1)
        form_layout.addRow("入库数量:", self.quantity_spin)

        self.purpose_edit = QLineEdit()
        self.purpose_edit.setPlaceholderText("请输入入库用途")
        form_layout.addRow("用途说明:", self.purpose_edit)

        self.remarks_edit = QTextEdit()
        self.remarks_edit.setPlaceholderText("请输入备注信息")
        self.remarks_edit.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remarks_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定入库")
        ok_btn.clicked.connect(self.do_stock_in)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_equipment(self):
        equipments, _ = EquipmentManager.get_all_equipments(status=1)
        for eq in equipments:
            type_name = dict(config.EQUIPMENT_TYPES).get(eq['type'], eq['type'])
            self.equipment_combo.addItem(
                f"{eq['equipment_code']} - {eq['name']} ({type_name}) [库存:{eq['quantity']}]",
                eq['id']
            )

    def do_stock_in(self):
        equipment_id = self.equipment_combo.itemData(self.equipment_combo.currentIndex())
        quantity = self.quantity_spin.value()
        purpose = self.purpose_edit.text().strip()
        remarks = self.remarks_edit.toPlainText().strip()

        if quantity <= 0:
            QMessageBox.warning(self, "提示", "请输入有效的入库数量")
            return

        success, msg = InOutManager.stock_in(
            equipment_id, quantity, purpose, remarks,
            self.current_user['id'], self.current_user['real_name']
        )

        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class StockOutDialog(QDialog):
    """出库对话框"""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.current_user = user
        self.init_ui()
        self.load_equipment()

    def init_ui(self):
        self.setWindowTitle("器材出库")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.equipment_combo = QComboBox()
        self.equipment_combo.setMinimumContentsLength(20)
        self.equipment_combo.currentIndexChanged.connect(self.on_equipment_changed)
        form_layout.addRow("选择器材:", self.equipment_combo)

        self.current_stock_label = QLabel("当前库存: 0")
        form_layout.addRow("", self.current_stock_label)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 99999)
        self.quantity_spin.setValue(1)
        form_layout.addRow("出库数量:", self.quantity_spin)

        self.purpose_edit = QLineEdit()
        self.purpose_edit.setPlaceholderText("请输入出库用途")
        form_layout.addRow("用途说明:", self.purpose_edit)

        self.remarks_edit = QTextEdit()
        self.remarks_edit.setPlaceholderText("请输入备注信息")
        self.remarks_edit.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remarks_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定出库")
        ok_btn.clicked.connect(self.do_stock_out)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_equipment(self):
        equipments, _ = EquipmentManager.get_all_equipments(status=1)
        for eq in equipments:
            type_name = dict(config.EQUIPMENT_TYPES).get(eq['type'], eq['type'])
            self.equipment_combo.addItem(
                f"{eq['equipment_code']} - {eq['name']} ({type_name}) [库存:{eq['quantity']}]",
                eq['id']
            )

        if equipments:
            self.update_stock_label(0)

    def on_equipment_changed(self, index):
        self.update_stock_label(index)

    def update_stock_label(self, index):
        if index >= 0:
            equipment_id = self.equipment_combo.itemData(index)
            equipment = EquipmentManager.get_equipment_by_id(equipment_id)
            if equipment:
                self.current_stock_label.setText(f"当前库存: {equipment['quantity']}")
                self.quantity_spin.setMaximum(equipment['quantity'])

    def do_stock_out(self):
        equipment_id = self.equipment_combo.itemData(self.equipment_combo.currentIndex())
        quantity = self.quantity_spin.value()
        purpose = self.purpose_edit.text().strip()
        remarks = self.remarks_edit.toPlainText().strip()

        if quantity <= 0:
            QMessageBox.warning(self, "提示", "请输入有效的出库数量")
            return

        success, msg = InOutManager.stock_out(
            equipment_id, quantity, purpose, remarks,
            self.current_user['id'], self.current_user['real_name']
        )

        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class InventoryCheckDialog(QDialog):
    """库存盘点对话框"""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.current_user = user
        self.init_ui()
        self.load_equipment()

    def init_ui(self):
        self.setWindowTitle("库存盘点")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.equipment_combo = QComboBox()
        self.equipment_combo.setMinimumContentsLength(20)
        self.equipment_combo.currentIndexChanged.connect(self.on_equipment_changed)
        form_layout.addRow("选择器材:", self.equipment_combo)

        self.system_stock_label = QLabel("系统库存: 0")
        form_layout.addRow("", self.system_stock_label)

        self.actual_quantity_spin = QSpinBox()
        self.actual_quantity_spin.setRange(0, 99999)
        self.actual_quantity_spin.setValue(0)
        form_layout.addRow("实际数量:", self.actual_quantity_spin)

        self.check_type_combo = QComboBox()
        self.check_type_combo.addItem("日常盘点", "daily")
        self.check_type_combo.addItem("定期盘点", "periodic")
        self.check_type_combo.addItem("年度盘点", "annual")
        form_layout.addRow("盘点类型:", self.check_type_combo)

        self.remarks_edit = QTextEdit()
        self.remarks_edit.setPlaceholderText("请输入备注信息")
        self.remarks_edit.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remarks_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定盘点")
        ok_btn.clicked.connect(self.do_check)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_equipment(self):
        equipments, _ = EquipmentManager.get_all_equipments(status=1)
        for eq in equipments:
            type_name = dict(config.EQUIPMENT_TYPES).get(eq['type'], eq['type'])
            self.equipment_combo.addItem(
                f"{eq['equipment_code']} - {eq['name']} ({type_name})",
                eq['id']
            )

        if equipments:
            self.on_equipment_changed(0)

    def on_equipment_changed(self, index):
        if index >= 0:
            equipment_id = self.equipment_combo.itemData(index)
            equipment = EquipmentManager.get_equipment_by_id(equipment_id)
            if equipment:
                self.system_stock_label.setText(f"系统库存: {equipment['quantity']}")
                self.actual_quantity_spin.setValue(equipment['quantity'])

    def do_check(self):
        equipment_id = self.equipment_combo.itemData(self.equipment_combo.currentIndex())
        actual_quantity = self.actual_quantity_spin.value()
        check_type = self.check_type_combo.itemData(self.check_type_combo.currentIndex())
        remarks = self.remarks_edit.toPlainText().strip()

        success, msg = InventoryManager.inventory_check(
            equipment_id, actual_quantity, check_type,
            self.current_user['id'], self.current_user['real_name'], remarks
        )

        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class InventoryAdjustmentDialog(QDialog):
    """库存调整对话框"""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.current_user = user
        self.init_ui()
        self.load_equipment()

    def init_ui(self):
        self.setWindowTitle("库存调整")
        self.setFixedSize(500, 350)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.equipment_combo = QComboBox()
        self.equipment_combo.setMinimumContentsLength(20)
        self.equipment_combo.currentIndexChanged.connect(self.on_equipment_changed)
        form_layout.addRow("选择器材:", self.equipment_combo)

        self.current_stock_label = QLabel("当前库存: 0")
        form_layout.addRow("", self.current_stock_label)

        self.new_quantity_spin = QSpinBox()
        self.new_quantity_spin.setRange(0, 99999)
        self.new_quantity_spin.setValue(0)
        form_layout.addRow("新库存数量:", self.new_quantity_spin)

        self.reason_edit = QTextEdit()
        self.reason_edit.setPlaceholderText("请输入调整原因")
        self.reason_edit.setMaximumHeight(80)
        form_layout.addRow("调整原因:", self.reason_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定调整")
        ok_btn.clicked.connect(self.do_adjust)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_equipment(self):
        equipments, _ = EquipmentManager.get_all_equipments(status=1)
        for eq in equipments:
            type_name = dict(config.EQUIPMENT_TYPES).get(eq['type'], eq['type'])
            self.equipment_combo.addItem(
                f"{eq['equipment_code']} - {eq['name']} ({type_name}) [库存:{eq['quantity']}]",
                eq['id']
            )

        if equipments:
            self.on_equipment_changed(0)

    def on_equipment_changed(self, index):
        if index >= 0:
            equipment_id = self.equipment_combo.itemData(index)
            equipment = EquipmentManager.get_equipment_by_id(equipment_id)
            if equipment:
                self.current_stock_label.setText(f"当前库存: {equipment['quantity']}")
                self.new_quantity_spin.setValue(equipment['quantity'])

    def do_adjust(self):
        equipment_id = self.equipment_combo.itemData(self.equipment_combo.currentIndex())
        new_quantity = self.new_quantity_spin.value()
        reason = self.reason_edit.toPlainText().strip()

        if not reason:
            QMessageBox.warning(self, "提示", "请输入调整原因")
            return

        success, msg = InventoryManager.inventory_adjustment(
            equipment_id, new_quantity, reason,
            self.current_user['id'], self.current_user['real_name']
        )

        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class UserManagementDialog(QDialog):
    """用户管理对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_users()

    def init_ui(self):
        self.setWindowTitle("用户管理")
        self.setFixedSize(800, 500)

        layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(self.add_user)
        button_layout.addWidget(add_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(7)
        self.user_table.setHorizontalHeaderLabels(["ID", "用户名", "真实姓名", "角色", "邮箱", "最后登录", "操作"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.user_table)

        self.setLayout(layout)

    def load_users(self):
        users, _ = UserManager.get_all_users(role=None)

        self.user_table.setRowCount(len(users))

        for i, user in enumerate(users):
            self.user_table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
            self.user_table.setItem(i, 1, QTableWidgetItem(user['username']))
            self.user_table.setItem(i, 2, QTableWidgetItem(user['real_name'] or ''))
            self.user_table.setItem(i, 3, QTableWidgetItem("管理员" if user['role'] == 'admin' else "操作员"))
            self.user_table.setItem(i, 4, QTableWidgetItem(user['email'] or ''))
            last_login = user.get('last_login')
            if last_login:
                if hasattr(last_login, 'strftime'):
                    last_login = last_login.strftime('%Y-%m-%d %H:%M')
            self.user_table.setItem(i, 5, QTableWidgetItem(str(last_login) if last_login else '从未登录'))
            self.user_table.setItem(i, 6, QTableWidgetItem("编辑|重置密码|删除"))

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()


class AddUserDialog(QDialog):
    """添加用户对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("添加用户")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        form_layout.addRow("用户名:", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请输入密码")
        form_layout.addRow("密码:", self.password_edit)

        self.real_name_edit = QLineEdit()
        self.real_name_edit.setPlaceholderText("请输入真实姓名")
        form_layout.addRow("真实姓名:", self.real_name_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItem("操作员", "operator")
        self.role_combo.addItem("管理员", "admin")
        form_layout.addRow("角色:", self.role_combo)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("请输入邮箱")
        form_layout.addRow("邮箱:", self.email_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("请输入电话")
        form_layout.addRow("电话:", self.phone_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定添加")
        ok_btn.clicked.connect(self.do_add)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def do_add(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        real_name = self.real_name_edit.text().strip()
        role = self.role_combo.itemData(self.role_combo.currentIndex())
        email = self.email_edit.text().strip()
        phone = self.phone_edit.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return

        success, msg = UserAuth.register(username, password, real_name, role, email, phone)

        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class ChangePasswordDialog(QDialog):
    """修改密码对话框"""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.current_user = user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("修改密码")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        self.old_password_edit.setPlaceholderText("请输入旧密码")
        form_layout.addRow("旧密码:", self.old_password_edit)

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        self.new_password_edit.setPlaceholderText("请输入新密码")
        form_layout.addRow("新密码:", self.new_password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("请确认新密码")
        form_layout.addRow("确认密码:", self.confirm_password_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定修改")
        ok_btn.clicked.connect(self.do_change)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def do_change(self):
        old_password = self.old_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not old_password or not new_password:
            QMessageBox.warning(self, "提示", "请输入旧密码和新密码")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "提示", "两次输入的新密码不一致")
            return

        if len(new_password) < 6:
            QMessageBox.warning(self, "提示", "新密码长度不能少于6位")
            return

        success, msg = UserAuth.change_password(self.current_user['id'], old_password, new_password)

        if success:
            QMessageBox.information(self, "成功", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)


class StatisticsDialog(QDialog):
    """统计报表对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("统计报表")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        button_layout.addWidget(QLabel("开始日期:"))
        button_layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        button_layout.addWidget(QLabel("结束日期:"))
        button_layout.addWidget(self.end_date_edit)

        query_btn = QPushButton("查询")
        query_btn.clicked.connect(self.load_data)
        button_layout.addWidget(query_btn)

        export_btn = QPushButton("导出报表")
        export_btn.clicked.connect(self.export_report)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels(["日期", "入库次数", "入库数量", "出库次数", "出库数量", "净变化"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.report_table)

        self.setLayout(layout)

    def load_data(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        statistics = ReportManager.get_statistics_by_date(start_date, end_date)

        dates = sorted(statistics.keys())

        self.report_table.setRowCount(len(dates))

        for i, date in enumerate(dates):
            stats = statistics[date]
            in_count = stats.get('in', {}).get('count', 0)
            in_quantity = stats.get('in', {}).get('quantity', 0)
            out_count = stats.get('out', {}).get('count', 0)
            out_quantity = stats.get('out', {}).get('quantity', 0)
            net_change = in_quantity - out_quantity

            self.report_table.setItem(i, 0, QTableWidgetItem(date))
            self.report_table.setItem(i, 1, QTableWidgetItem(str(in_count)))
            self.report_table.setItem(i, 2, QTableWidgetItem(str(in_quantity)))
            self.report_table.setItem(i, 3, QTableWidgetItem(str(out_count)))
            self.report_table.setItem(i, 4, QTableWidgetItem(str(out_quantity)))
            self.report_table.setItem(i, 5, QTableWidgetItem(f"{net_change:+d}"))

    def export_report(self):
        try:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

            statistics = ReportManager.get_statistics_by_date(start_date, end_date)

            data = []
            dates = sorted(statistics.keys())
            for date in dates:
                stats = statistics[date]
                in_count = stats.get('in', {}).get('count', 0)
                in_quantity = stats.get('in', {}).get('quantity', 0)
                out_count = stats.get('out', {}).get('count', 0)
                out_quantity = stats.get('out', {}).get('quantity', 0)
                net_change = in_quantity - out_quantity
                data.append([date, in_count, in_quantity, out_count, out_quantity, net_change])

            filepath = ReportManager.export_to_csv(
                data,
                f"统计报表_{start_date}_{end_date}.csv",
                ["日期", "入库次数", "入库数量", "出库次数", "出库数量", "净变化"]
            )

            if filepath:
                QMessageBox.information(self, "成功", f"报表已导出:\n{filepath}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    try:
        init_database()
    except Exception as e:
        QMessageBox.critical(None, "错误", f"数据库初始化失败:\n{str(e)}\n\n请检查数据库配置和权限。")
        return

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        user = login_dialog.get_user()
        if user:
            window = MainWindow(user)
            window.show()
            sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
