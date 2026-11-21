
from datetime import datetime

from database.connection import SessionLocal
from database.models import Issue, StatusLog, Vote, User


VALID_CATEGORIES = [
    "Roads",
    "Water",
    "Electricity",
    "Sanitation",
    "Public Spaces"
]

VALID_SEVERITIES = ["Low", "Medium", "High", "Critical"]

VALID_STATUSES = [
    "Pending Review",
    "Assigned",
    "In Progress",
    "Resolved",
    "Reopened"
]


# =========================================================
# 1. CREATE ISSUE
# =========================================================

def create_issue(
    user_id,
    title,
    category,
    description,
    latitude=None,
    longitude=None,
    address=None,
    ward_zone=None,
    severity="Medium"
):
    db = SessionLocal()

   try:
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"success": False, "message": "User not found"}

    if not user.is_active:
        return {"success": False, "message": "User account is inactive"}

    if category not in VALID_CATEGORIES:
        return {"success": False, "message": "Invalid issue category"}

    if severity not in VALID_SEVERITIES:
        return {"success": False, "message": "Invalid severity level"}

    if not title or not title.strip():
        return {"success": False, "message": "Issue title is required"}

    if not description or not description.strip():
        return {"success": False, "message": "Description is required"}try:
    # Validate issue information
    if category not in VALID_CATEGORIES:
        return {"success": False, "message": "Invalid issue category"}

    if severity not in VALID_SEVERITIES:
        return {"success": False, "message": "Invalid severity level"}

    if not title or not title.strip():
        return {"success": False, "message": "Issue title is required"}

    if not description or not description.strip():
        return {"success": False, "message": "Description is required"}

    # Check whether the user exists
    user = db.query(User).filter(User.user_id == user_id).first()

    # If the user does not exist, create a default citizen account
    if not user:
        user = User(
            user_id=user_id,
            name="CivicLens Citizen",
            role="citizen",
            is_active=True
        )
        db.add(user)
        db.flush()

    elif not user.is_active:
        return {"success": False, "message": "User account is inactive"}
        new_issue = Issue(
            user_id=user_id,
            title=title.strip(),
            category=category,
            description=description.strip(),
            latitude=latitude,
            longitude=longitude,
            address=address,
            ward_zone=ward_zone,
            severity=severity,
            status="Pending Review",
            upvotes_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)

        return {
            "success": True,
            "message": "Issue reported successfully",
            "issue_id": new_issue.issue_id,
            "status": new_issue.status
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

    finally:
        db.close()


# =========================================================
# 2. GET ALL ISSUES
# =========================================================

def get_all_issues():
    db = SessionLocal()

    try:
        issues = db.query(Issue).order_by(
            Issue.created_at.desc()
        ).all()

        return {
            "success": True,
            "total_issues": len(issues),
            "issues": [
                {
                    "issue_id": issue.issue_id,
                    "title": issue.title,
                    "category": issue.category,
                    "description": issue.description,
                    "severity": issue.severity,
                    "status": issue.status,
                    "address": issue.address,
                    "ward_zone": issue.ward_zone,
                    "upvotes_count": issue.upvotes_count,
                    "created_at": str(issue.created_at)
                }
                for issue in issues
            ]
        }

    except Exception as e:
        return {"success": False, "message": str(e)}

    finally:
        db.close()


# =========================================================
# 3. GET ISSUE BY ID
# =========================================================

def get_issue_by_id(issue_id):
    db = SessionLocal()

    try:
        issue = db.query(Issue).filter(
            Issue.issue_id == issue_id
        ).first()

        if not issue:
            return {"success": False, "message": "Issue not found"}

        return {
            "success": True,
            "issue": {
                "issue_id": issue.issue_id,
                "user_id": issue.user_id,
                "title": issue.title,
                "category": issue.category,
                "description": issue.description,
                "latitude": issue.latitude,
                "longitude": issue.longitude,
                "address": issue.address,
                "ward_zone": issue.ward_zone,
                "severity": issue.severity,
                "status": issue.status,
                "upvotes_count": issue.upvotes_count,
                "created_at": str(issue.created_at),
                "updated_at": str(issue.updated_at),
                "resolved_at": (
                    str(issue.resolved_at)
                    if issue.resolved_at else None
                )
            }
        }

    except Exception as e:
        return {"success": False, "message": str(e)}

    finally:
        db.close()


# =========================================================
# 4. UPDATE ISSUE STATUS
# =========================================================

def update_issue_status(
    issue_id,
    updated_by,
    new_status,
    remarks=None
):
    db = SessionLocal()

    try:
        issue = db.query(Issue).filter(
            Issue.issue_id == issue_id
        ).first()

        if not issue:
            return {"success": False, "message": "Issue not found"}

        updater = db.query(User).filter(
            User.user_id == updated_by
        ).first()

        if not updater:
            return {"success": False, "message": "Updater not found"}

        if new_status not in VALID_STATUSES:
            return {"success": False, "message": "Invalid status"}

        if issue.status == new_status:
            return {
                "success": False,
                "message": f"Issue is already in '{new_status}' status"
            }

        old_status = issue.status

        issue.status = new_status
        issue.updated_at = datetime.utcnow()

        if new_status == "Resolved":
            issue.resolved_at = datetime.utcnow()

        elif new_status == "Reopened":
            issue.resolved_at = None

        status_log = StatusLog(
            issue_id=issue_id,
            updated_by=updated_by,
            old_status=old_status,
            new_status=new_status,
            remarks=remarks,
            timestamp=datetime.utcnow()
        )

        db.add(status_log)
        db.commit()

        return {
            "success": True,
            "message": "Issue status updated successfully",
            "issue_id": issue_id,
            "old_status": old_status,
            "new_status": new_status
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

    finally:
        db.close()


# =========================================================
# 5. GET ISSUE HISTORY
# =========================================================

def get_issue_history(issue_id):
    db = SessionLocal()

    try:
        issue = db.query(Issue).filter(
            Issue.issue_id == issue_id
        ).first()

        if not issue:
            return {"success": False, "message": "Issue not found"}

        history = db.query(StatusLog).filter(
            StatusLog.issue_id == issue_id
        ).order_by(StatusLog.timestamp.asc()).all()

        return {
            "success": True,
            "issue_id": issue_id,
            "history": [
                {
                    "log_id": log.log_id,
                    "old_status": log.old_status,
                    "new_status": log.new_status,
                    "remarks": log.remarks,
                    "updated_by": log.updated_by,
                    "timestamp": str(log.timestamp)
                }
                for log in history
            ]
        }

    except Exception as e:
        return {"success": False, "message": str(e)}

    finally:
        db.close()


# =========================================================
# 6. GET USER ISSUES
# =========================================================

def get_user_issues(user_id):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            return {"success": False, "message": "User not found"}

        issues = db.query(Issue).filter(
            Issue.user_id == user_id
        ).order_by(Issue.created_at.desc()).all()

        return {
            "success": True,
            "user_id": user_id,
            "total_issues": len(issues),
            "issues": [
                {
                    "issue_id": issue.issue_id,
                    "title": issue.title,
                    "category": issue.category,
                    "description": issue.description,
                    "severity": issue.severity,
                    "status": issue.status,
                    "address": issue.address,
                    "ward_zone": issue.ward_zone,
                    "created_at": str(issue.created_at)
                }
                for issue in issues
            ]
        }

    except Exception as e:
        return {"success": False, "message": str(e)}

    finally:
        db.close()


# =========================================================
# 7. UPVOTE ISSUE
# =========================================================

def upvote_issue(issue_id, user_id):
    db = SessionLocal()

    try:
        issue = db.query(Issue).filter(
            Issue.issue_id == issue_id
        ).first()

        if not issue:
            return {"success": False, "message": "Issue not found"}

        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            return {"success": False, "message": "User not found"}

        existing_vote = db.query(Vote).filter(
            Vote.issue_id == issue_id,
            Vote.user_id == user_id
        ).first()

        if existing_vote:
            return {
                "success": False,
                "message": "You have already upvoted this issue"
            }

        new_vote = Vote(
            issue_id=issue_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )

        db.add(new_vote)
        issue.upvotes_count = (issue.upvotes_count or 0) + 1

        db.commit()

        return {
            "success": True,
            "message": "Issue upvoted successfully",
            "issue_id": issue_id,
            "upvotes_count": issue.upvotes_count
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

    finally:
        db.close()


# =========================================================
# 8. ASSIGN ISSUE TO STAFF
# =========================================================

def assign_issue(issue_id, staff_id, assigned_by):
    db = SessionLocal()

    try:
        issue = db.query(Issue).filter(
            Issue.issue_id == issue_id
        ).first()

        if not issue:
            return {"success": False, "message": "Issue not found"}

        staff = db.query(User).filter(
            User.user_id == staff_id
        ).first()

        if not staff:
            return {"success": False, "message": "Staff member not found"}

        admin = db.query(User).filter(
            User.user_id == assigned_by
        ).first()

        if not admin:
            return {"success": False, "message": "Admin user not found"}

        if admin.role != "admin":
            return {
                "success": False,
                "message": "Only admins can assign issues"
            }

        if staff.role != "staff":
            return {
                "success": False,
                "message": "Selected user is not a staff member"
            }

        if not staff.is_active:
            return {
                "success": False,
                "message": "Staff account is inactive"
            }

        old_status = issue.status

        issue.assigned_staff_id = staff_id
        issue.status = "Assigned"
        issue.updated_at = datetime.utcnow()

        if old_status != "Assigned":
            status_log = StatusLog(
                issue_id=issue_id,
                updated_by=assigned_by,
                old_status=old_status,
                new_status="Assigned",
                remarks=f"Issue assigned to staff member {staff.name}",
                timestamp=datetime.utcnow()
            )

            db.add(status_log)

        db.commit()

        return {
            "success": True,
            "message": "Issue assigned successfully",
            "issue_id": issue_id,
            "assigned_staff_id": staff_id,
            "staff_name": staff.name,
            "status": issue.status
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

    finally:
        db.close()

# =========================================================
# 9. GET ISSUES ASSIGNED TO STAFF
# =========================================================

def get_assigned_issues(staff_id):
    db = SessionLocal()

    try:
        staff = db.query(User).filter(
            User.user_id == staff_id
        ).first()

        if not staff:
            return {
                "success": False,
                "message": "Staff member not found"
            }

        if staff.role != "staff":
            return {
                "success": False,
                "message": "User is not a staff member"
            }

        issues = db.query(Issue).filter(
            Issue.assigned_staff_id == staff_id
        ).order_by(Issue.created_at.desc()).all()

        return {
            "success": True,
            "staff_id": staff_id,
            "staff_name": staff.name,
            "total_assigned": len(issues),
            "issues": [
                {
                    "issue_id": issue.issue_id,
                    "title": issue.title,
                    "category": issue.category,
                    "description": issue.description,
                    "severity": issue.severity,
                    "status": issue.status,
                    "address": issue.address,
                    "ward_zone": issue.ward_zone,
                    "upvotes_count": issue.upvotes_count,
                    "created_at": str(issue.created_at)
                }
                for issue in issues
            ]
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

    finally:
        db.close()
