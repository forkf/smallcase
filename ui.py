import csv
import sys
from multiprocessing import Pool

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import market
from constants import HEADERS, LOGGER


class Worker(QThread):
    any_signal = pyqtSignal(dict)

    def __int__(self, parent=None):
        super(Worker, self).__int__(parent)
        self.is_running = True
        self.table: QTableWidget = None

    def get_table_data(self):
        if self.table is None:
            raise ValueError("self.table is None")
        rows = []
        # Iterate through rows and columns to get values
        for row in range(self.table.rowCount()):
            row_values = {}  # Store values of each row
            symbol = self.table.horizontalHeaderItem(0).text()
            for col in range(self.table.columnCount()):
                if col == 0:
                    continue
                colname = self.table.horizontalHeaderItem(col).text()
                item = self.table.item(row, col)
                colvalue = item.text() if item else ""
                row_values[colname] = colvalue
            rows[symbol] = row_values

        return rows

    def run(self):
        """ This method will query
        live market market data based on holdings.

        Returns:
            None

        """
        while True:
            market = {}
            table_data = self.get_table_data()
            if not trade_data:
                logger.warning('Trade data not found !')
                break

            coins = list(
                set(
                    [v['coin'] for k, v in trade_data.items()]
                )
            )

            for coin in coins:
                url = "https://api.wazirx.com/api/v2/tickers/{}inr".format(
                    str(coin).lower()
                )
                coin_req = requests.get(url)
                if coin_req.ok:
                    current_price = coin_req.json()['ticker']['last']
                    market.update(
                        {coin: current_price}
                    )
                else:
                    market.update(
                        {coin: 'None'}
                    )
                    logger.warning('Market link is Down.')

            self.any_signal.emit(market)

    def stop(self):
        """ This method will stop thread process

        Returns:
            None

        """
        self.is_running = False
        self.terminate()

class PopUp(QDialog):
    def __init__(self):
        super(PopUp, self).__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.value = None
        self.label = QLabel("Enter Fund Name")
        self.linedit = QLineEdit()

        buttonLayout = QHBoxLayout()
        self.submit = QPushButton("Submit")
        self.cancel = QPushButton("Cancel")
        buttonLayout.addWidget(self.submit)
        buttonLayout.addWidget(self.cancel)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.linedit)
        self.layout.addLayout(buttonLayout)

        self.submit.clicked.connect(self.trigger_submit)
        self.cancel.clicked.connect(self.close)

    def trigger_submit(self):
        self.value = self.linedit.text()
        self.close()


class FundTable(QGroupBox):
    def __init__(self, title: str, parent=None):
        super(FundTable, self).__init__(parent)

        # self.group_name = PopUp()
        # self.group_name.exec_()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # self.setTitle(self.group_name.value)
        self.setTitle(title)

        self.table_live = QTableWidget(self)
        self.table_live.verticalHeader().hide()

        self.table_live.setColumnCount(5)
        self.table_live.setHorizontalHeaderLabels(HEADERS)
        self.table_live.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        # self.buttonRemove = QPushButton("Remove Fund")
        # self.buttonEntry = QPushButton("Add Entry")
        self.buttonRefresh = QPushButton("Refresh")
        self.layout.addWidget(self.table_live)
        # self.layout.addWidget(self.buttonRemove)
        # self.layout.addWidget(self.buttonEntry)
        self.layout.addWidget(self.buttonRefresh)
        # self.buttonRemove.clicked.connect(self.remove)
        # self.buttonEntry.clicked.connect(self.add_entry)
        self.buttonRefresh.clicked.connect(self.get_latest_price)

    def remove(self):
        self.destroy()

    def add_entry(self, symbol, avg_price, share, cur_price, p_l):
        count = self.table_live.rowCount()
        self.table_live.insertRow(count)

        self.table_live.setItem(count, 0, QTableWidgetItem(str(symbol)))
        self.table_live.setItem(count, 1, QTableWidgetItem(str(share)))
        self.table_live.setItem(count, 2, QTableWidgetItem(str(avg_price)))
        self.table_live.setItem(count, 3, QTableWidgetItem(str(cur_price)))
        self.table_live.setItem(count, 4, QTableWidgetItem(str(p_l)))


    def get_latest_price(self):
        updates = self.fetch_stocks()
        # for symbol, metadata in updates.items():


    def fetch_stocks(self):
        table_data = self.get_table_data()
        symbols = list(table_data.keys())
        with Pool(10) as p:
            stock_data = p.map(market.screen_symbol, symbols)
        for fetch_data in stock_data:
            for symbol, last_price in fetch_data.items():
                table_data[symbol]["Current Price"] = last_price
                if not last_price:
                    table_data[symbol]["P/L"] = 0
                    continue
                p_l = self.calculate_p_l(table_data[symbol])
                table_data[symbol]["P/L"] = p_l
        return table_data

    @staticmethod
    def calculate_p_l(quantity, average_price, current_price):
        total_buying_cost = int(quantity) * float(average_price)
        current_value = int(quantity) * int(current_price)
        p_l = current_value - total_buying_cost
        return round(p_l, 2)

    def get_table_data(self):
        rows = {}
        # Iterate through rows and columns to get values
        for row in range(self.table_live.rowCount()):
            row_values = {}  # Store values of each row
            empty_col = False
            symbol = None

            # Get column value
            for col in range(self.table_live.columnCount()):
                colname = self.table_live.horizontalHeaderItem(col).text()
                colvalue = self.table_live.item(row, col)
                if col in [3, 4]:
                    row_values[symbol][colname] = ""
                    continue

                # Check column value exists or not
                if colvalue is None:
                    empty_col = True
                    break

                # Check if column value is empty string
                if colvalue.text() == "":
                    empty_col = True
                    break

                # Get first column value which is symbol
                if col == 0:
                    symbol = colvalue.text()
                    row_values[symbol] = {}

                row_values[symbol][colname] = colvalue.text()
            if empty_col is False:
                rows.update(row_values)
        return rows

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.setBaseSize(600, 600)

        # self.fund_widget_list = []

        # self.buttonAdd = QPushButton("Add")
        # self.buttonAdd.setFixedWidth(100)
        # self.layout.addWidget(self.buttonAdd)
        #
        # self.buttonAdd.clicked.connect(self.trigger_add)

        self.initialise()

    def initialise(self):
        self.add_new_table(title="GreenEnergy", file_name="greenenergy.csv")

    def add_new_table(self, title: str, file_name: str):
        self.table_energy = FundTable(title)
        self.layout.addWidget(self.table_energy)
        with open(file_name, 'r') as csvfile:
            csvreader = csvfile.read()
            lines = csvreader.split("\n")
            data = [x.split(",") for x in lines[1:] if x]  # Skip First Header Row
            for each in data:
                cur_price = market.screen_symbol(each[1])
                p_l = self.table_energy.calculate_p_l(
                    quantity=each[3],
                    average_price=each[2],
                    current_price=cur_price
                )
                self.table_energy.add_entry(
                    symbol=each[1],
                    avg_price=each[2],
                    share=each[3],
                    cur_price=cur_price,
                    p_l=p_l
                )





    # def trigger_add(self):
    #     self.table_live = FundTable(self)
    #     if self.table_live.group_name.value is None:
    #         return
    #     self.layout.addWidget(self.table_live)
    #     self.fund_widget_list.append(self.table_live)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()