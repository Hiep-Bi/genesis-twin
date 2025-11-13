"""QR Scanner and AGV/Robot simulator"""
import random
import string
from typing import Dict, Any
from datetime import datetime
from faker import Faker

fake = Faker()


class QRScannerSimulator:
    """Simulate QR code scanning by AGVs and robots"""
    
    SCAN_LOCATIONS = [
        "Receiving Bay",
        "Storage Area A",
        "Storage Area B",
        "Production Line 1",
        "Production Line 2",
        "Quality Control",
        "Packaging",
        "Shipping Bay"
    ]
    
    SCAN_TYPES = [
        "material_received",
        "material_consumed",
        "product_manufactured",
        "quality_inspected",
        "product_shipped"
    ]
    
    def __init__(self, num_robots: int = 10):
        self.num_robots = num_robots
        self.robots = [f"ROBOT-{i:02d}" for i in range(num_robots)]
        self.scan_counter = 0
    
    def _generate_qr_code(self) -> str:
        """Generate a realistic QR code"""
        # Format: PREFIX-YYYYMMDD-RANDOM6
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        prefix = random.choice(["MAT", "PRD", "PKG", "SHP"])
        
        return f"{prefix}-{date_part}-{random_part}"
    
    def generate_scan(self) -> Dict[str, Any]:
        """Generate a QR scan event"""
        self.scan_counter += 1
        
        robot_id = random.choice(self.robots)
        location = random.choice(self.SCAN_LOCATIONS)
        scan_type = random.choice(self.SCAN_TYPES)
        qr_code = self._generate_qr_code()
        
        # Generate additional metadata based on scan type
        metadata = {}
        
        if scan_type == "material_received":
            metadata = {
                "supplier_id": f"SUP-{random.randint(1, 20):03d}",
                "material_type": random.choice(["raw_material", "component", "packaging"]),
                "quantity": random.randint(10, 1000),
                "batch_number": fake.bothify(text='BATCH-####??')
            }
        
        elif scan_type == "material_consumed":
            metadata = {
                "production_order": f"PO-{random.randint(1000, 9999)}",
                "machine_id": f"MACHINE-{random.randint(0, 49):03d}",
                "quantity_used": random.randint(1, 100)
            }
        
        elif scan_type == "product_manufactured":
            metadata = {
                "product_code": f"PROD-{random.randint(100, 999)}",
                "serial_number": fake.bothify(text='SN-########'),
                "machine_id": f"MACHINE-{random.randint(0, 49):03d}",
                "quality_status": random.choice(["pass", "pass", "pass", "fail"])  # 75% pass rate
            }
        
        elif scan_type == "quality_inspected":
            metadata = {
                "inspector_id": f"INS-{random.randint(1, 10):02d}",
                "inspection_result": random.choice(["pass", "pass", "pass", "fail"]),
                "defects_found": random.choice([[], [], [], ["scratch", "dent"]])
            }
        
        elif scan_type == "product_shipped":
            metadata = {
                "shipment_id": f"SHIP-{random.randint(1000, 9999)}",
                "destination": fake.city(),
                "carrier": random.choice(["FedEx", "UPS", "DHL", "USPS"]),
                "tracking_number": fake.bothify(text='TRK-##########')
            }
        
        # Create scan event
        scan_event = {
            "scan_id": f"SCAN-{self.scan_counter:08d}",
            "robot_id": robot_id,
            "qr_code": qr_code,
            "scan_type": scan_type,
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "position": {
                "x": random.uniform(-100, 100),
                "y": random.uniform(-100, 100),
                "z": random.uniform(0, 10)
            }
        }
        
        return scan_event
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about QR scanning"""
        return {
            "num_robots": self.num_robots,
            "total_scans": self.scan_counter,
            "scan_locations": len(self.SCAN_LOCATIONS),
            "scan_types": len(self.SCAN_TYPES)
        }

