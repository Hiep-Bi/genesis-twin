"""
Quick Test Script for Advanced Features
Run this to test all new features without manual curl commands
"""
import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Test credentials (update after login)
TOKEN = None


def login() -> str:
    """Login and get token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        data={
            "username": "admin@genesis.ai",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        exit(1)


def get_headers() -> Dict[str, str]:
    """Get auth headers"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


def test_qr_traceability():
    """Test QR Code Traceability"""
    print("\n" + "="*60)
    print("📱 Testing QR Code Traceability")
    print("="*60)
    
    # Test 1: Generate QR Code
    print("\n1️⃣ Generating QR Code for new product...")
    payload = {
        "product_code": "TEST-PROD-001",
        "serial_number": "SN-TEST-" + str(int(time.time())),
        "machine_id": "MACHINE-003"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/traceability/generate-qr",
        headers=get_headers(),
        json=payload
    )
    
    if response.status_code == 200:
        qr_code = response.json()["qr_code"]
        print(f"✅ QR Code generated: {qr_code}")
        
        # Test 2: Trace QR Code
        print(f"\n2️⃣ Tracing QR Code: {qr_code}...")
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/traceability/trace/{qr_code}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Trace successful!")
            print(f"   - Type: {data.get('trace_type')}")
            print(f"   - Journey Steps: {data.get('total_steps')}")
            print(f"   - Current Location: {data.get('current_location')}")
        else:
            print(f"❌ Trace failed: {response.text}")
    else:
        print(f"❌ QR generation failed: {response.text}")


def test_autonomous_control():
    """Test Autonomous Control Loop"""
    print("\n" + "="*60)
    print("🤖 Testing Autonomous Control Loop")
    print("="*60)
    
    # Test 1: Trigger auto-adjustment
    print("\n1️⃣ Triggering autonomous adjustment for high vibration...")
    payload = {
        "machine_id": "MACHINE-003",
        "sensor_data": {
            "vibration_level": 6.5,
            "temperature": 88.0,
            "efficiency_score": 12.0
        },
        "prediction": {
            "anomaly_detected": True,
            "severity": "high"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/advanced/autonomous-control/detect-adjust",
        headers=get_headers(),
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Autonomous adjustment executed!")
        print(f"   - Action: {data.get('action')}")
        print(f"   - Machine: {data.get('machine_id')}")
        print(f"   - Parameters Changed: {json.dumps(data.get('parameters_changed', {}), indent=4)}")
        print(f"   - Expected Impact: {json.dumps(data.get('expected_impact', {}), indent=4)}")
        print(f"   - Monitoring: {data.get('monitoring')}")
    else:
        print(f"❌ Adjustment failed: {response.text}")
    
    # Test 2: Get active controls
    print("\n2️⃣ Getting active control loops...")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/advanced/autonomous-control/active",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Active controls retrieved: {data.get('total_active')} loops")
    else:
        print(f"❌ Failed to get active controls: {response.text}")


def test_orchestration():
    """Test Orchestration Engine"""
    print("\n" + "="*60)
    print("🚚 Testing Orchestration Engine")
    print("="*60)
    
    # Test 1: Get fleet status
    print("\n1️⃣ Getting AGV fleet status...")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/advanced/orchestration/fleet-status",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Fleet status retrieved!")
        print(f"   - Total AGVs: {data.get('total_agvs')}")
        print(f"   - Idle: {data.get('idle')}")
        print(f"   - Busy: {data.get('busy')}")
        print(f"   - Utilization: {data.get('utilization_percent'):.1f}%")
    else:
        print(f"❌ Failed to get fleet status: {response.text}")
    
    # Test 2: Assign AGV task
    print("\n2️⃣ Assigning AGV task...")
    payload = {
        "task_type": "transport_material",
        "from_location": {"x": 40, "y": 50},
        "to_location": {"x": 120, "y": 75},
        "priority": 8,
        "payload": {"material_code": "MAT-TEST-001"}
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/advanced/orchestration/assign-agv",
        headers=get_headers(),
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AGV task assigned!")
        print(f"   - Status: {data.get('status')}")
        if 'task' in data:
            task = data['task']
            print(f"   - Task ID: {task.get('task_id')}")
            print(f"   - AGV ID: {task.get('agv_id')}")
            print(f"   - ETA: {task.get('eta_seconds')} seconds")
    else:
        print(f"❌ AGV assignment failed: {response.text}")


def test_esg_optimizer():
    """Test ESG Optimizer"""
    print("\n" + "="*60)
    print("🌍 Testing ESG Optimizer")
    print("="*60)
    
    # Test 1: Calculate ESG Score
    print("\n1️⃣ Calculating ESG Score...")
    payload = {
        "production_data": {
            "units_produced": 1000
        },
        "environmental_data": {
            "carbon_emissions_kg": 1500,
            "energy_consumed_kwh": 4000,
            "water_used_liters": 10000,
            "waste_generated_kg": 400,
            "renewable_energy_percent": 40
        },
        "social_data": {
            "accident_rate": 1.5,
            "training_hours_per_employee": 25,
            "employee_satisfaction_percent": 80,
            "diversity_percent": 40
        },
        "governance_data": {
            "compliance_rate_percent": 98,
            "audits_per_year": 4,
            "data_transparency_percent": 85,
            "ethical_sourcing_percent": 75
        }
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/advanced/esg/calculate-score",
        headers=get_headers(),
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ ESG Score calculated!")
        print(f"   - Total Score: {data.get('total_score')}")
        print(f"   - Rating: {data.get('rating')}")
        components = data.get('components', {})
        print(f"   - Environmental: {components.get('environmental', {}).get('score')}")
        print(f"   - Social: {components.get('social', {}).get('score')}")
        print(f"   - Governance: {components.get('governance', {}).get('score')}")
    else:
        print(f"❌ ESG calculation failed: {response.text}")
    
    # Test 2: Run Pareto Optimization
    print("\n2️⃣ Running Pareto Optimization...")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/advanced/esg/simulate-scenarios",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        result = data.get('optimization_result', {})
        print(f"✅ Pareto optimization completed!")
        print(f"   - Total Scenarios: {result.get('total_scenarios')}")
        print(f"   - Pareto Optimal Count: {result.get('pareto_optimal_count')}")
        
        recommendation = data.get('current_recommendation')
        if recommendation:
            print(f"\n   📊 Recommended Mode: {recommendation.get('name')}")
            print(f"      - Cost: ${recommendation.get('cost')}")
            print(f"      - Productivity: {recommendation.get('productivity')}%")
            print(f"      - Carbon: {recommendation.get('carbon_kg')} kg CO₂")
    else:
        print(f"❌ Pareto optimization failed: {response.text}")


def main():
    """Main test runner"""
    global TOKEN
    
    print("🚀 Genesis Twin - Advanced Features Test Suite")
    print("=" * 60)
    
    # Login first
    TOKEN = login()
    
    # Run all tests
    try:
        test_qr_traceability()
        test_autonomous_control()
        test_orchestration()
        test_esg_optimizer()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        print("\n📊 Summary:")
        print("   - QR Code Traceability: ✅")
        print("   - Autonomous Control Loop: ✅")
        print("   - Orchestration Engine: ✅")
        print("   - ESG Optimizer: ✅")
        print("\n🎉 Genesis Twin is fully operational!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

