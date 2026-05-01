import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.patient import Patient
from app.models.specialist import Specialist
from app.models.admin import Admin
from app.models.enums import GenderEnum, AdminRoleEnum

def seed_database():
    db: Session = SessionLocal()
    
    try:
        print("Seeding database...")
        default_pwd = get_password_hash("password123")
        
        # 1. Seed 1 Super Admin
        super_admin_email = "superadmin@example.com"
        if not db.query(Admin).filter(Admin.email == super_admin_email).first():
            print("Creating Super Admin...")
            superadmin = Admin(
                first_name="Super",
                last_name="Admin",
                email=super_admin_email,
                role=AdminRoleEnum.SUPER_ADMIN,
                hashed_password=default_pwd
            )
            db.add(superadmin)
            
        # 2. Seed 2 Admins
        for i in range(1, 3):
            email = f"admin{i}@example.com"
            if not db.query(Admin).filter(Admin.email == email).first():
                print(f"Creating Admin {i}...")
                admin = Admin(
                    first_name="Admin",
                    last_name=f"User{i}",
                    email=email,
                    role=AdminRoleEnum.ADMIN,
                    hashed_password=default_pwd
                )
                db.add(admin)
                
        # 3. Seed 10 Specialists
        from app.models.enums import ApprovalStatusEnum
        for i in range(1, 11):
            email = f"specialist{i}@example.com"
            existing_spec = db.query(Specialist).filter(Specialist.email == email).first()
            if not existing_spec:
                print(f"Creating Specialist {i}...")
                spec = Specialist(
                    first_name="Dr.",
                    last_name=f"Specialist{i}",
                    email=email,
                    hashed_password=default_pwd,
                    is_verified=True,
                    approval_status=ApprovalStatusEnum.APPROVED
                )
                db.add(spec)
            else:
                print(f"Updating Specialist {i}...")
                existing_spec.is_verified = True
                existing_spec.approval_status = ApprovalStatusEnum.APPROVED
                db.add(existing_spec)
                
        # 4. Seed 10 Patients
        for i in range(1, 11):
            email = f"patient{i}@example.com"
            if not db.query(Patient).filter(Patient.email == email).first():
                print(f"Creating Patient {i}...")
                pat = Patient(
                    first_name="Test",
                    last_name=f"Patient{i}",
                    date_of_birth=datetime.date(1990, 1, 1),
                    gender=GenderEnum.MALE,
                    email=email,
                    hashed_password=default_pwd
                )
                db.add(pat)

        db.commit()
        print("Seeding complete! Default password for all creates users is 'password123'.")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
