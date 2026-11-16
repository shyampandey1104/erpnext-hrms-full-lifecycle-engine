import unittest
from hrms_lifecycle.engine import (
    HRMSFullLifecycleEngine, JobApplicantRecord, EmployeeMasterRecord,
    ShiftSchedule, BiometricPunch
)

class TestHRMSLifecycle(unittest.TestCase):
    def test_recruitment_offer_workflow(self):
        engine = HRMSFullLifecycleEngine()
        cand1 = JobApplicantRecord("APP-001", "Aarav Sharma", "aarav@test.com", "9876543210", "Software Engineer", 88.0)
        res1 = engine.process_job_offer(cand1)
        self.assertEqual(res1.status, "OFFERED")

        cand2 = JobApplicantRecord("APP-002", "Pooja Patel", "pooja@test.com", "9876543211", "Accountant", 62.0)
        res2 = engine.process_job_offer(cand2)
        self.assertEqual(res2.status, "REJECTED")

    def test_biometric_attendance_evaluation(self):
        engine = HRMSFullLifecycleEngine()
        shift = ShiftSchedule("General Day Shift", "09:00", "18:00", 15, 15)
        punches = [
            BiometricPunch("EMP-01", "2026-04-01 08:55:00", "IN", "BIO-GATE-01"),
            BiometricPunch("EMP-01", "2026-04-01 18:05:00", "OUT", "BIO-GATE-01")
        ]
        res = engine.evaluate_daily_attendance("EMP-01", "2026-04-01", shift, punches)
        self.assertEqual(res.status, "PRESENT")
        self.assertFalse(res.is_late_entry)
        self.assertFalse(res.is_early_exit)
        self.assertGreaterEqual(res.total_working_hours, 9.0)

    def test_full_and_final_settlement(self):
        engine = HRMSFullLifecycleEngine()
        emp = EmployeeMasterRecord("EMP-10", "Rahul", "Verma", "Male", "1990-01-01", "2020-01-01", "Engineering", "Senior Lead")
        fnf = engine.calculate_full_and_final(
            emp=emp,
            separation_date="2026-03-31",
            per_day_basic_pay=2000.0,
            unpaid_days=15.0,
            accumulated_leave_days=10.0,
            completed_service_years=6,
            short_notice_days=0
        )
        self.assertEqual(fnf.salary_amount_due, 30000.0)
        self.assertEqual(fnf.leave_encashment_amount, 20000.0)
        self.assertGreater(fnf.gratuity_payable, 0.0)
        self.assertEqual(fnf.settlement_status, "AUDITED")

if __name__ == "__main__":
    unittest.main()
