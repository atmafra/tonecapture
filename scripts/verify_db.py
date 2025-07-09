"""Verify the data in the database."""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tonecapture.db.database import SessionLocal
from tonecapture.db.models import Manufacturer, Speaker, Microphone, IrFile

def verify_database():
    """Queries the database and prints the contents."""
    db = SessionLocal()

    try:
        print("--- Manufacturers ---")
        for manufacturer in db.query(Manufacturer).all():
            print(manufacturer)

        print("\n--- Speakers ---")
        for speaker in db.query(Speaker).all():
            print(speaker)

        print("\n--- Microphones ---")
        for microphone in db.query(Microphone).all():
            print(microphone)

        print("\n--- IR Files ---")
        for ir_file in db.query(IrFile).all():
            print(ir_file)
            print(f"  Path: {ir_file.path}")
            print(f"  Notes: {ir_file.notes}")
            print("  Devices:")
            for device in ir_file.devices:
                print(f"    - {device}")

    finally:
        db.close()


if __name__ == "__main__":
    verify_database()
