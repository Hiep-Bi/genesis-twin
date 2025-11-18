"""Unified Seed Script - Admin User + System Data for Genesis Twin"""

import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from passlib.context import CryptContext

# Add backend path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Load environment variables
load_dotenv(os.path.join(backend_path, '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/genesis_twin")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def to_json(value, default=None):
    """Convert Python objects to JSON strings for SQL insertion"""
    if value is None:
        value = default if default is not None else {}
    if isinstance(value, str):
        return value
    return json.dumps(value)


def seed_admin_user():
    """Create default admin user if not exists"""
    db = SessionLocal()
    ADMIN_USERNAME = "admin"
    ADMIN_EMAIL = "admin@genesistwin.com"
    DEFAULT_PASSWORD = "admin123"

    try:
        db.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        db.commit()

        result = db.execute(
            text("SELECT id, username, email FROM users WHERE username = :username"),
            {"username": ADMIN_USERNAME}
        ).fetchone()

        hashed_password = pwd_context.hash(DEFAULT_PASSWORD)

        if result:
            # Update existing user password to ensure it's correct
            db.execute(
                text("""
                    UPDATE users 
                    SET hashed_password = :hashed_password,
                        email = :email,
                        full_name = :full_name,
                        role = 'ADMIN',
                        is_active = TRUE,
                        updated_at = NOW()
                    WHERE username = :username
                """),
                {
                    "username": ADMIN_USERNAME,
                    "email": ADMIN_EMAIL,
                    "hashed_password": hashed_password,
                    "full_name": "System Administrator",
                }
            )
            db.commit()
            print("✅ Admin user already exists - password updated:")
            print(f"   - Username: {result.username}")
            print(f"   - Email: {ADMIN_EMAIL}")
            print(f"   - Password: {DEFAULT_PASSWORD}")
            return

        db.execute(
            text("""
                INSERT INTO users (
                    id, username, email, hashed_password, full_name,
                    role, is_active, created_at, updated_at
                ) VALUES (
                    uuid_generate_v4(), :username, :email, :hashed_password, :full_name,
                    'ADMIN', TRUE, NOW(), NOW()
                )
            """),
            {
                "username": ADMIN_USERNAME,
                "email": ADMIN_EMAIL,
                "hashed_password": hashed_password,
                "full_name": "System Administrator",
            }
        )
        db.commit()
        print("✅ Created default admin user!")
        print(f"   - Username: {ADMIN_USERNAME}")
        print(f"   - Email: {ADMIN_EMAIL}")
        print(f"   - Password: {DEFAULT_PASSWORD}")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding admin user:", e)
        raise
    finally:
        db.close()

def seed_factories():
    db = SessionLocal()
    try:
        print("Seeding factories...")
        # Keep the default factory
        db.execute(text("DELETE FROM factories WHERE name != 'Genesis Factory 01'"))

        factories_data = [
            {"name": "Factory Alpha", "location": "Industrial Park East"},
            {"name": "Factory Beta", "location": "Innovation Hub West"}
        ]

        for factory in factories_data:
            existing_factory = db.execute(text("SELECT id FROM factories WHERE name = :name"), {"name": factory["name"]}).fetchone()
            if existing_factory:
                db.execute(text("""
                    UPDATE factories
                    SET location = :location, updated_at = NOW()
                    WHERE name = :name
                """), factory)
            else:
                db.execute(text("""
                    INSERT INTO factories (id, name, location, created_at, updated_at)
                    VALUES (uuid_generate_v4(), :name, :location, NOW(), NOW())
                """), factory)

        db.commit()
        print("✅ Seeded factories")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding factories:", e)
        raise
    finally:
        db.close()


def seed_machines():
    db = SessionLocal()
    try:
        print("Seeding machines...")
        db.execute(text("DELETE FROM machines"))

        factories = db.execute(text("SELECT id, name FROM factories")).fetchall()

        machines_data = []
        for factory_id, factory_name in factories:
            if factory_name == "Genesis Factory 01":
                machines_data.extend([
                    {
                        "factory_id": factory_id, "machine_code": "CNC-001", "machine_type": "CNC", "name": "CNC Machine 1",
                        "manufacturer": "Siemens", "model": "Sinumerik 840D", "year_installed": 2020,
                        "specifications": {"axis": 5, "power_kw": 25}, "position_x": 10.0, "position_y": 5.0, "position_z": 0.0
                    },
                    {
                        "factory_id": factory_id, "machine_code": "ROB-001", "machine_type": "Robot", "name": "Assembly Robot 1",
                        "manufacturer": "ABB", "model": "IRB 6700", "year_installed": 2021,
                        "specifications": {"payload_kg": 150, "reach_m": 3.0}, "position_x": 12.0, "position_y": 8.0, "position_z": 0.0
                    }
                ])
            elif factory_name == "Factory Alpha":
                machines_data.extend([
                    {
                        "factory_id": factory_id, "machine_code": "AGV-001", "machine_type": "AGV", "name": "AGV Unit 1",
                        "manufacturer": "MiR", "model": "MiR250", "year_installed": 2022,
                        "specifications": {"capacity_kg": 250, "speed_mps": 1.5}, "position_x": 1.0, "position_y": 1.0, "position_z": 0.0
                    },
                    {
                        "factory_id": factory_id, "machine_code": "CNC-002", "machine_type": "CNC", "name": "CNC Machine 2",
                        "manufacturer": "DMG Mori", "model": "DMC 650", "year_installed": 2023,
                        "specifications": {"axis": 3, "power_kw": 20}, "position_x": 20.0, "position_y": 10.0, "position_z": 0.0
                    }
                ])
            elif factory_name == "Factory Beta":
                machines_data.extend([
                    {
                        "factory_id": factory_id, "machine_code": "ASM-001", "machine_type": "Assembly", "name": "Assembly Station 1",
                        "manufacturer": "FlexLink", "model": "X70", "year_installed": 2021,
                        "specifications": {"throughput_per_hr": 100, "workers": 2}, "position_x": 5.0, "position_y": 15.0, "position_z": 0.0
                    }
                ])

        for machine in machines_data:
            machine_params = machine.copy()
            machine_params["specifications"] = to_json(machine.get("specifications", {}))
            db.execute(text("""
                INSERT INTO machines (
                    id, factory_id, machine_code, machine_type, name, manufacturer, model,
                    year_installed, specifications, position_x, position_y, position_z,
                    status, created_at, updated_at
                ) VALUES (
                    uuid_generate_v4(), :factory_id, :machine_code, :machine_type, :name, :manufacturer, :model,
                    :year_installed, CAST(:specifications AS jsonb), :position_x, :position_y, :position_z,
                    'idle', NOW(), NOW()
                )
                ON CONFLICT (machine_code) DO UPDATE SET
                    factory_id = EXCLUDED.factory_id,
                    name = EXCLUDED.name,
                    updated_at = NOW()
            """), machine_params)
        db.commit()
        print("✅ Seeded machines")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding machines:", e)
        raise
    finally:
        db.close()


def seed_sensors():
    db = SessionLocal()
    try:
        print("Seeding sensors...")
        db.execute(text("DELETE FROM sensors"))

        machines = db.execute(text("SELECT id, machine_code FROM machines")).fetchall()

        sensors_data = []
        for machine_id, machine_code in machines:
            sensors_data.extend([
                {
                    "machine_id": machine_id, "sensor_code": f"{machine_code}-TEMP-01", "sensor_type": "temperature",
                    "unit": "C", "min_value": 0.0, "max_value": 100.0, "threshold_warning": 80.0, "threshold_critical": 95.0
                },
                {
                    "machine_id": machine_id, "sensor_code": f"{machine_code}-VIB-01", "sensor_type": "vibration",
                    "unit": "mm/s", "min_value": 0.0, "max_value": 20.0, "threshold_warning": 10.0, "threshold_critical": 15.0
                },
                {
                    "machine_id": machine_id, "sensor_code": f"{machine_code}-ENRG-01", "sensor_type": "energy",
                    "unit": "kW", "min_value": 0.0, "max_value": 50.0, "threshold_warning": 30.0, "threshold_critical": 45.0
                }
            ])

        for sensor in sensors_data:
            db.execute(text("""
                INSERT INTO sensors (
                    id, machine_id, sensor_code, sensor_type, unit, min_value, max_value,
                    threshold_warning, threshold_critical, created_at
                ) VALUES (
                    uuid_generate_v4(), :machine_id, :sensor_code, :sensor_type, :unit, :min_value, :max_value,
                    :threshold_warning, :threshold_critical, NOW()
                )
                ON CONFLICT (sensor_code) DO UPDATE SET
                    machine_id = EXCLUDED.machine_id,
                    sensor_type = EXCLUDED.sensor_type
            """), sensor)
        db.commit()
        print("✅ Seeded sensors")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding sensors:", e)
        raise
    finally:
        db.close()


def seed_suppliers():
    db = SessionLocal()
    try:
        print("Seeding suppliers...")

        suppliers_data = [
            {
                "supplier_code": "SUP-001", "name": "Global Components Inc.",
                "contact_info": {"email": "contact@global.com", "phone": "111-222-3333"},
                "rating": 4.5, "performance_score": 0.92
            },
            {
                "supplier_code": "SUP-002", "name": "Local Raw Materials Co.",
                "contact_info": {"email": "info@localrm.com", "phone": "444-555-6666"},
                "rating": 3.8, "performance_score": 0.85
            }
        ]

        for supplier in suppliers_data:
            supplier_params = supplier.copy()
            supplier_params["contact_info"] = to_json(supplier.get("contact_info", {}))
            db.execute(text("""
                INSERT INTO suppliers (
                    id, supplier_code, name, contact_info, rating, performance_score,
                    created_at, updated_at
                ) VALUES (
                    uuid_generate_v4(), :supplier_code, :name, CAST(:contact_info AS jsonb), :rating, :performance_score,
                    NOW(), NOW()
                )
                ON CONFLICT (supplier_code) DO UPDATE SET
                    name = EXCLUDED.name,
                    contact_info = EXCLUDED.contact_info,
                    updated_at = NOW()
            """), supplier_params)
        db.commit()
        print("✅ Seeded suppliers")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding suppliers:", e)
        raise
    finally:
        db.close()


def seed_line_mapping():
    db = SessionLocal()
    try:
        db.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        db.commit()

        db.execute(text("DELETE FROM production_line_mapping"))

        mappings = [
            {
                "product_code_pattern": "PROD-LINE01-%",
                "line_code": "LINE-01",
                "line_name": "Dây chuyền Gia công 01",
                "line_type": "machining",
                "priority_base": 7,
                "is_upstream": True,
                "dependencies": ["LINE-02", "LINE-03"]
            },
            {
                "product_code_pattern": "PROD-LINE02-%",
                "line_code": "LINE-02",
                "line_name": "Dây chuyền Lắp giáp 02",
                "line_type": "assembly",
                "priority_base": 6,
                "is_upstream": False,
                "dependencies": []
            },
            {
                "product_code_pattern": "PROD-LINE03-%",
                "line_code": "LINE-03",
                "line_name": "Dây chuyền Đóng gói 03",
                "line_type": "packaging",
                "priority_base": 5,
                "is_upstream": False,
                "dependencies": []
            }
        ]

        for m in mappings:
            db.execute(text("""
                INSERT INTO production_line_mapping (
                    id, product_code_pattern, line_code, line_name,
                    line_type, priority_base, is_upstream, dependencies,
                    created_at, updated_at
                ) VALUES (
                    uuid_generate_v4(), :pattern, :line_code, :line_name,
                    :line_type, :priority_base, :is_upstream, :dependencies,
                    NOW(), NOW()
                )
            """), {
                "pattern": m["product_code_pattern"],
                "line_code": m["line_code"],
                "line_name": m["line_name"],
                "line_type": m["line_type"],
                "priority_base": m["priority_base"],
                "is_upstream": m["is_upstream"],
                "dependencies": json.dumps(m["dependencies"])
            })
        db.commit()
        print("✅ Seeded production_line_mapping")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding line mapping:", e)
        raise
    finally:
        db.close()


def seed_material_requirements():
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM line_material_requirements"))

        # Ensure materials exist
        materials = [
            {"code": "MAT-001", "name": "Linh kiện A", "supplier_code": "SUP-001"},
            {"code": "MAT-002", "name": "Linh kiện B", "supplier_code": "SUP-001"},
            {"code": "MAT-003", "name": "Linh kiện C", "supplier_code": "SUP-002"},
            {"code": "MAT-004", "name": "Vật liệu đóng gói", "supplier_code": "SUP-002"},
        ]
        for mat in materials:
            supplier_id_res = db.execute(text("SELECT id FROM suppliers WHERE supplier_code = :supplier_code"),
                                         {"supplier_code": mat["supplier_code"]}).fetchone()
            supplier_id = None
            if supplier_id_res:
                supplier_id = supplier_id_res[0]
            else:
                print(f"⚠️ Supplier {mat['supplier_code']} not found for material {mat['code']}. Creating a placeholder supplier.")
                db.execute(text("""
                    INSERT INTO suppliers (id, supplier_code, name, created_at)
                    VALUES (uuid_generate_v4(), :supplier_code, :supplier_name, NOW())
                    ON CONFLICT (supplier_code) DO NOTHING
                """), {"supplier_code": mat["supplier_code"], "supplier_name": f"Placeholder {mat['supplier_code']}"})
                supplier_id = db.execute(text("SELECT id FROM suppliers WHERE supplier_code = :supplier_code"),
                                         {"supplier_code": mat["supplier_code"]}).scalar_one()

            res = db.execute(text("SELECT id FROM materials WHERE material_code = :code"),
                             {"code": mat["code"]}).fetchone()
            if not res:
                db.execute(text("""
                    INSERT INTO materials (id, material_code, name, supplier_id, unit, unit_price, created_at)
                    VALUES (uuid_generate_v4(), :code, :name, :supplier_id, 'pcs', 10.0, NOW())
                """), {"code": mat["code"], "name": mat["name"], "supplier_id": supplier_id})
            else:
                db.execute(text("""
                    UPDATE materials SET supplier_id = :supplier_id, name = :name
                    WHERE material_code = :code
                """), {"supplier_id": supplier_id, "name": mat["name"], "code": mat["code"]})
        db.commit()

        # Insert line material requirements
        requirements = [
            {"line_code": "LINE-01", "material_code": "MAT-001", "required_qty": 2.0, "is_critical": True, "location": "external_staging"},
            {"line_code": "LINE-01", "material_code": "MAT-002", "required_qty": 1.5, "is_critical": True, "location": "external_staging"},
            {"line_code": "LINE-02", "material_code": "MAT-003", "required_qty": 1.0, "is_critical": True, "location": "main_warehouse"},
            {"line_code": "LINE-03", "material_code": "MAT-004", "required_qty": 0.5, "is_critical": False, "location": "main_warehouse"}
        ]

        for r in requirements:
            db.execute(text("""
                INSERT INTO line_material_requirements (
                    id, line_code, material_code, required_quantity_per_unit,
                    is_critical, preferred_location, created_at, updated_at
                ) VALUES (
                    uuid_generate_v4(), :line_code, :material_code, :required_qty,
                    :is_critical, :location, NOW(), NOW()
                )
                ON CONFLICT (line_code, material_code) DO UPDATE SET
                    required_quantity_per_unit = EXCLUDED.required_quantity_per_unit,
                    is_critical = EXCLUDED.is_critical,
                    preferred_location = EXCLUDED.preferred_location,
                    updated_at = NOW()
            """), {
                "line_code": r["line_code"],
                "material_code": r["material_code"],
                "required_qty": r["required_qty"],
                "is_critical": r["is_critical"],
                "location": r["location"]
            })
        db.commit()
        print("✅ Seeded line_material_requirements")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding material requirements:", e)
        raise
    finally:
        db.close()


def seed_system_settings():
    db = SessionLocal()
    try:
        print("Seeding system settings...")
        columns = {
            row[0]
            for row in db.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'system_settings'
            """)).fetchall()
        }
        has_id = "id" in columns
        has_created_at = "created_at" in columns
        has_updated_at = "updated_at" in columns
        has_updated_by = "updated_by" in columns
        admin_user_id = None
        if has_updated_by:
            admin_res = db.execute(text("""
                SELECT id FROM users
                WHERE username = :username OR email = :username
                LIMIT 1
            """), {"username": "admin"}).fetchone()
            if admin_res:
                admin_user_id = admin_res[0]

        settings_data = [
            {
                "key": "dashboard_refresh_interval_sec", "value": {"interval": 10},
                "description": "Interval for dashboard data refresh in seconds."
            },
            {
                "key": "anomaly_detection_threshold", "value": {"threshold": 0.85},
                "description": "Threshold for anomaly detection alerts."
            },
            {
                "key": "maintenance_reminder_days", "value": {"days": 7},
                "description": "Days before scheduled maintenance to trigger reminders."
            }
        ]

        for s in settings_data:
            setting_params = s.copy()
            setting_params["value"] = to_json(s.get("value", {}))
            if has_id and has_created_at:
                db.execute(text("""
                    INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
                    VALUES (uuid_generate_v4(), :key, CAST(:value AS jsonb), :description, NOW(), NOW())
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        description = EXCLUDED.description,
                        updated_at = NOW()
                """), setting_params)
            else:
                columns_clause = ["key", "value", "description"]
                values_clause = [":key", "CAST(:value AS jsonb)", ":description"]
                update_clause = [
                    "value = EXCLUDED.value",
                    "description = EXCLUDED.description"
                ]

                if has_updated_at:
                    columns_clause.append("updated_at")
                    values_clause.append("NOW()")
                    update_clause.append("updated_at = NOW()")

                if has_updated_by:
                    columns_clause.append("updated_by")
                    setting_params["updated_by"] = admin_user_id
                    values_clause.append(":updated_by")
                    update_clause.append("updated_by = EXCLUDED.updated_by")

                insert_sql = f"""
                    INSERT INTO system_settings ({', '.join(columns_clause)})
                    VALUES ({', '.join(values_clause)})
                    ON CONFLICT (key) DO UPDATE SET
                        {', '.join(update_clause)}
                """
                db.execute(text(insert_sql), setting_params)
        db.commit()
        print("✅ Seeded system_settings")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding system settings:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding Genesis Twin data...")

    seed_admin_user()
    seed_factories()
    seed_machines()
    seed_sensors()
    seed_suppliers()
    seed_line_mapping()
    seed_material_requirements()
    seed_system_settings()

    print("✅ All seeding complete!")
