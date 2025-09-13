# This script is solely made for previewing the plot view
import sys
from PySide6.QtWidgets import QApplication
from plot_view import PlotView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the plot view
    plot_view = PlotView()
    plot_view.setWindowTitle("Plot View Preview")
    plot_view.resize(800, 600)
    plot_view.show()
    
    sys.exit(app.exec())