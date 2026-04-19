import pandas as pd


def _normalize(val) -> str:
    return str(val).strip().lower()


def run_reconciliation(hr_df: pd.DataFrame, payroll_df: pd.DataFrame) -> dict:
    hr_df = hr_df.set_index("Employee_ID")
    payroll_df = payroll_df.set_index("Employee_ID")

    hr_ids = set(hr_df.index)
    payroll_ids = set(payroll_df.index)
    hr_only_ids = sorted(hr_ids - payroll_ids)
    payroll_only_ids = sorted(payroll_ids - hr_ids)
    common_ids = sorted(hr_ids & payroll_ids)

    # Type A: in HR but not in Payroll
    if hr_only_ids:
        hr_only = hr_df.loc[hr_only_ids].reset_index()
        hr_only["Discrepancy_Type"] = "Missing in Payroll"
        hr_only["Description"] = hr_only["Employee_ID"].apply(
            lambda eid: f"Employee {eid} exists in HR but has no matching record in Payroll."
        )
    else:
        hr_only = pd.DataFrame(columns=list(hr_df.columns) + ["Employee_ID", "Discrepancy_Type", "Description"])

    # Type B: in Payroll but not in HR
    if payroll_only_ids:
        payroll_only = payroll_df.loc[payroll_only_ids].reset_index()
        payroll_only["Discrepancy_Type"] = "Missing in HR"
        payroll_only["Description"] = payroll_only["Employee_ID"].apply(
            lambda eid: f"Employee {eid} exists in Payroll but has no matching record in HR."
        )
    else:
        payroll_only = pd.DataFrame(columns=list(payroll_df.columns) + ["Employee_ID", "Discrepancy_Type", "Description"])

    # Type C: field-level mismatches on common employees
    common_columns = [col for col in hr_df.columns if col in payroll_df.columns]
    mismatch_rows = []

    for emp_id in common_ids:
        for col in common_columns:
            hr_val = hr_df.loc[emp_id, col]
            pay_val = payroll_df.loc[emp_id, col]
            if _normalize(hr_val) != _normalize(pay_val):
                mismatch_rows.append({
                    "Employee_ID": emp_id,
                    "Column_Name": col,
                    "HR_Value": hr_val,
                    "Payroll_Value": pay_val,
                    "Discrepancy_Type": "Field Mismatch",
                    "Description": (
                        f"Employee {emp_id}: '{col}' differs — "
                        f"HR has '{hr_val}', Payroll has '{pay_val}'."
                    ),
                })

    mismatches = pd.DataFrame(mismatch_rows) if mismatch_rows else pd.DataFrame(
        columns=["Employee_ID", "Column_Name", "HR_Value", "Payroll_Value", "Discrepancy_Type", "Description"]
    )

    summary = {
        "Total HR Records": len(hr_df),
        "Total Payroll Records": len(payroll_df),
        "Matched (Common) Records": len(common_ids),
        "Missing in Payroll (HR only)": len(hr_only_ids),
        "Missing in HR (Payroll only)": len(payroll_only_ids),
        "Field-Level Mismatches": len(mismatch_rows),
        "Total Discrepancies": len(hr_only_ids) + len(payroll_only_ids) + len(mismatch_rows),
    }

    return {
        "summary": summary,
        "hr_only": hr_only,
        "payroll_only": payroll_only,
        "mismatches": mismatches,
    }
