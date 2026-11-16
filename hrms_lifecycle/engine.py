"""Complete ERPNext HRMS Lifecycle Engine (Hire se Retire tak - poora HR ek jagah)."""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class JobApplicantRecord:
    applicant_id: str
    applicant_name: str
    email: str
    phone: str
    job_title: str
    interview_score: float  # Scale 1-100
    status: str = "APPLIED"  # APPLIED, SHORTLISTED, INTERVIEWED, OFFERED, REJECTED


@dataclass
class EmployeeMasterRecord:
    employee_id: str
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str
    date_of_joining: str
    department: str
    designation: str
    status: str = "ACTIVE"  # ACTIVE, ON_LEAVE, SUSPENDED, SEPARATED
    notice_period_days: int = 30


@dataclass
class ShiftSchedule:
    shift_name: str
    start_time: str  # "09:00"
    end_time: str    # "18:00"
    late_entry_grace_minutes: int = 15
    early_exit_grace_minutes: int = 15


@dataclass
class BiometricPunch:
    employee_id: str
    punch_timestamp: str  # "YYYY-MM-DD HH:MM:SS"
    punch_type: str       # IN, OUT
    device_id: str


@dataclass
class AttendanceEvaluation:
    employee_id: str
    attendance_date: str
    shift_name: str
    first_in: Optional[str]
    last_out: Optional[str]
    total_working_hours: float
    is_late_entry: bool
    is_early_exit: bool
    status: str  # PRESENT, HALF_DAY, ABSENT, ON_LEAVE


@dataclass
class LeaveApplication:
    employee_id: str
    leave_type: str  # PRIVILEGE, CASUAL, SICK, COMPENSATORY
    from_date: str
    to_date: str
    total_days: float
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED


@dataclass
class FullAndFinalSettlement:
    employee_id: str
    separation_date: str
    unpaid_salary_days: float
    salary_amount_due: float
    leave_encashment_days: float
    leave_encashment_amount: float
    gratuity_payable: float
    notice_pay_deduction: float
    net_payable_amount: float
    settlement_status: str  # DRAFT, AUDITED, SETTLED


class HRMSFullLifecycleEngine:
    """End-to-End Enterprise HRMS Workflow Engine for Frappe / ERPNext."""

    def process_job_offer(self, applicant: JobApplicantRecord, min_qualifying_score: float = 75.0) -> JobApplicantRecord:
        """Evaluates applicant score and transitions status to OFFERED or REJECTED."""
        if applicant.interview_score >= min_qualifying_score:
            applicant.status = "OFFERED"
        else:
            applicant.status = "REJECTED"
        return applicant

    def evaluate_daily_attendance(
        self,
        employee_id: str,
        attendance_date: str,
        shift: ShiftSchedule,
        punches: List[BiometricPunch]
    ) -> AttendanceEvaluation:
        """Parses raw biometric punches and derives attendance status, hours, and late entry flags."""
        emp_punches = [p for p in punches if p.employee_id == employee_id and p.punch_timestamp.startswith(attendance_date)]
        if not emp_punches:
            return AttendanceEvaluation(
                employee_id=employee_id,
                attendance_date=attendance_date,
                shift_name=shift.shift_name,
                first_in=None,
                last_out=None,
                total_working_hours=0.0,
                is_late_entry=False,
                is_early_exit=False,
                status="ABSENT"
            )

        emp_punches.sort(key=lambda x: x.punch_timestamp)
        first_in = emp_punches[0].punch_timestamp
        last_out = emp_punches[-1].punch_timestamp if len(emp_punches) > 1 else first_in

        t_in = datetime.strptime(first_in, "%Y-%m-%d %H:%M:%S")
        t_out = datetime.strptime(last_out, "%Y-%m-%d %H:%M:%S")

        duration_hours = max(0.0, (t_out - t_in).total_seconds() / 3600.0)

        shift_start_dt = datetime.strptime(f"{attendance_date} {shift.start_time}:00", "%Y-%m-%d %H:%M:%S")
        grace_start_dt = shift_start_dt + timedelta(minutes=shift.late_entry_grace_minutes)
        is_late = t_in > grace_start_dt

        shift_end_dt = datetime.strptime(f"{attendance_date} {shift.end_time}:00", "%Y-%m-%d %H:%M:%S")
        grace_end_dt = shift_end_dt - timedelta(minutes=shift.early_exit_grace_minutes)
        is_early = t_out < grace_end_dt and duration_hours > 0

        status = "PRESENT"
        if duration_hours < 4.0:
            status = "HALF_DAY" if duration_hours >= 2.0 else "ABSENT"
        elif duration_hours >= 8.0:
            status = "PRESENT"
        else:
            status = "HALF_DAY"

        return AttendanceEvaluation(
            employee_id=employee_id,
            attendance_date=attendance_date,
            shift_name=shift.shift_name,
            first_in=first_in,
            last_out=last_out,
            total_working_hours=round(duration_hours, 2),
            is_late_entry=is_late,
            is_early_exit=is_early,
            status=status
        )

    def calculate_full_and_final(
        self,
        emp: EmployeeMasterRecord,
        separation_date: str,
        per_day_basic_pay: float,
        unpaid_days: float,
        accumulated_leave_days: float,
        completed_service_years: int,
        short_notice_days: int = 0
    ) -> FullAndFinalSettlement:
        """Computes Full & Final settlement including salary arrears, leave encashment, and Gratuity."""
        salary_due = unpaid_days * per_day_basic_pay
        leave_encash = accumulated_leave_days * per_day_basic_pay
        
        # Payment of Gratuity Act: 15 * Last Drawn Basic * Years / 26 (if service >= 5 years)
        gratuity = 0.0
        if completed_service_years >= 5:
            gratuity = round((15 * per_day_basic_pay * completed_service_years * 26) / 26.0, 2)

        notice_deduction = short_notice_days * per_day_basic_pay
        net_payable = max(0.0, salary_due + leave_encash + gratuity - notice_deduction)

        return FullAndFinalSettlement(
            employee_id=emp.employee_id,
            separation_date=separation_date,
            unpaid_salary_days=unpaid_days,
            salary_amount_due=round(salary_due, 2),
            leave_encashment_days=accumulated_leave_days,
            leave_encashment_amount=round(leave_encash, 2),
            gratuity_payable=round(gratuity, 2),
            notice_pay_deduction=round(notice_deduction, 2),
            net_payable_amount=round(net_payable, 2),
            settlement_status="AUDITED"
        )
