import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit,
                             QPushButton, QSpinBox, QTextEdit, QTabWidget,
                             QScrollArea, QGroupBox, QMessageBox, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt
from AHP import AHP
from LLMWorkerClient import LLMWorkerClient
from Presenter import Presenter
from ShortPromptGenerator import ShortPromptGenerator


class AHPApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data = {
            'num_criteria': 0,
            'num_alternatives': 0,
            'num_experts': 0,
            'criteria_names': [],
            'alternative_names': [],
            'expert_data': []
        }
        self.llm_worker = None
        self.prompt_generator = None
        self.setup_llm_tab()

    def initUI(self):
        self.setWindowTitle('Метод анализа иерархий (AHP)')
        self.setGeometry(100, 100, 800, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Вкладка ввода основных параметров
        self.setup_basic_input_tab()
        # Вкладка ввода данных экспертов
        self.setup_expert_input_tab()
        # Вкладка результатов
        self.setup_results_tab()

    def setup_llm_tab(self):
        """Создаем вкладку настроек LLM"""
        llm_tab = QWidget()
        layout = QVBoxLayout(llm_tab)

        # Настройки модели
        model_group = QGroupBox("Настройки модели")
        model_layout = QVBoxLayout(model_group)

        model_layout.addWidget(QLabel("Модель LLM:"))
        # self.model_path_edit = QLineEdit("./models/qwen2.5-1.5b")
        self.model_path_edit = QComboBox()
        self.model_path_edit.addItem("Qwen/Qwen2.5-7B-Instruct")
        self.model_path_edit.addItem("Qwen/Qwen2.5-32B-Instruct:featherless-ai")
        self.model_path_edit.addItem("./models/qwen2.5-1.5b")
        self.model_path_edit.addItem("E:/models/qwen2.5-3b")
        self.model_path_edit.addItem("E:/models/openhermes-mistral")
        model_layout.addWidget(self.model_path_edit)

        layout.addWidget(model_group)

        # Промпты
        prompt_group = QGroupBox("Промпты")
        self.prompt_layout = QVBoxLayout(prompt_group)

        self.prompt_layout.addWidget(QLabel("Базовый промпт:"))
        self.base_prompt = QTextEdit()
        self.base_prompt.setMaximumHeight(100)
        self.prompt_layout.addWidget(self.base_prompt)

        self.prompt_layout.addWidget(QLabel("Описание альтернатив:"))

        layout.addWidget(prompt_group)

        # Кнопки управления
        btn_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Получить оценки от модели")
        self.generate_btn.clicked.connect(self.get_llm_scores)
        self.generate_btn.setEnabled(False)
        btn_layout.addWidget(self.generate_btn)

        layout.addLayout(btn_layout)

        layout.addStretch()

        # Добавляем вкладку после "Основные параметры"
        self.tab_widget.insertTab(1, llm_tab, "Настройки LLM")

    def setup_basic_input_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Ввод количества критериев и альтернатив
        basic_group = QGroupBox("Основные параметры")
        basic_layout = QGridLayout(basic_group)

        basic_layout.addWidget(QLabel("Количество критериев:"), 0, 0)
        self.criteria_spin = QSpinBox()
        self.criteria_spin.setRange(1, 10)
        self.criteria_spin.valueChanged.connect(self.on_criteria_changed)
        basic_layout.addWidget(self.criteria_spin, 0, 1)

        basic_layout.addWidget(QLabel("Количество альтернатив:"), 1, 0)
        self.alternatives_spin = QSpinBox()
        self.alternatives_spin.setRange(1, 10)
        self.alternatives_spin.valueChanged.connect(self.on_alternatives_changed)
        basic_layout.addWidget(self.alternatives_spin, 1, 1)

        basic_layout.addWidget(QLabel("Количество экспертов:"), 2, 0)
        self.experts_spin = QSpinBox()
        self.experts_spin.setRange(1, 10)
        basic_layout.addWidget(self.experts_spin, 2, 1)

        layout.addWidget(basic_group)

        # Ввод названий критериев
        self.criteria_names_group = QGroupBox("Названия критериев")
        self.criteria_names_layout = QVBoxLayout(self.criteria_names_group)
        layout.addWidget(self.criteria_names_group)

        # Ввод названий альтернатив
        self.alternatives_names_group = QGroupBox("Названия альтернатив")
        self.alternatives_names_layout = QVBoxLayout(self.alternatives_names_group)
        layout.addWidget(self.alternatives_names_group)

        # Кнопка подтверждения
        confirm_btn = QPushButton("Подтвердить параметры")
        confirm_btn.clicked.connect(self.confirm_parameters)
        layout.addWidget(confirm_btn)

        self.tab_widget.addTab(tab, "Основные параметры")

    def setup_expert_input_tab(self):
        self.expert_tab = QWidget()
        self.expert_layout = QVBoxLayout(self.expert_tab)

        self.expert_scroll = QScrollArea()
        self.expert_widget = QWidget()
        self.expert_scroll_layout = QVBoxLayout(self.expert_widget)
        self.expert_scroll.setWidget(self.expert_widget)
        self.expert_scroll.setWidgetResizable(True)

        self.expert_layout.addWidget(self.expert_scroll)

        calculate_btn = QPushButton("Рассчитать результаты")
        calculate_btn.clicked.connect(self.on_calculate_results)
        self.expert_layout.addWidget(calculate_btn)

        self.tab_widget.addTab(self.expert_tab, "Данные экспертов")

    def setup_results_tab(self):
        self.results_tab = QWidget()
        layout = QVBoxLayout(self.results_tab)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        export_btn = QPushButton("Экспорт в Excel")
        export_btn.clicked.connect(self.export_to_excel)
        layout.addWidget(export_btn)

        self.tab_widget.addTab(self.results_tab, "Результаты")

    def on_criteria_changed(self, value):
        self.update_criteria_names_input(value)

    def on_alternatives_changed(self, value):
        self.update_alternative_names_input(value)

    def update_criteria_names_input(self, count):
        current_count = self.criteria_names_layout.count()
        if current_count < count:
            for i in range(current_count, count):
                layout = QHBoxLayout()
                layout.addWidget(QLabel(f"Критерий {i + 1}:"))
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(f"Введите название критерия {i + 1}")
                layout.addWidget(line_edit)
                self.criteria_names_layout.addLayout(layout)
        elif current_count > count:
            for i in range(current_count - 1, count - 1, -1):
                layout = self.criteria_names_layout.itemAt(i).layout()
                for j in reversed(range(layout.count())):
                    layout.itemAt(j).widget().deleteLater()
                layout.deleteLater()

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

    def confirm_parameters(self):
        # Сохраняем основные параметры
        self.data['num_criteria'] = self.criteria_spin.value()
        self.data['num_alternatives'] = self.alternatives_spin.value()
        self.data['num_experts'] = self.experts_spin.value()

        # Сохраняем названия критериев
        self.data['criteria_names'] = []
        for i in range(self.criteria_names_layout.count()):
            layout = self.criteria_names_layout.itemAt(i)
            if layout:
                line_edit = layout.itemAt(1).widget()
                name = line_edit.text().strip()
                if not name:
                    name = f"Критерий {i + 1}"
                self.data['criteria_names'].append(name)

        # Сохраняем названия альтернатив
        self.data['alternative_names'] = []
        for i in range(self.alternatives_names_layout.count()):
            layout = self.alternatives_names_layout.itemAt(i)
            if layout:
                line_edit = layout.itemAt(1).widget()
                name = line_edit.text().strip()
                if not name:
                    name = f"Альтернатива {i + 1}"
                self.data['alternative_names'].append(name)

        # Создаем интерфейс для ввода данных экспертов
        self.setup_expert_data_input()

        if (self.data['num_criteria'] > 0 and
                self.data['num_alternatives'] > 0):
            self.generate_btn.setEnabled(True)

        for i in range(self.alternatives_names_layout.count()):
            layout = QHBoxLayout()
            layout.addWidget(QLabel(self.data['alternative_names'][i]))
            text_edit = QTextEdit()
            layout.addWidget(text_edit)
            self.prompt_layout.addLayout(layout)

        # self.prompt_generator = PromptGenerator(self.data['criteria_names'], self.data['alternative_names'])
        self.prompt_generator = ShortPromptGenerator()
        self.base_prompt.setPlainText(self.prompt_generator.basic_prompt)
        self.base_prompt.textChanged.connect(self.on_basic_prompt_changed)

    def on_basic_prompt_changed(self):
        self.prompt_generator.basic_prompt = self.base_prompt.toPlainText()

    def setup_expert_data_input(self):
        # Очищаем текущий контент
        for i in reversed(range(self.expert_scroll_layout.count())):
            widget = self.expert_scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        n_criteria = self.data['num_criteria']
        n_alternatives = self.data['num_alternatives']
        n_experts = self.data['num_experts']

        # Создаем интерфейс для каждого эксперта
        for expert_idx in range(n_experts):
            expert_group = QGroupBox(f"Эксперт {expert_idx + 1}")
            expert_layout = QVBoxLayout(expert_group)

            # Матрица попарных сравнений критериев
            criteria_group = QGroupBox("Попарные сравнения критериев")
            criteria_layout = QGridLayout(criteria_group)
            alignment = Qt.AlignmentFlag.AlignHCenter

            # Заголовки строк и столбцов
            for i in range(n_criteria):
                criteria_layout.addWidget(QLabel(self.data['criteria_names'][i]), i + 1, 0, alignment=alignment)
                criteria_layout.addWidget(QLabel(self.data['criteria_names'][i]), 0, i + 1, alignment=alignment)

            # Поля ввода для матрицы критериев
            criteria_matrix_inputs = []
            for i in range(n_criteria):
                row_inputs = []
                for j in range(n_criteria):
                    if i == j:
                        label = QLabel("1")
                        criteria_layout.addWidget(label, i + 1, j + 1, alignment=alignment)
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

                        criteria_layout.addLayout(input_layout, i + 1, j + 1, alignment=alignment)
                        row_inputs.append((numerator, denominator))
                    else:
                        row_inputs.append(None)
                criteria_matrix_inputs.append(row_inputs)

            expert_layout.addWidget(criteria_group)

            # Матрицы попарных сравнений альтернатив по каждому критерию
            alternatives_groups = []
            for crit_idx in range(n_criteria):
                alt_group = QGroupBox(
                    f"Попарные сравнения альтернатив по критерию: {self.data['criteria_names'][crit_idx]}")
                alt_layout = QGridLayout(alt_group)

                # Заголовки
                for i in range(n_alternatives):
                    alt_layout.addWidget(QLabel(self.data['alternative_names'][i]), i + 1, 0, alignment=alignment)
                    alt_layout.addWidget(QLabel(self.data['alternative_names'][i]), 0, i + 1, alignment=alignment)

                # Поля ввода
                alt_matrix_inputs = []
                for i in range(n_alternatives):
                    row_inputs = []
                    for j in range(n_alternatives):
                        if i == j:
                            label = QLabel("1")
                            alt_layout.addWidget(label, i + 1, j + 1, alignment=alignment)
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

                            alt_layout.addLayout(input_layout, i + 1, j + 1, alignment=alignment)
                            row_inputs.append((numerator, denominator))
                        else:
                            row_inputs.append(None)
                    alt_matrix_inputs.append(row_inputs)

                alternatives_groups.append(alt_matrix_inputs)
                expert_layout.addWidget(alt_group)

            # Сохраняем ссылки на поля ввода
            expert_data = {
                'criteria_matrix': criteria_matrix_inputs,
                'alternatives_matrices': alternatives_groups
            }
            if len(self.data['expert_data']) <= expert_idx:
                self.data['expert_data'].append(expert_data)
            else:
                self.data['expert_data'][expert_idx] = expert_data

            self.expert_scroll_layout.addWidget(expert_group)

    def display_results(self, result_text):
        self.results_text.setText(result_text)

    def on_calculate_results(self):
        ahp = AHP(self.data)
        self.results = ahp.calculate_results()
        result_text = Presenter.display_results(self.data, *self.results)
        self.display_results(result_text)

    def export_to_excel(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить результаты Excel", "", "Excel Files (*.xlsx)"
            )

            if not file_path:
                return

            Presenter.export_to_excel(self.data, *self.results, file_path)

            QMessageBox.information(self, "Успех", f"Результаты экспортированы в файл:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте в Excel: {str(e)}")

    def _collect_alternative_descriptions(self):
        self.alternative_descriptions = []
        for i in range(3, self.prompt_layout.count()):
            layout = self.prompt_layout.itemAt(i)
            if layout:
                text_edit = layout.itemAt(1).widget()
                desc = text_edit.toPlainText().strip()
                if not desc:
                    desc = self.data['alternative_names'][i-1]
                self.alternative_descriptions.append(desc)

    def get_llm_scores(self):
        """Получение оценок от LLM"""
        if not self.data['criteria_names'] or not self.data['alternative_names']:
            QMessageBox.warning(self, "Ошибка", "Сначала введите названия критериев и альтернатив")
            return

        self.generate_btn.setEnabled(False)
        print('collect descriptions')
        self._collect_alternative_descriptions()

        # Запускаем worker в отдельном потоке
        print("start creating worker")
        self.llm_worker = LLMWorkerClient(
            model_path=self.model_path_edit.currentText(),
            prompt_generator=self.prompt_generator,
            criteria_names=self.data['criteria_names'],
            alternative_names=self.data['alternative_names'],
            alternative_descriptions=self.alternative_descriptions
        )

        self.llm_worker.finished.connect(self.on_llm_finished)
        self.llm_worker.error.connect(self.on_llm_error)
        self.llm_worker.start()

    def on_llm_finished(self, results):
        """Обработка завершения работы LLM"""
        # Заполняем матрицы в UI
        print("start filling ui with results")
        self.fill_matrices_with_llm_results(results)
        print("filled with results")

        # Переключаемся на вкладку экспертов
        self.tab_widget.setCurrentIndex(2)  # "Данные экспертов"

        QMessageBox.information(self, "Успех", "Оценки от LLM получены и заполнены!")

        # Возвращаем UI в исходное состояние
        self.generate_btn.setEnabled(True)

    def on_llm_error(self, error_message):
        """Обработка ошибки LLM"""
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка LLM", f"Не удалось получить оценки:\n{error_message}")

    def fill_matrices_with_llm_results(self, results):
        """Заполнение матриц результатами LLM"""
        if not self.data['expert_data']:
            return

        # Заполняем матрицу критериев для первого эксперта
        print("fill criteria matrix")
        expert_data = self.data['expert_data'][0]
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


def main():
    app = QApplication(sys.argv)
    window = AHPApplication()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
