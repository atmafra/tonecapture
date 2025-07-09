"""Verify the data in the database."""

import os
import sys

from tonecapture.core.logger import logger
from tonecapture.db.database import SessionLocal, _handle_database_read_error
from tonecapture.db.models import IrFile, Manufacturer, Microphone, Speaker

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def verify_database():
    """Queries the database and prints the contents."""
    db = SessionLocal()

    try:
        logger.info("--- Manufacturers ---")
        for manufacturer in db.query(Manufacturer).all():
            logger.info(manufacturer)

        logger.info("\n--- Speakers ---")
        for speaker in db.query(Speaker).all():
            logger.info(speaker)

        logger.info("\n--- Microphones ---")
        for microphone in db.query(Microphone).all():
            logger.info(microphone)

        logger.info("\n--- IR Files ---")
        for ir_file in db.query(IrFile).all():
            logger.info(ir_file)
            logger.info(f"  Path: {ir_file.path}")
            logger.info(f"  Notes: {ir_file.notes}")
            logger.info("  Devices:")
            for link in ir_file.device_links:
                logger.info(f"    - {link.device} (as {link.role})")

    except Exception as e:
        raise _handle_database_read_error(e) from e

    finally:
        db.close()


if __name__ == "__main__":
    try:
        verify_database()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
