import sys
import requests

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QLabel, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from definitions import *
from src.python.match import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class LoadingWindow(QMainWindow):
    def __init__(self, parent=None):
        super(LoadingWindow, self).__init__(parent)
        self.setWindowTitle("Loading, please wait...")


class MainMenu(QMainWindow):
    # TODO: allow for setting of DB_PATH, TREE_PATH, and OUTPUT_PATH before run
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
        self.pushButton = QPushButton("Run")

        self.setCentralWidget(self.pushButton)

        self.pushButton.clicked.connect(self.start_match)

        self.loading_window = LoadingWindow(self)

        self.dialogs = list()

    def start_match(self):
        # Might include other functionality, such as loading bar
        self.run_match()

    def run_match(self):
        compare_window = Compare(self)
        self.dialogs.append(compare_window)

        info = read_wiki_file(INFO_PATH, INFO_FNAME)
        taxa_list = match(DB_PATH, TREE_PATH, "_", 4)
        missing_info = validate_info(info, taxa_list)
        wiki_info = get_wiki_info(missing_info)
        # Skip file writing if no info is added
        if wiki_info:
            write_wiki_file(wiki_info, INFO_PATH, INFO_FNAME)

        compare_window.__init__(self)

        compare_window.setParent(self)
        compare_window.compare_mismatch(iter(taxa_list), compare_window)
        self.hide()


# dialog.close()

# print("Starting Match...")
#
# start_time = time.time()
# taxa_list = db_match(DB_PATH, TREE_PATH, "_", 4)
# print("--- %s seconds ---" % (time.time() - start_time))
#
# compare = Compare(self)
# compare.compare_mismatch(self, iter(taxa_list))


