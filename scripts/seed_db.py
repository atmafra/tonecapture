"""Seed the database with initial data."""

import os
import sys

from tonecapture.core.logger import logger
from tonecapture.db.database import SessionLocal, _handle_database_error, init_db
from tonecapture.db.models import (
    IrFile,
    Manufacturer,
    Microphone,
    Speaker,
    ToneFileDeviceLink,
)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def seed_database():
    """Creates the database and populates it with initial data."""
    # Initialize the database
    init_db()

    # Create a new session
    db = SessionLocal()

    try:
        # --- Create Manufacturers ---
        celestion = Manufacturer(name="Celestion")
        shure = Manufacturer(name="Shure")

        db.add(celestion)
        db.add(shure)
        db.commit()

        # --- Create Devices ---
        vintage30 = Speaker(name="Vintage 30", manufacturer=celestion)
        sm57 = Microphone(name="SM-57", manufacturer=shure)

        db.add(vintage30)
        db.add(sm57)
        db.commit()

        # --- Create an IR File ---
        ir_file = IrFile(
            path="/data/irs/celestion_v30_sm57.wav",
            filename="celestion_v30_sm57.wav",
            notes="A classic combination for rock and metal tones.",
        )

        db.add(ir_file)
        db.commit()

        # --- Link Devices to the IR File ---
        link1 = ToneFileDeviceLink(
            tone_file=ir_file, device=vintage30, role="Speaker", order=1
        )
        link2 = ToneFileDeviceLink(
            tone_file=ir_file, device=sm57, role="Microphone", order=2
        )

        db.add(link1)
        db.add(link2)
        db.commit()

        logger.info("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        raise _handle_database_error(e) from e

    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
