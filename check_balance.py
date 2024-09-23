import sys
import copy
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLineEdit, QLabel, QHBoxLayout, QCheckBox, QPushButton


class wheelLineEdit(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.line_edit = QLineEdit()
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)
        self.second_line = None

    def wheelEvent(self, event):
        try:
            current_value = int(self.line_edit.text())
        except:
            current_value = 0

        current_len = len(self.line_edit.text())

        delta = event.angleDelta().y()

        step = 1
        if current_len == 3:
            step = 10
        elif current_len >=4:
            step = 100
        if delta > 0:
            current_value += step
        else:
            current_value -= step

        if current_value <= 0:
            current_value = 0

        self.line_edit.setText(str(current_value))
        event.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        is_test = False

        self.command = ""

        self.setWindowTitle("Legion TD balanced")
        self.layout = QVBoxLayout()
        self.grid = QGridLayout()

        self.copy_but = QPushButton("Копировать")
        self.copy_but.clicked.connect(self.copy_to_clipboard)

        self.label1 = QLabel("")
        self.label2 = QLabel("")
        self.label3 = QLabel("")
        self.layout.addWidget(self.label1)
        lay_buf = QHBoxLayout()
        lay_buf.addWidget(self.label2)
        lay_buf.addWidget(self.copy_but)
        self.layout.addLayout(lay_buf)
        self.layout.addWidget(self.label3)

        self.line_edits = []
        self.check_edits = []
        number = 1
        colors = ('red', 'blue', 'turquoise', 'purple', 'yellow', 'orange', 'green', 'pink')
        for i in range(2):
            for j in range(4):
                lay = QHBoxLayout()
                line_edit = wheelLineEdit()
                if is_test:
                    line_edit.line_edit.setText(str(number))
                line_edit.line_edit.textChanged.connect(self.check_values)
                check = QCheckBox()
                check.stateChanged.connect(self.check_values)
                check.setText(str(number))
                if number == 2 or number == 4:
                    check.setStyleSheet(f"background-color: {colors[number-1]}; color: white;")
                else:
                    check.setStyleSheet(f"background-color: {colors[number-1]}; color: black;")

                self.line_edits.append(line_edit)
                self.check_edits.append(check)
                if i == 0:
                    lay.addWidget(check)
                    lay.addWidget(line_edit)
                else:
                    lay.addWidget(line_edit)
                    lay.addWidget(check)
                self.grid.addLayout(lay, j, i)

                number+=1

        if is_test:
            self.check_values()
        else:
            self.check_edits[0].setChecked(True)

        self.layout.addLayout(self.grid)
        self.setLayout(self.layout)



    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        
        clipboard.setText(self.command)

    def check_values(self):
        all_valid = True
        sum_col1 = 0
        sum_col2 = 0
        numbers = []
        
        for index, line_edit in enumerate(self.line_edits):
            text = line_edit.line_edit.text()
            if text == "" or self.is_number(text):
                numbers.append(float(text) if text != "" else 0)
                line_edit.line_edit.setStyleSheet("border: 2px solid green;")
            else:
                line_edit.line_edit.setStyleSheet("border: 2px solid red;")
                all_valid = False

        restricted_indices = [i for i, x in enumerate(self.check_edits) if x.isChecked()]
        
        if all_valid:
            difference = self.get_diff()
            self.label1.setText(f"Разница: {difference:.2f}")

            self.command = self.get_best_commands(numbers, restricted_indices)
            self.label2.setText(self.command)
        else:
            self.label1.setText("Есть некорректные поля.")

    def get_diff(self):
        sum_col1 = 0
        sum_col2 = 0
        
        for index, line_edit in enumerate(self.line_edits):
            text = line_edit.line_edit.text()
            if text == "" or self.is_number(text):
                value = float(text) if text != "" else 0
                if index < 4:
                    sum_col1 += value
                else:       
                    sum_col2 += value
            else:
                return False

        return sum_col1 - sum_col2
    
    def calc_diff_after_swap(self, numbers, restricted_indices):
        num = copy.deepcopy(numbers)
        num[restricted_indices[0]], num[restricted_indices[1]] = num[restricted_indices[1]], num[restricted_indices[0]]
        return sum(num[:4]) - sum(num[4:]), num


    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def get_best_commands(self, numbers, restricted_indices):
            indexes1 = self.minimize_difference(numbers, restricted_indices)
            self.command= f"разница минимальна в текущих условиях"
            if indexes1[0] == indexes1[1]:
                return self.command
            else:
                numbers[indexes1[0]], numbers[indexes1[1]] = numbers[indexes1[1]], numbers[indexes1[0]]
                indexes2 = self.minimize_difference(numbers, restricted_indices)
                numbers[indexes1[0]], numbers[indexes1[1]] = numbers[indexes1[1]], numbers[indexes1[0]]
                if indexes1[0] == indexes2[1] or indexes1[0] in indexes2 or indexes1[1] in indexes2 or numbers[indexes2[0]] == numbers[indexes2[1]]:
                    self.command= f"!swap {indexes1[0]+1} {indexes1[1]+1}"
                    after_val, _ = self.calc_diff_after_swap(numbers, indexes1)
                    self.label3.setText(f"После команды будет {after_val}")
                    return self.command
                else:
                    self.command= f"!swap {indexes1[0]+1} {indexes1[1]+1},{indexes2[0]+1} {indexes2[1]+1}"
                    _ , new_num = self.calc_diff_after_swap(numbers, indexes1)
                    after_val, _ = self.calc_diff_after_swap(new_num, indexes2)
                    self.label3.setText(f"После команды будет {after_val}")
                    return self.command
        
    def minimize_difference(self, numbers, restricted_indices):
        min_diff = abs(self.get_diff())
        min_val = min_diff
        best_indices = (0, 0)

        for i in range(4):
            if i in restricted_indices:
                continue 

            for j in range(4, 8):
                if j in restricted_indices:
                    continue 

                numbers[i], numbers[j] = numbers[j], numbers[i]
                current_diff = abs(sum(numbers[:4]) - sum(numbers[4:]))

                if current_diff < min_diff:
                    min_diff = current_diff
                    min_val = sum(numbers[:4]) - sum(numbers[4:])
                    best_indices = (i, j)

                numbers[i], numbers[j] = numbers[j], numbers[i]

        self.label3.setText(f"После команды будет {min_val}")

        return best_indices


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