class Compare(QMainWindow):
    def __init__(self, parent=None):
        super(Compare, self).__init__(parent)
        self.setWindowTitle("compare")

        self.main_widget = QWidget()
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.layout = QGridLayout(self.main_widget)

        self.info_layout = QVBoxLayout()
        self.layout.addLayout(self.info_layout, 0, 1)

        self.taxa_layout = QHBoxLayout()
        self.layout.addLayout(self.taxa_layout, 1, 1)

        self.suggestions_layout = QHBoxLayout()
        self.layout.addLayout(self.suggestions_layout, 2, 1)

        self.images = QHBoxLayout()
        self.layout.addLayout(self.images, 3, 1)

        self.buttons = QHBoxLayout()
        self.layout.addLayout(self.buttons, 4, 1)

        self.taxa_label = QLabel("animals_animals")
        self.taxa_label.setAlignment(Qt.AlignCenter)
        self.info_layout.addWidget(self.taxa_label, 1)

        self.removed_suggestions = []
        self.removed_suggestions_label = QLabel()
        self.removed_suggestions_label.setStyleSheet("QLabel {background-color: red;}")

        self.taxa_info = QLabel("So many options!")
        self.taxa_info.setAlignment(Qt.AlignCenter)

        self.options_count_label = QHBoxLayout()
        self.options_count_label.setAlignment(Qt.AlignCenter)
        self.info_layout.addLayout(self.options_count_label, 1)

        self.similar_entries_count = QPushButton()
        self.options_count_label.addWidget(self.similar_entries_count)
        self.same_species_count = QPushButton()
        self.options_count_label.addWidget(self.same_species_count)
        self.same_genus_count = QPushButton()
        self.options_count_label.addWidget(self.same_genus_count)

        # self.suggestion_label.setStyleSheet(
        #     "border-style: solid; border-width: 1px; border-color: black;"
        # )

        self.continue_btn = QPushButton("None of these", self)
        self.buttons.addWidget(self.continue_btn, 1)

        self.line_edit = QLineEdit()
        self.buttons.addWidget(self.line_edit, 1)

        self.skip_btn = QPushButton("Enter", self)
        self.buttons.addWidget(self.skip_btn, 1)

        self.taxa_list = []
        self.suggestions_info = read_wiki_file(INFO_PATH, INFO_FNAME)

    def compare_mismatch(self, taxa_iter, compare_window):

        next_taxa = next(taxa_iter, None)
        print(next_taxa)
        if next_taxa:
            if type(next_taxa) == str:
                self.taxa_list.append(next_taxa)
                self.compare_mismatch(taxa_iter, compare_window)
            else:
                db_taxa = next_taxa[0]

                i = 1

                next_taxa = self.remove_chosen_entries(next_taxa)

                self.show_suggestions(next_taxa, taxa_iter, i)

                self.taxa_label.setText(db_taxa)
                compare_window.setGeometry(100, 100, 600, 400)
                compare_window.show()
        else:
            # End of file, record results
            write_file(self.taxa_list, DB_PATH, OUTPUT_PATH)
            # Open main menu
            self.parent().show()
            self.close()

    def make_confirm_function(self, suggestion, taxa_iter, compare_window):
        def confirm_suggestion():
            print("You chose:", suggestion)
            self.taxa_list.append(suggestion)

            self.line_edit.clear()
            self.removed_suggestions.clear()

            self.compare_mismatch(taxa_iter, compare_window)

        return confirm_suggestion

    def remove_chosen_entries(self, taxa):

        print(f"NEXT TAXA: {taxa}")
        taxa_name = taxa[0]

        for taxa_suggestions in taxa:
            print(f"TAXA_SUGGESTIONS: {taxa_suggestions}")
            if type(taxa_suggestions) != str:
                for suggestion in taxa_suggestions:
                    # Remove suggestions that have already been chosen
                    # TODO: do this for entire suggestions list at beginning of new taxa to avoid changing once clicking
                    if suggestion in self.taxa_list:
                        self.removed_suggestions.append(suggestion)
                        print(f"{suggestion} previously selected.")
                        taxa_suggestions.remove(suggestion)
                        continue
        return taxa

    def confirm_text(self, suggestion, taxa_iter, compare_window):
        # TODO: close window more intelligently
        if not suggestion:
            print('hi')

        print("You chose:", suggestion)
        self.taxa_list.append(suggestion)

        self.line_edit.clear()

        self.compare_mismatch(taxa_iter, compare_window)

    def create_wiki_label(self, taxa):
        # Create text box from wiki
        label = QLabel()
        label.setScaledContents(True)
        label.setText(self.suggestions_info[taxa])
        label.setMaximumSize(200, 200)
        label.setMargin(5)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.show()

        # Create scroll area for text box
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setFixedHeight(200)

        return scroll

    def create_wiki_layout(self, taxa, taxa_iter):
        # TODO: reimplement images?

        # url_image = get_wiki_image(taxa)
        # Get wiki information, and image if it's available
        # try:
        #     if url_image != 0:
        #         image = QImage()
        #         image.loadFromData(requests.get(url_image).content)
        #
        #         label.setPixmap(QPixmap(image))
        # except:
        #     label.setText("Cannot find " + taxa)

        # Create base layout for taxa selection
        taxa_layout = QVBoxLayout()
        taxa_layout.setAlignment(Qt.AlignCenter)

        # Create taxa selection button
        btn = QPushButton(taxa, self)
        btn.setStyleSheet("padding: 20px;")
        # btn.adjustSize()
        f = self.make_confirm_function(taxa, taxa_iter, self)
        btn.clicked.connect(f)
        btn.clicked.connect(lambda s=1: print(s))
        taxa_layout.addWidget(btn)

        scroll = self.create_wiki_label(taxa)
        taxa_layout.addWidget(scroll)

        return taxa_layout

    def show_suggestions(self, next_taxa, taxa_iter, i):

        # Clear old buttons + images
        for j in reversed(range(self.suggestions_layout.count())):
            layout = self.suggestions_layout.itemAt(j).layout()
            for k in reversed(range(layout.count())):
                layout.itemAt(k).widget().setParent(None)

        print(f"show_suggestions - next_taxa: {next_taxa}")
        print(f"Removed category_suggestions: {self.removed_suggestions}")

        self.removed_suggestions_label.setParent(None)
        if self.removed_suggestions:
            self.removed_suggestions_label.setText(str(self.removed_suggestions))
            self.taxa_layout.addWidget(self.removed_suggestions_label, 1)

        num_suggestions = [len(next_taxa[1]), len(next_taxa[2]), len(next_taxa[3])]

        if i <= 3:
            category_suggestions = next_taxa[i]
            while not category_suggestions:
                i += 1
                if i > 3:
                    break
                category_suggestions = next_taxa[i]

            if i <= 3:
                # reset and load taxa, if possible
                self.taxa_info.setParent(None)
                self.taxa_info = self.create_wiki_label(next_taxa[0])
                self.taxa_layout.insertWidget(0, self.taxa_info, 1)

                for suggestion in category_suggestions:

                    print(suggestion)

                    # Add info and image widget to page
                    suggestion_layout = self.create_wiki_layout(suggestion, taxa_iter)
                    self.suggestions_layout.addLayout(suggestion_layout)

                # Check that all category_suggestions were not removed by being previously picked, continue if they were
                if not category_suggestions:
                    i += 1
                    self.show_suggestions(next_taxa, taxa_iter, i)

            # TODO: get this logic outside of the category_suggestions, so it's not doing it every time
            # Set button text
            self.similar_entries_count.setText(f"Similar Entries: {num_suggestions[0]}")
            self.same_species_count.setText(f"Same Species: {num_suggestions[1]}")
            self.same_genus_count.setText(f"Same Genus: {num_suggestions[2]}")

            # Unlink buttons, if needed
            try:
                self.similar_entries_count.clicked.disconnect()
            except Exception:
                pass
            try:
                self.same_species_count.clicked.disconnect()
            except Exception:
                pass
            try:
                self.same_genus_count.clicked.disconnect()
            except Exception:
                pass

            # Link buttons, if category_suggestions exist for those categories
            if num_suggestions[0] > 0: self.similar_entries_count.clicked.connect(
                lambda: self.show_suggestions(next_taxa, taxa_iter, 1))
            if num_suggestions[1] > 0: self.same_species_count.clicked.connect(
                lambda: self.show_suggestions(next_taxa, taxa_iter, 2))
            if num_suggestions[2] > 0: self.same_genus_count.clicked.connect(
                lambda: self.show_suggestions(next_taxa, taxa_iter, 3))

        if i == 1:
            self.setWindowTitle("Similar Entries")
        elif i == 2:
            self.setWindowTitle("Same Species")
        elif i == 3:
            self.setWindowTitle("Same Genus")
        else:
            self.setWindowTitle("No Suggestions")

        # Disconnect if already connected
        try:
            self.continue_btn.clicked.disconnect()
        except Exception:
            pass

        if i <= 3:
            self.continue_btn.setText("None of these")
            self.continue_btn.clicked.connect(lambda: self.show_suggestions(next_taxa, taxa_iter, i + 1))
        else:
            self.continue_btn.setText("Back")
            self.continue_btn.clicked.connect(lambda: self.show_suggestions(next_taxa, taxa_iter, 1))

        # Disconnect if already connected
        try:
            self.skip_btn.clicked.disconnect()
        except Exception:
            pass

        # Chooses the text entry box
        self.skip_btn.clicked.connect(lambda: self.confirm_text(self.line_edit.text(), taxa_iter, self))


def main():
    app = QApplication(sys.argv)
    main = MainMenu()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
