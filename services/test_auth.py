from services.auth_service import hash_password, verify_password
password = "Test@0000"

hashed_password = hash_password(password)

print("Original password:", password)
print("Hashed password:", hashed_password)

print("Correct password:", verify_password(password, hashed_password))
print("Wrong password:", verify_password("Wrong@123", hashed_password))