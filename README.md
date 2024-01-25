FastAPI application to be deployed on AWS Lambda

- Admin can view customers and MX Records of their emails' domains
- Admin can create, update, and delete customers
- Auth is done via JWT
- No API is implemented. Only the admin panel is available.

---

## Instructions

- Get a `HASHED_PASSWORD` with the output of the following commands in Python:
```python
from passlib.context import CryptContext
print(CryptContext(schemes=["bcrypt"]).hash("YOUR_PASSWORD"))
```

    
- A manually created admin user is required to access the admin panel. To create one, run the following on the relevant database:

```sql
INSERT INTO users
    (username, phone, email, hashed_password, is_active)
VALUES
    ('admin', '+11234567890', 'admin@example.com', 'HASHED_PASSWORD', true);
```

