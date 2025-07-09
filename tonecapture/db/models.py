"""tonecapture.db.models"""

import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# --- Device and Manufacturer Models ---


class Manufacturer(Base):
    """Represents a manufacturer of audio equipment."""

    __tablename__ = "manufacturers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)

    def __repr__(self):
        return f"<Manufacturer(name='{self.name}')>"


class Device(Base):
    """A concrete base model for an equipment device using Single Table Inheritance."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String(50))  # Discriminator for STI

    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    manufacturer = relationship("Manufacturer")

    __mapper_args__ = {
        "polymorphic_identity": "device",
        "polymorphic_on": "type",
    }

    def __repr__(self):
        manufacturer_name = (
            self.manufacturer.name if self.manufacturer is not None else ""
        )
        return f"<{self.__class__.__name__}(name='{(manufacturer_name + ' ' + self.name).strip()}')>"


class Speaker(Device):
    """Represents a speaker model."""

    __mapper_args__ = {"polymorphic_identity": "speaker"}


class Microphone(Device):
    """Represents a microphone model."""

    __mapper_args__ = {"polymorphic_identity": "microphone"}


class Amplifier(Device):
    """Represents an amplifier model."""

    __mapper_args__ = {"polymorphic_identity": "amplifier"}


class Pedal(Device):
    """Represents a pedal/stompbox model."""

    __mapper_args__ = {"polymorphic_identity": "pedal"}


# --- ToneFile Models with Joined Table Inheritance ---


class ToneFile(Base):
    """Base model for a tone file, using joined-table inheritance."""

    __tablename__ = "tone_files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False, unique=True)
    filename = Column(String, nullable=False)
    notes = Column(String)

    # For audio analysis (Phase 2)
    embedding = Column(LargeBinary, nullable=True)

    # This column will determine which subclass to instantiate (e.g., 'ir', 'nam').
    file_type = Column(String(50))

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    __mapper_args__ = {
        "polymorphic_identity": "tone_file",
        "polymorphic_on": "file_type",
    }

    device_links = relationship(
        "ToneFileDeviceLink",
        back_populates="tone_file",
        cascade="all, delete-orphan",
        order_by="ToneFileDeviceLink.order",
    )

    def __repr__(self):
        return f"<ToneFile(id={self.id}, filename='{self.filename}')>"

    @property
    def devices(self):
        """Returns a list of all associated device objects, ordered by signal chain."""
        return [link.device for link in self.device_links if link.device is not None]


class ToneFileDeviceLink(Base):
    """Association object linking a ToneFile to a specific Device."""

    __tablename__ = "tone_file_device_links"

    id = Column(Integer, primary_key=True)
    tone_file_id = Column(
        Integer, ForeignKey("tone_files.id"), nullable=False, index=True
    )

    # A single, non-nullable Foreign Key to the polymorphic devices table.
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)

    # Metadata about the link
    role = Column(String)  # e.g., "Main Mic", "Room Mic", "Pre-Gain", "Post-Gain"
    order = Column(Integer, default=0, nullable=False)  # For signal chain order

    # Relationships
    tone_file = relationship("ToneFile", back_populates="device_links")
    # This is now a polymorphic relationship. SQLAlchemy will automatically fetch
    # the correct subclass (Speaker, Microphone, etc.).
    device = relationship("Device")


class IrFile(ToneFile):
    """
    Represents an Impulse Response (IR) file.
    Inherits device associations from ToneFile.
    """

    __tablename__ = "ir_files"

    id = Column(Integer, ForeignKey("tone_files.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "ir",
    }

    def __repr__(self):
        num_speakers = len(self.speakers)
        num_mics = len(self.microphones)
        return f"<IrFile(filename='{self.filename}', speakers={num_speakers}, mics={num_mics})>"

    @property
    def speakers(self):
        """Helper property to get all speakers associated with this IR."""
        return [
            link.device
            for link in self.device_links
            if isinstance(link.device, Speaker)
        ]

    @property
    def microphones(self):
        """Helper property to get all microphones associated with this IR."""
        return [
            link.device
            for link in self.device_links
            if isinstance(link.device, Microphone)
        ]


class NamFile(ToneFile):
    """
    Represents a Neural Amp Modeler (NAM) capture file.
    Inherits device associations from ToneFile.
    """

    __tablename__ = "nam_files"

    id = Column(Integer, ForeignKey("tone_files.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "nam",
    }

    def __repr__(self):
        num_amps = len(self.amplifiers)
        num_speakers = len(self.speakers)
        num_pedals = len(self.pedals)
        return f"<NamFile(filename='{self.filename}', amps={num_amps}, speakers={num_speakers}, pedals={num_pedals})>"

    @property
    def amplifiers(self):
        """Helper property to get all amplifiers associated with this NAM file."""
        return [
            link.device
            for link in self.device_links
            if isinstance(link.device, Amplifier)
        ]

    @property
    def speakers(self):
        """Helper property to get all speakers associated with this NAM file."""
        return [
            link.device
            for link in self.device_links
            if isinstance(link.device, Speaker)
        ]

    @property
    def pedals(self):
        """Helper property to get all pedals associated with this NAM file."""
        return [
            link.device for link in self.device_links if isinstance(link.device, Pedal)
        ]
