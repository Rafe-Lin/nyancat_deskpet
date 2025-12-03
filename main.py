import sys
import signal
from PyQt6.QtWidgets import QApplication
from pet import NyanCatPet

def main():
    # Allow Ctrl+C to exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    
    # Create the pet
    pet = NyanCatPet()
    pet.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
