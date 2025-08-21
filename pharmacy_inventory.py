import sys
import csv
import json
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTableWidget, QTableWidgetItem, 
                               QPushButton, QLineEdit, QLabel, QMessageBox,
                               QTabWidget, QGroupBox, QFormLayout, QSpinBox,
                               QComboBox, QHeaderView)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QIcon

class PharmacyInventoryManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inventory = []
        self.low_stock_threshold = 10
        self.filename = "pharmacy_inventory.csv"
        
        self.setWindowTitle("UPS Pharmacy - Inventory Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        # Load existing inventory
        self.load_inventory()
        
        # Setup UI
        self.setup_ui()
        
        # Setup auto-save timer
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.save_inventory)
        self.autosave_timer.start(30000)  # Auto-save every 30 seconds
        
    def setup_ui(self):
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("UPS Pharmacy - Inventory Management System")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 15px; background-color: #2c3e50; color: white;")
        main_layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Inventory tab
        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(inventory_tab)
        
        # Search area
        search_group = QGroupBox("Search Inventory")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or ID...")
        self.search_input.textChanged.connect(self.filter_inventory)
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.filter_inventory)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        inventory_layout.addWidget(search_group)
        
        # Inventory table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Quantity", "Price", "Category", "Last Updated"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        inventory_layout.addWidget(self.table)
        
        # Button group
        button_group = QGroupBox("Inventory Actions")
        button_layout = QHBoxLayout(button_group)
        
        add_btn = QPushButton("Add New Item")
        add_btn.clicked.connect(self.show_add_dialog)
        
        update_btn = QPushButton("Update Quantity")
        update_btn.clicked.connect(self.show_update_dialog)
        
        low_stock_btn = QPushButton("Check Low Stock")
        low_stock_btn.clicked.connect(self.check_low_stock)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(low_stock_btn)
        inventory_layout.addWidget(button_group)
        
        tabs.addTab(inventory_tab, "Inventory Management")
        
        # Statistics tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.stats_label)
        tabs.addTab(stats_tab, "Statistics")
        
        # Update the display
        self.update_display()
        self.update_stats()
        
    def load_inventory(self):
        try:
            with open(self.filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                self.inventory = list(reader)
                # Convert quantity to integer
                for item in self.inventory:
                    item['quantity'] = int(item['quantity'])
        except FileNotFoundError:
            # Initialize with some sample data if file doesn't exist
            self.inventory = [
                {"id": "1001", "name": "Aspirin", "quantity": 45, "price": "5.99", "category": "Pain Relief", "last_updated": datetime.now().strftime("%Y-%m-%d")},
                {"id": "1002", "name": "Amoxicillin", "quantity": 8, "price": "12.50", "category": "Antibiotic", "last_updated": datetime.now().strftime("%Y-%m-%d")},
                {"id": "1003", "name": "Lipitor", "quantity": 22, "price": "15.75", "category": "Cholesterol", "last_updated": datetime.now().strftime("%Y-%m-%d")},
                {"id": "1004", "name": "Ventolin", "quantity": 5, "price": "23.40", "category": "Asthma", "last_updated": datetime.now().strftime("%Y-%m-%d")},
                {"id": "1005", "name": "Metformin", "quantity": 34, "price": "8.99", "category": "Diabetes", "last_updated": datetime.now().strftime("%Y-%m-%d")}
            ]
            self.save_inventory()
    
    def save_inventory(self):
        with open(self.filename, 'w', newline='') as file:
            fieldnames = ["id", "name", "quantity", "price", "category", "last_updated"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.inventory)
    
    def update_display(self):
        self.table.setRowCount(len(self.inventory))
        for row, item in enumerate(self.inventory):
            self.table.setItem(row, 0, QTableWidgetItem(item['id']))
            self.table.setItem(row, 1, QTableWidgetItem(item['name']))
            
            # Highlight low stock items in red
            quantity_item = QTableWidgetItem(str(item['quantity']))
            if item['quantity'] < self.low_stock_threshold:
                quantity_item.setBackground(QColor(255, 200, 200))
            self.table.setItem(row, 2, quantity_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(item['price']))
            self.table.setItem(row, 4, QTableWidgetItem(item['category']))
            self.table.setItem(row, 5, QTableWidgetItem(item['last_updated']))
    
    def update_stats(self):
        total_items = len(self.inventory)
        low_stock_count = sum(1 for item in self.inventory if item['quantity'] < self.low_stock_threshold)
        total_quantity = sum(item['quantity'] for item in self.inventory)
        
        stats_text = f"""
        <h2>Inventory Statistics</h2>
        <p><b>Total Items:</b> {total_items}</p>
        <p><b>Total Quantity:</b> {total_quantity}</p>
        <p><b>Low Stock Items:</b> {low_stock_count}</p>
        <p><b>Last Updated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
        """
        self.stats_label.setText(stats_text)
    
    def filter_inventory(self):
        search_text = self.search_input.text().lower()
        if not search_text:
            self.update_display()
            return
            
        filtered_inventory = [
            item for item in self.inventory 
            if search_text in item['name'].lower() or search_text in item['id'].lower()
        ]
        
        self.table.setRowCount(len(filtered_inventory))
        for row, item in enumerate(filtered_inventory):
            self.table.setItem(row, 0, QTableWidgetItem(item['id']))
            self.table.setItem(row, 1, QTableWidgetItem(item['name']))
            
            quantity_item = QTableWidgetItem(str(item['quantity']))
            if item['quantity'] < self.low_stock_threshold:
                quantity_item.setBackground(QColor(255, 200, 200))
            self.table.setItem(row, 2, quantity_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(item['price']))
            self.table.setItem(row, 4, QTableWidgetItem(item['category']))
            self.table.setItem(row, 5, QTableWidgetItem(item['last_updated']))
    
    def show_add_dialog(self):
        dialog = QWidget()
        dialog.setWindowTitle("Add New Item")
        dialog.setGeometry(400, 400, 400, 300)
        layout = QFormLayout(dialog)
        
        id_input = QLineEdit()
        name_input = QLineEdit()
        quantity_input = QSpinBox()
        quantity_input.setRange(0, 1000)
        price_input = QLineEdit()
        category_input = QComboBox()
        category_input.addItems(["Pain Relief", "Antibiotic", "Cholesterol", "Asthma", "Diabetes", "Other"])
        
        layout.addRow("ID:", id_input)
        layout.addRow("Name:", name_input)
        layout.addRow("Quantity:", quantity_input)
        layout.addRow("Price:", price_input)
        layout.addRow("Category:", category_input)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Item")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
        
        def add_item():
            new_item = {
                "id": id_input.text(),
                "name": name_input.text(),
                "quantity": quantity_input.value(),
                "price": price_input.text(),
                "category": category_input.currentText(),
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
            self.inventory.append(new_item)
            self.save_inventory()
            self.update_display()
            self.update_stats()
            dialog.close()
            QMessageBox.information(self, "Success", "Item added successfully!")
        
        add_button.clicked.connect(add_item)
        cancel_button.clicked.connect(dialog.close)
        
        dialog.setLayout(layout)
        dialog.show()
    
    def show_update_dialog(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select an item to update.")
            return
            
        item_id = self.table.item(selected_row, 0).text()
        item = next((i for i in self.inventory if i['id'] == item_id), None)
        
        if not item:
            return
            
        dialog = QWidget()
        dialog.setWindowTitle("Update Quantity")
        dialog.setGeometry(400, 400, 300, 150)
        layout = QFormLayout(dialog)
        
        current_qty_label = QLabel(f"Current Quantity: {item['quantity']}")
        new_quantity_input = QSpinBox()
        new_quantity_input.setRange(0, 1000)
        new_quantity_input.setValue(item['quantity'])
        
        layout.addRow(current_qty_label)
        layout.addRow("New Quantity:", new_quantity_input)
        
        button_layout = QHBoxLayout()
        update_button = QPushButton("Update")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(update_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
        
        def update_item():
            item['quantity'] = new_quantity_input.value()
            item['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            self.save_inventory()
            self.update_display()
            self.update_stats()
            dialog.close()
            QMessageBox.information(self, "Success", "Quantity updated successfully!")
        
        update_button.clicked.connect(update_item)
        cancel_button.clicked.connect(dialog.close)
        
        dialog.setLayout(layout)
        dialog.show()
    
    def check_low_stock(self):
        low_stock_items = [item for item in self.inventory if item['quantity'] < self.low_stock_threshold]
        
        if not low_stock_items:
            QMessageBox.information(self, "Stock Status", "No items are low in stock.")
            return
            
        message = "The following items are low in stock:\n\n"
        for item in low_stock_items:
            message += f"{item['name']} (ID: {item['id']}): {item['quantity']} remaining\n"
            
        QMessageBox.warning(self, "Low Stock Alert", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PharmacyInventoryManager()
    window.show()
    sys.exit(app.exec())