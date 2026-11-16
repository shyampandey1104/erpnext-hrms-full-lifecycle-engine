# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "hrms_lifecycle"
app_title = "Erpnext Hrms Full Lifecycle Engine"
app_publisher = "Shyamkumar Pandey"
app_description = "Erpnext Hrms Full Lifecycle Engine for Frappe and ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/hrms_lifecycle/css/hrms_lifecycle.bundle.css"
app_include_js = "/assets/hrms_lifecycle/js/hrms_lifecycle.bundle.js"

# Document Events
# ---------------
doc_events = {
    "DocType Event": {
        "on_submit": "hrms_lifecycle.engine.on_document_submit",
        "on_cancel": "hrms_lifecycle.engine.on_document_cancel"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "hrms_lifecycle.engine.daily_scheduled_sync"
    ]
}
