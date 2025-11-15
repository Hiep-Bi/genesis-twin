"""Seed Config Data - Production Line Mapping and Material Requirements"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/genesis_twin")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed_line_mapping():
    """Seed production line mapping data"""
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.execute(text("DELETE FROM production_line_mapping"))
        
        # Insert line mappings
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
            },
            {
                "product_code_pattern": "LINE01-%",
                "line_code": "LINE-01",
                "line_name": "Dây chuyền Gia công 01",
                "line_type": "machining",
                "priority_base": 7,
                "is_upstream": True,
                "dependencies": ["LINE-02", "LINE-03"]
            },
            {
                "product_code_pattern": "LINE02-%",
                "line_code": "LINE-02",
                "line_name": "Dây chuyền Lắp giáp 02",
                "line_type": "assembly",
                "priority_base": 6,
                "is_upstream": False,
                "dependencies": []
            },
            {
                "product_code_pattern": "LINE03-%",
                "line_code": "LINE-03",
                "line_name": "Dây chuyền Đóng gói 03",
                "line_type": "packaging",
                "priority_base": 5,
                "is_upstream": False,
                "dependencies": []
            }
        ]
        
        for mapping in mappings:
            db.execute(text("""
                INSERT INTO production_line_mapping (
                    product_code_pattern,
                    line_code,
                    line_name,
                    line_type,
                    priority_base,
                    is_upstream,
                    dependencies
                ) VALUES (
                    :pattern,
                    :line_code,
                    :line_name,
                    :line_type,
                    :priority_base,
                    :is_upstream,
                    :dependencies::jsonb
                )
            """), {
                "pattern": mapping["product_code_pattern"],
                "line_code": mapping["line_code"],
                "line_name": mapping["line_name"],
                "line_type": mapping["line_type"],
                "priority_base": mapping["priority_base"],
                "is_upstream": mapping["is_upstream"],
                "dependencies": str(mapping["dependencies"])
            })
        
        db.commit()
        print("✅ Seeded production_line_mapping data")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding line mapping: {e}")
        raise
    finally:
        db.close()


def seed_material_requirements():
    """Seed line material requirements"""
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.execute(text("DELETE FROM line_material_requirements"))
        
        # First, ensure materials exist
        materials = [
            {"code": "MAT-001", "name": "Linh kiện A"},
            {"code": "MAT-002", "name": "Linh kiện B"},
            {"code": "MAT-003", "name": "Linh kiện C"},
            {"code": "MAT-004", "name": "Vật liệu đóng gói"},
        ]
        
        for mat in materials:
            # Check if exists
            result = db.execute(
                text("SELECT id FROM materials WHERE material_code = :code"),
                {"code": mat["code"]}
            ).fetchone()
            
            if not result:
                # Create material
                db.execute(text("""
                    INSERT INTO materials (material_code, name, unit, unit_price)
                    VALUES (:code, :name, 'pcs', 10.0)
                """), {"code": mat["code"], "name": mat["name"]})
        
        db.commit()
        
        # Insert material requirements
        requirements = [
            # LINE-01 requirements
            {
                "line_code": "LINE-01",
                "material_code": "MAT-001",
                "required_quantity_per_unit": 2.0,
                "is_critical": True,
                "preferred_location": "external_staging"
            },
            {
                "line_code": "LINE-01",
                "material_code": "MAT-002",
                "required_quantity_per_unit": 1.5,
                "is_critical": True,
                "preferred_location": "external_staging"
            },
            # LINE-02 requirements
            {
                "line_code": "LINE-02",
                "material_code": "MAT-003",
                "required_quantity_per_unit": 1.0,
                "is_critical": True,
                "preferred_location": "main_warehouse"
            },
            # LINE-03 requirements
            {
                "line_code": "LINE-03",
                "material_code": "MAT-004",
                "required_quantity_per_unit": 0.5,
                "is_critical": False,
                "preferred_location": "main_warehouse"
            }
        ]
        
        for req in requirements:
            db.execute(text("""
                INSERT INTO line_material_requirements (
                    line_code,
                    material_code,
                    required_quantity_per_unit,
                    is_critical,
                    preferred_location
                ) VALUES (
                    :line_code,
                    :material_code,
                    :required_qty,
                    :is_critical,
                    :preferred_location
                )
                ON CONFLICT (line_code, material_code) DO NOTHING
            """), {
                "line_code": req["line_code"],
                "material_code": req["material_code"],
                "required_qty": req["required_quantity_per_unit"],
                "is_critical": req["is_critical"],
                "preferred_location": req["preferred_location"]
            })
        
        db.commit()
        print("✅ Seeded line_material_requirements data")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding material requirements: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding config data...")
    seed_line_mapping()
    seed_material_requirements()
    print("✅ Config data seeding complete!")

