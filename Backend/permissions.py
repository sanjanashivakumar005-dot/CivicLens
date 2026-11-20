
# =========================================================
# CivicLens - Role-Based Permissions
# =========================================================

ROLE_PERMISSIONS = {
    "citizen": [
        "create_issue",
        "view_own_issues",
        "view_all_issues",
        "upvote_issue",
        "view_issue_history"
    ],

    "staff": [
        "view_all_issues",
        "view_assigned_issues",
        "update_issue_status",
        "view_issue_history"
    ],

    "admin": [
        "create_issue",
        "view_all_issues",
        "view_assigned_issues",
        "update_issue_status",
        "assign_issue",
        "manage_users",
        "delete_issue",
        "view_analytics",
        "view_issue_history",
        "upvote_issue"
    ]
}


def has_permission(role, permission):
    """
    Check whether a role has a specific permission.
    """
    if role not in ROLE_PERMISSIONS:
        return False

    return permission in ROLE_PERMISSIONS[role]


def get_permissions(role):
    """
    Return all permissions available to a role.
    """
    return ROLE_PERMISSIONS.get(role, [])


def check_permission(role, permission):
    """
    Return a structured permission result.
    """
    allowed = has_permission(role, permission)

    return {
        "allowed": allowed,
        "role": role,
        "permission": permission,
        "message": (
            "Permission granted"
            if allowed
            else "Permission denied"
        )
    }
