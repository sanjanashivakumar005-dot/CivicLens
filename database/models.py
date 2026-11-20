
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship

from database.connection import Base


# =========================================================
# 1. USERS TABLE
# =========================================================

class User(Base):

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, nullable=False, index=True)

    phone = Column(String(20), unique=True, nullable=True)

    password_hash = Column(String(255), nullable=False)

    role = Column(String(20), default="citizen", nullable=False)

    ward_zone = Column(String(100), nullable=True)

    is_active = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reported_issues = relationship(
        "Issue",
        back_populates="reporter",
        foreign_keys="Issue.user_id"
    )

    votes = relationship(
        "Vote",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# =========================================================
# 2. ISSUES TABLE
# =========================================================

class Issue(Base):

    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    assigned_staff_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True
    )

    title = Column(String(200), nullable=False)

    category = Column(String(50), nullable=False)

    description = Column(Text, nullable=False)

    latitude = Column(Float, nullable=True)

    longitude = Column(Float, nullable=True)

    address = Column(String(300), nullable=True)

    ward_zone = Column(String(100), nullable=True)

    status = Column(
        String(30),
        default="Pending Review",
        nullable=False,
        index=True
    )

    severity = Column(
        Integer,
        default=1,
        nullable=False
    )

    upvotes_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    reporter = relationship(
        "User",
        back_populates="reported_issues",
        foreign_keys=[user_id]
    )

    assigned_staff = relationship(
        "User",
        foreign_keys=[assigned_staff_id]
    )

    media = relationship(
        "Media",
        back_populates="issue",
        cascade="all, delete-orphan"
    )

    status_logs = relationship(
        "StatusLog",
        back_populates="issue",
        cascade="all, delete-orphan",
        order_by="StatusLog.timestamp"
    )

    votes = relationship(
        "Vote",
        back_populates="issue",
        cascade="all, delete-orphan"
    )


# =========================================================
# 3. MEDIA TABLE
# =========================================================

class Media(Base):

    __tablename__ = "media"

    media_id = Column(Integer, primary_key=True, autoincrement=True)

    issue_id = Column(
        Integer,
        ForeignKey("issues.issue_id"),
        nullable=False,
        index=True
    )

    file_path = Column(String(500), nullable=False)

    media_type = Column(
        String(30),
        default="before_evidence",
        nullable=False
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship
    issue = relationship(
        "Issue",
        back_populates="media"
    )


# =========================================================
# 4. STATUS LOGS TABLE
# =========================================================

class StatusLog(Base):

    __tablename__ = "status_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)

    issue_id = Column(
        Integer,
        ForeignKey("issues.issue_id"),
        nullable=False,
        index=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True
    )

    old_status = Column(String(30), nullable=True)

    new_status = Column(String(30), nullable=False)

    remarks = Column(Text, nullable=True)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    issue = relationship(
        "Issue",
        back_populates="status_logs"
    )

    updater = relationship(
        "User"
    )


# =========================================================
# 5. VOTES TABLE
# =========================================================

class Vote(Base):

    __tablename__ = "votes"

    vote_id = Column(Integer, primary_key=True, autoincrement=True)

    issue_id = Column(
        Integer,
        ForeignKey("issues.issue_id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Prevent one user from voting multiple times
    __table_args__ = (
        UniqueConstraint(
            "issue_id",
            "user_id",
            name="unique_issue_vote"
        ),
        Index("idx_votes_issue_user", "issue_id", "user_id"),
    )

    # Relationships
    issue = relationship(
        "Issue",
        back_populates="votes"
    )

    user = relationship(
        "User",
        back_populates="votes"
    )
