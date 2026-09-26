import abc
import numpy as np
import PyQt6.sip
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit,
                             QPushButton, QSpinBox, QTextEdit, QTabWidget,
                             QScrollArea, QGroupBox, QMessageBox, QFileDialog, QComboBox, QTreeWidget, QHeaderView,
                             QTreeWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from domain.CriterionNode import CriterionNode
from presenter.IAHPView import IAHPView


class Meta(abc.ABCMeta, PyQt6.sip.wrappertype):
    pass


class AHPApplication(QMainWindow, IAHPView, metaclass=Meta):
    generate_clicked = pyqtSignal()
    alternatives_changed = pyqtSignal(int)
    confirm_parameters_clicked = pyqtSignal()
    calculate_results_clicked = pyqtSignal()
    export_clicked = pyqtSignal()

    def show_error(self, message: str):
        QMessageBox.critical(self, "Ошибка", message)

    def show_success(self, message: str):
        QMessageBox.information(self, "Успех", message)

    def show_results(self, results_text: str):
        self.results_text.setText(results_text)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.expert_data = []
        self._connect_signals()

    def _connect_signals(self):
        self.generate_btn.clicked.connect(self.generate_clicked)
        self.alternatives_spin.valueChanged.connect(self.alternatives_changed)
        self.confirm_btn.clicked.connect(self.confirm_parameters_clicked)
        self.calculate_btn.clicked.connect(self.calculate_results_clicked)
        self.export_btn.clicked.connect(self.export_clicked)

    def init_ui(self):
        self.setWindowTitle('Метод анализа иерархий (AHP)')
        self.setGeometry(100, 100, 800, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.setup_basic_input_tab()
        self.setup_expert_input_tab()
        self.setup_results_tab()
        self.setup_llm_tab()

    def setup_llm_tab(self):
        """Создаем вкладку настроек LLM"""
        llm_tab = QWidget()
        layout = QVBoxLayout(llm_tab)

        # Настройки модели
        model_group = QGroupBox("Настройки модели")
        model_layout = QVBoxLayout(model_group)

        model_layout.addWidget(QLabel("Модель LLM:"))
        self.model_path_edit = QComboBox()
        self.model_path_edit.addItem("./models/qwen2.5")
        self.model_path_edit.addItem("./models/qwen2.5-1.5b")
        self.model_path_edit.addItem("Qwen/Qwen2.5-7B-Instruct")
        self.model_path_edit.addItem("Qwen/Qwen2.5-32B-Instruct:featherless-ai")
        self.model_path_edit.addItem("Qwen/Qwen3.6-35B-A3B:featherless-ai")
        self.model_path_edit.addItem("Qwen/Qwen3-235B-A22B-Instruct-2507:scaleway")
        model_layout.addWidget(self.model_path_edit)

        layout.addWidget(model_group)

        # Промпты
        prompt_group = QGroupBox("Промпты")
        self.prompt_layout = QVBoxLayout(prompt_group)

        self.prompt_layout.addWidget(QLabel("Файл с текстами:"))
        self.alt_file = QLineEdit()
        self.prompt_layout.addWidget(self.alt_file)

        layout.addWidget(prompt_group)

        # Кнопки управления
        btn_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Получить оценки от модели")
        self.generate_btn.setEnabled(False)
        btn_layout.addWidget(self.generate_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # Добавляем вкладку после "Основные параметры"
        self.tab_widget.insertTab(1, llm_tab, "Настройки LLM")

    @staticmethod
    def build_matrix_from_inputs(input_matrix, size):
        matrix = np.ones((size, size))

        for i in range(size):
            for j in range(size):
                if i < j and input_matrix[i][j] is not None:
                    numerator_edit, denominator_edit = input_matrix[i][j]
                    try:
                        numerator = float(numerator_edit.text() or 1)
                        denominator = float(denominator_edit.text() or 1)
                        if denominator == 0:
                            denominator = 1
                        value = numerator / denominator
                        matrix[i, j] = value
                        matrix[j, i] = 1.0 / value
                    except ValueError:
                        matrix[i, j] = 1.0
                        matrix[j, i] = 1.0

        return matrix

    def setup_basic_input_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Ввод количества критериев и альтернатив
        basic_group = QGroupBox("Основные параметры")
        basic_layout = QGridLayout(basic_group)

        basic_layout.addWidget(QLabel("Количество альтернатив:"), 0, 0)
        self.alternatives_spin = QSpinBox()
        self.alternatives_spin.setRange(1, 10)
        basic_layout.addWidget(self.alternatives_spin, 0, 1)

        basic_layout.addWidget(QLabel("Количество экспертов:"), 1, 0)
        self.experts_spin = QSpinBox()
        self.experts_spin.setRange(1, 10)
        basic_layout.addWidget(self.experts_spin, 1, 1)

        layout.addWidget(basic_group)

        # Ввод названий критериев
        self.criteria_names_group = QGroupBox("Названия критериев")
        self.criteria_names_layout = QVBoxLayout(self.criteria_names_group)

        # Дерево
        self.criteria_tree_widget = QTreeWidget()
        self.criteria_tree_widget.setHeaderLabels(["", ""])
        self.criteria_tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.criteria_tree_widget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.criteria_tree_widget.header().resizeSection(1, 100)
        self.criteria_names_layout.addWidget(self.criteria_tree_widget)

        # Кнопка добавления корневого критерия
        btn_layout = QHBoxLayout()
        self.add_root_criterion_btn = QPushButton("Добавить критерий")
        self.add_root_criterion_btn.clicked.connect(self._on_add_root_criterion)
        btn_layout.addWidget(self.add_root_criterion_btn)
        btn_layout.addStretch()
        self.criteria_names_layout.addLayout(btn_layout)
        # self._on_add_root_criterion()

        layout.addWidget(self.criteria_names_group)

        # Ввод названий альтернатив
        self.alternatives_names_group = QGroupBox("Названия альтернатив")
        self.alternatives_names_layout = QVBoxLayout(self.alternatives_names_group)
        layout.addWidget(self.alternatives_names_group)

        # Кнопка подтверждения
        self.confirm_btn = QPushButton("Подтвердить параметры")
        layout.addWidget(self.confirm_btn)

        self.tab_widget.addTab(tab, "Основные параметры")

    def _on_add_root_criterion(self):
        """Добавить корневой критерий"""
        item = QTreeWidgetItem(self.criteria_tree_widget.invisibleRootItem())
        item.setText(0, "")
        self._add_tree_item_controls(item)
        # self._add_tree_item_button(item)

    def _add_tree_item_controls(self, item: QTreeWidgetItem):
        """Добавить кнопки управления к элементу дерева"""
        self._add_tree_item_button(item)
        # Line edit для названия
        self._add_tree_item_line_edit(item)

    def _add_tree_item_button(self, item: QTreeWidgetItem):
        # Кнопка добавления потомка
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(30)
        add_btn.clicked.connect(lambda: self._on_add_child(item))
        self.criteria_tree_widget.setItemWidget(item, 1, add_btn)

    def _add_tree_item_line_edit(self, item: QTreeWidgetItem):
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Название критерия")
        self.criteria_tree_widget.setItemWidget(item, 0, name_edit)

    def _on_add_child(self, parent_item: QTreeWidgetItem):
        """Добавить потомка к выбранному элементу"""
        child_item = QTreeWidgetItem(parent_item)
        child_item.setText(0, "")
        self._add_tree_item_controls(child_item)
        parent_item.setExpanded(True)

    def setup_expert_input_tab(self):
        self.expert_tab = QWidget()
        self.expert_layout = QVBoxLayout(self.expert_tab)

        self.expert_scroll = QScrollArea()
        self.expert_widget = QWidget()
        self.expert_scroll_layout = QVBoxLayout(self.expert_widget)
        self.expert_scroll.setWidget(self.expert_widget)
        self.expert_scroll.setWidgetResizable(True)

        self.expert_layout.addWidget(self.expert_scroll)

        self.calculate_btn = QPushButton("Рассчитать результаты")
        self.expert_layout.addWidget(self.calculate_btn)

        self.tab_widget.addTab(self.expert_tab, "Данные экспертов")

    def setup_results_tab(self):
        self.results_tab = QWidget()
        layout = QVBoxLayout(self.results_tab)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        self.export_btn = QPushButton("Экспорт в Excel")
        layout.addWidget(self.export_btn)

        self.tab_widget.addTab(self.results_tab, "Результаты")

    def update_alternative_names_input(self, count):
        current_count = self.alternatives_names_layout.count()
        if current_count < count:
            for i in range(current_count, count):
                layout = QHBoxLayout()
                layout.addWidget(QLabel(f"Альтернатива {i + 1}:"))
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(f"Введите название альтернативы {i + 1}")
                layout.addWidget(line_edit)
                self.alternatives_names_layout.addLayout(layout)
        elif current_count > count:
            for i in range(current_count - 1, count - 1, -1):
                layout = self.alternatives_names_layout.itemAt(i).layout()
                for j in reversed(range(layout.count())):
                    layout.itemAt(j).widget().deleteLater()
                layout.deleteLater()

    def get_parameters(self):
        # Сохраняем основные параметры
        data = {'num_alternatives': self.alternatives_spin.value(),
                'num_experts': self.experts_spin.value(), 'alternative_names': [],
                'criteria_tree': self._build_criteria_tree_from_ui()}

        # Сохраняем названия альтернатив
        for i in range(self.alternatives_names_layout.count()):
            layout = self.alternatives_names_layout.itemAt(i)
            if layout:
                line_edit = layout.itemAt(1).widget()
                name = line_edit.text().strip()
                if not name:
                    name = f"Альтернатива {i + 1}"
                data['alternative_names'].append(name)

        if data['criteria_tree'].children and data['num_alternatives'] > 0:
            self.generate_btn.setEnabled(True)
        return data

    def _build_criteria_tree_from_ui(self) -> CriterionNode:
        """Построить дерево критериев из UI"""
        root = CriterionNode(name="Root")
        root_item = self.criteria_tree_widget.invisibleRootItem()

        for i in range(root_item.childCount()):
            child_item = root_item.child(i)
            node = self._tree_item_to_node(child_item)
            if node:
                root.add_child(node)

        return root

    def _tree_item_to_node(self, item: QTreeWidgetItem) -> CriterionNode | None:
        """Рекурсивно преобразовать QTreeWidgetItem в CriterionNode"""
        name_edit = self.criteria_tree_widget.itemWidget(item, 0)
        if not name_edit:
            return None
        name = name_edit.text().strip()
        if not name:
            name = f"Критерий_{id(item)}"
        node = CriterionNode(name=name)

        for i in range(item.childCount()):
            child_item = item.child(i)
            child_node = self._tree_item_to_node(child_item)
            if child_node:
                node.add_child(child_node)

        return node

    class ExpertDataInputNode:
        def __init__(self, name=None):
            self.name = name
            self.matrix_inputs = None
            self.children = []

    def setup_expert_data_input(self, data):
        # Очищаем текущий контент
        for i in reversed(range(self.expert_scroll_layout.count())):
            widget = self.expert_scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        n_alternatives = data['num_alternatives']
        n_experts = data['num_experts']
        criteria_tree = data['criteria_tree']
        alternative_names = data['alternative_names']

        # Создаем интерфейс для каждого эксперта
        for expert_idx in range(n_experts):
            expert_group = QGroupBox(f"Эксперт {expert_idx + 1}")
            expert_layout = QVBoxLayout(expert_group)

            # Создаем матрицы для каждого узла дерева
            expert_data = self.ExpertDataInputNode()
            self._create_node_matrices_ui(
                expert_layout,
                criteria_tree,
                n_alternatives,
                alternative_names,
                expert_data,
                expert_idx
            )

            self.expert_data.append(expert_data)
            self.expert_scroll_layout.addWidget(expert_group)

    def _create_node_matrices_ui(
            self,
            parent_layout: QVBoxLayout,
            node: CriterionNode,
            n_alternatives: int,
            alternative_names: list[str],
            expert_data: ExpertDataInputNode,
            expert_idx: int
    ):
        expert_data.name = node.name
        """Рекурсивно создать матрицы для всех узлов дерева"""
        if node.is_leaf():
            # Лист — матрица сравнений альтернатив
            group = QGroupBox(f"Альтернативы по критерию: {node.name}")
            layout = QGridLayout(group)
            matrix_inputs = self._create_matrix_input_ui(
                layout,
                alternative_names,
                n_alternatives
            )
            expert_data.matrix_inputs = matrix_inputs
        else:
            # Внутренний узел — матрица сравнений потомков
            child_names = [c.name for c in node.children]
            group = QGroupBox(f"Потомки критерия: {node.name}" if node.name != 'Root' else 'Корневые критерии')
            layout = QGridLayout(group)
            matrix_inputs = self._create_matrix_input_ui(
                layout,
                child_names,
                len(child_names)
            )
            expert_data.matrix_inputs = matrix_inputs
        parent_layout.addWidget(group)
        for child_node in node.children:
            expert_data.children.append(self.ExpertDataInputNode())
            child_expert_data = expert_data.children[-1]
            # Рекурсия для потомков
            self._create_node_matrices_ui(
                parent_layout,
                child_node,
                n_alternatives,
                alternative_names,
                child_expert_data,
                expert_idx
            )

    def _create_matrix_input_ui(
            self,
            layout: QGridLayout,
            labels: list[str],
            size: int
    ) -> list[list]:
        """Создать UI для матрицы парных сравнений"""
        alignment = Qt.AlignmentFlag.AlignHCenter

        # Заголовки
        for i in range(size):
            layout.addWidget(QLabel(labels[i]), i + 1, 0, alignment=alignment)
            layout.addWidget(QLabel(labels[i]), 0, i + 1, alignment=alignment)

        # Поля ввода
        matrix_inputs = []
        for i in range(size):
            row_inputs = []
            for j in range(size):
                if i == j:
                    label = QLabel("1")
                    layout.addWidget(label, i + 1, j + 1, alignment=alignment)
                    row_inputs.append(None)
                elif i < j:
                    input_layout = QHBoxLayout()
                    numerator = QLineEdit()
                    numerator.setPlaceholderText("1")
                    numerator.setText("1")
                    numerator.setFixedWidth(30)
                    denominator = QLineEdit()
                    denominator.setPlaceholderText("1")
                    denominator.setText("1")
                    denominator.setFixedWidth(30)
                    slash_label = QLabel("/")
                    input_layout.addStretch()
                    input_layout.addWidget(numerator)
                    input_layout.addWidget(slash_label)
                    input_layout.addWidget(denominator)
                    input_layout.addStretch()

                    layout.addLayout(input_layout, i + 1, j + 1, alignment=alignment)
                    row_inputs.append((numerator, denominator))
                else:
                    row_inputs.append(None)
            matrix_inputs.append(row_inputs)

        return matrix_inputs

    def get_expert_data(self, data):
        n_experts = data['num_experts']
        criteria_tree = data['criteria_tree']

        for expert_idx in range(n_experts):
            expert_data = self.expert_data[expert_idx]
            self._get_expert_data_from_node(expert_data, criteria_tree, expert_idx)

    def _get_expert_data_from_node(self, input_node, node, expert_idx):
        node.matrices[expert_idx] = self.build_matrix_from_inputs(
            input_node.matrix_inputs, len(input_node.matrix_inputs)
        )
        for i, child in enumerate(input_node.children):
            self._get_expert_data_from_node(child, node.children[i], expert_idx)

    def display_results(self, result_text):
        self.results_text.setText(result_text)

    def get_file_path_from_dialog(self) -> str | None:
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результаты Excel", "", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return None
        return file_path

    def get_model_path(self) -> str:
        self.generate_btn.setEnabled(False)
        return self.model_path_edit.currentText()

    def on_llm_finished(self, results):
        """Обработка завершения работы LLM"""
        # Заполняем матрицы в UI
        print("start filling ui with results")
        self.fill_matrices_with_llm_results(results)
        print("filled with results")
        # Переключаемся на вкладку экспертов
        self.tab_widget.setCurrentIndex(2)  # "Данные экспертов"
        self.show_success("Оценки от LLM получены и заполнены!")
        # Возвращаем UI в исходное состояние
        self.generate_btn.setEnabled(True)

    def on_llm_error(self, error_message):
        self.generate_btn.setEnabled(True)
        self.show_error(f"Не удалось получить оценки:\n{error_message}")

    def fill_matrices_with_llm_results(self, results):
        # Заполняем матрицу критериев для первого эксперта
        print("fill criteria matrix")
        expert_data = self.expert_data[0]
        criteria_matrix = results['criteria_matrix']
        self.fill_matrix_ui(expert_data['criteria_matrix'], criteria_matrix)

        # Заполняем матрицы альтернатив
        print("fill alternatives matrices")
        for crit_idx, alt_matrix in enumerate(results['alternative_matrices']):
            if crit_idx < len(expert_data['alternatives_matrices']):
                self.fill_matrix_ui(
                    expert_data['alternatives_matrices'][crit_idx],
                    alt_matrix
                )

    def fill_matrix_ui(self, ui_matrix, values_matrix):
        """Заполнение UI матрицы значениями"""
        size = len(values_matrix)

        for i in range(size):
            for j in range(size):
                if i < j and ui_matrix[i][j] is not None:
                    numerator_edit, denominator_edit = ui_matrix[i][j]
                    value = values_matrix[i][j]

                    if isinstance(value, (int, float)):
                        if value >= 1:
                            numerator_edit.setText(f"{value:.2f}")
                            denominator_edit.setText("1")
                        elif value > 0:
                            numerator_edit.setText("1")
                            denominator_edit.setText(f"{1 / value:.2f}")
                        else:
                            numerator_edit.setText("1")
                            denominator_edit.setText("1")
