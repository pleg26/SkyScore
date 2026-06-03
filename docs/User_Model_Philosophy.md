# User Model Philosophy

---

## Purpose

The `User` model is the single authentication identity for the platform.
All access to the site must go through a `User` account.

Main goals:
- keep one account per person (email is unique, case-insensitive),
- separate authentication from business profiles (competitor, judge, organizer),
- support privilege hierarchy and additional roles without duplicating accounts.

---

## Current Design (Implemented)

### 1. Single identity
- `User` uses email as login identifier.
- Email is normalized (`lower`) and validated as unique.

### 2. Main role + additional roles
- `role` is the primary role.
- `roles` (JSON list) stores additional explicit roles.
- Current primary role set:
  - `ADM` (Administrator)
  - `ORG` (Organizer)
  - `COMP` (Competitor)
  - `JUD` (Judge)
  - `PUB` (Public)

### 3. Hierarchy behavior
- Effective permissions are computed with hierarchy rules.
- `ADM` implies lower privilege roles for access control.
- Helper methods are available (`has_role`, `has_any_role`, etc.).

### 4. User management UI in Database
- Admin can create and edit users in Database menu.
- Password can be set at creation and changed on update.
- Password visibility toggle is available in the form.
- Admin can delete users from list, except current logged user.

---

## Security Principles

- Self-deletion is blocked for connected user.
- Role consistency checks are enforced when a user is linked to sensitive profiles.
- Password updates require confirmation fields.

---

## What Was Migrated

- Legacy `PIL` role was replaced by `COMP`.
- Existing records were migrated to keep role consistency.
- New `roles` field was added to support explicit extra roles.

---

## Remaining Work

### Short term
- Add policy: prevent deletion of last active administrator.
- Add better audit information in User management (created date, last login, effective roles).
- Add explicit UI help text explaining primary role vs additional roles.

### Mid term
- Move from single-primary-role model to fully normalized many-to-many role model if needed.
- Add invitation flow (create account without sending plain password manually).
- Add password reset workflow (email/token) instead of only admin-driven changes.

### Long term
- Add fine-grained permission groups (feature-based permissions), not only role-based.
- Add security audit trail for user lifecycle actions (create/update/delete/password change).

---

## Decision Notes

- Current model is intentionally pragmatic and incremental.
- It supports immediate operations while preparing migration to more advanced RBAC if required.
