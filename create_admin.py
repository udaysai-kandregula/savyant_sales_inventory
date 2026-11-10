"""Create an administrator interactively; password is never stored in source."""
import getpass
from services.auth_service import register_user

name = input("Admin name: ").strip()
email = input("Admin email: ").strip().lower()
password = getpass.getpass("Admin password (8+ chars): ")
confirm = getpass.getpass("Confirm password: ")
if password != confirm:
    raise SystemExit("Passwords do not match.")
result = register_user(name, email, password, role="admin")
print(result["message"])
if not result.get("success"):
    raise SystemExit(1)
