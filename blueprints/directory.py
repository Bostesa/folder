# directory.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
import mysql.connector
from utils import get_db_connection, login_required, role_required, fetch_all, fetch_one

# Define the blueprint
directory_bp = Blueprint('directory', __name__)

@directory_bp.route('/directory')
@login_required
def directory():
    return redirect(url_for('dashboard.dashboard'))

def role_name(role_id):
    row = fetch_one("SELECT role_name FROM Role WHERE role_id = %s", (role_id,))
    return row['role_name'] if row else ''

def accounting_department_id(default_id=6):
    row = fetch_one("SELECT department_id FROM Department WHERE name = 'Accounting' LIMIT 1")
    return row['department_id'] if row else default_id

def finance_department_id(default_id=5):
    row = fetch_one("SELECT department_id FROM Department WHERE name = 'Financial Services and Loans' LIMIT 1")
    return row['department_id'] if row else default_id

PAYMENT_METHODS = ('Cash', 'Credit Card', 'Check', 'Bank Transfer', 'Financing')
LOAN_PAYMENT_METHODS = ('Cash', 'Credit Card', 'Check', 'Bank Transfer')
ACCOUNTING_TYPES = ('Expense', 'Other')
VEHICLE_CONDITIONS = ('New', 'Used')
VEHICLE_STATUSES = ('Available', 'Sold', 'Removed')
LOAN_STATUSES = ('Pending', 'Approved', 'Rejected')

def require_choice(value, allowed, label):
    if value not in allowed:
        raise ValueError(f"{label} must be one of: {', '.join(allowed)}.")
    return value

def require_positive_decimal(value, label, allow_zero=False):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a number.")
    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError(f"{label} must be greater than zero.")
    return value

def require_positive_int(value, label, min_value=None, max_value=None, allow_zero=False):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a whole number.")
    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError(f"{label} must be greater than zero.")
    if min_value is not None and number < min_value:
        raise ValueError(f"{label} must be at least {min_value}.")
    if max_value is not None and number > max_value:
        raise ValueError(f"{label} must be at most {max_value}.")
    return value

def normalize_phone(phone):
    digits = ''.join(ch for ch in (phone or '') if ch.isdigit())
    if len(digits) != 10:
        raise ValueError("Phone numbers must be 10 digits, for example 5551234567.")
    return digits

def phone_values(value):
    return [normalize_phone(phone) for phone in split_csv(value)]

def normalize_vehicle_vin(value):
    raw = (value or '').strip().upper().replace(' ', '')
    if raw.startswith('VIN'):
        raw = raw[3:]
    if len(raw) != 14 or not raw.isdigit():
        raise ValueError("VIN must be exactly 14 digits. The app adds the VIN prefix automatically.")
    return f"VIN{raw}"

@directory_bp.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action in ('create', 'update') and session.get('role_name') == 'Accountant':
                flash("Accountants can view customers but cannot change customer records.", "error")
            elif action in ('create', 'update'):
                if action == 'create':
                    phones = phone_values(request.form.get('phones'))
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO Customer (name, address, email) VALUES (%s, %s, %s)",
                        (request.form['name'], request.form.get('address'), request.form.get('email'))
                    )
                    customer_id = cursor.lastrowid
                    for phone in phones:
                        cursor.execute(
                            "INSERT INTO CustomerPhone (customer_id, phone) VALUES (%s, %s)",
                            (customer_id, phone)
                        )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    flash("Customer added.", "success")
                else:
                    phones = phone_values(request.form.get('phones'))
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE Customer SET name=%s, address=%s, email=%s WHERE customer_id=%s",
                        (
                            request.form['name'],
                            request.form.get('address'),
                            request.form.get('email'),
                            request.form['customer_id']
                        )
                    )
                    cursor.execute("DELETE FROM CustomerPhone WHERE customer_id=%s", (request.form['customer_id'],))
                    for phone in phones:
                        cursor.execute(
                            "INSERT INTO CustomerPhone (customer_id, phone) VALUES (%s, %s)",
                            (request.form['customer_id'], phone)
                        )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    flash("Customer updated.", "success")

        q = request.values.get('q', '')
        params = ()
        where = ""
        if q:
            q_digits = ''.join(ch for ch in q if ch.isdigit())
            like = f"%{q}%"
            if q_digits:
                where = """WHERE c.customer_id IN (
                    SELECT DISTINCT c2.customer_id FROM Customer c2
                    LEFT JOIN CustomerPhone cp2 ON c2.customer_id = cp2.customer_id
                    WHERE c2.name LIKE %s OR c2.email LIKE %s OR cp2.phone LIKE %s OR cp2.phone LIKE %s
                )"""
                params = (like, like, like, f"%{q_digits}%")
            else:
                where = """WHERE c.customer_id IN (
                    SELECT DISTINCT c2.customer_id FROM Customer c2
                    LEFT JOIN CustomerPhone cp2 ON c2.customer_id = cp2.customer_id
                    WHERE c2.name LIKE %s OR c2.email LIKE %s OR cp2.phone LIKE %s
                )"""
                params = (like, like, like)

        customers_data = fetch_all(
            f"""
            SELECT c.customer_id, c.name, c.address, c.email,
                   GROUP_CONCAT(cp.phone SEPARATOR ', ') AS phones
            FROM Customer c
            LEFT JOIN CustomerPhone cp ON c.customer_id = cp.customer_id
            {where}
            GROUP BY c.customer_id, c.name, c.address, c.email
            ORDER BY c.name
            """,
            params
        )
        histories = fetch_all(
            """
            SELECT c.name AS customer_name, 'Sale' AS record_type, v.vin, s.sale_date AS record_date, s.sale_price AS amount
            FROM Sales s
            JOIN Customer c ON s.customer_id = c.customer_id
            JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
            UNION ALL
            SELECT c.name, 'Service', v.vin, sv.service_date, sv.cost
            FROM Service sv
            JOIN Customer c ON sv.customer_id = c.customer_id
            JOIN Vehicle v ON sv.vehicle_id = v.vehicle_id
            UNION ALL
            SELECT c.name, 'Loan', v.vin, NULL, l.amount
            FROM Loan l
            JOIN Customer c ON l.customer_id = c.customer_id
            JOIN Vehicle v ON l.vehicle_id = v.vehicle_id
            ORDER BY customer_name, record_type
            """
        )
        return render_template('customers.html', customers=customers_data, histories=histories, q=q)
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('customers.html', customers=[], histories=[], q='')
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for('directory.customers'))

@directory_bp.route('/vehicles', methods=['GET', 'POST'])
@login_required
def vehicles():
    try:
        if request.method == 'POST':
            if not sales_or_admin():
                flash("Only sales staff or administrators can change inventory.", "error")
                return redirect(url_for('directory.vehicles'))
            action = request.form.get('action')
            if action == 'create':
                execute_simple(
                    """
                    INSERT INTO Vehicle (make, model, year, vin, price, mileage, condition_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    vehicle_form_values()
                )
                flash("Vehicle added.", "success")
            elif action == 'update':
                execute_simple(
                    """
                    UPDATE Vehicle
                    SET make=%s, model=%s, year=%s, vin=%s, price=%s, mileage=%s, condition_type=%s, status=%s
                    WHERE vehicle_id=%s
                    """,
                    vehicle_form_values() + (request.form['vehicle_id'],)
                )
                flash("Vehicle updated.", "success")
            elif action == 'remove':
                execute_simple("UPDATE Vehicle SET status='Removed' WHERE vehicle_id=%s", (request.form['vehicle_id'],))
                flash("Vehicle removed from inventory.", "success")

        q = request.values.get('q', '')
        params = ()
        where = ""
        if q:
            where = "WHERE make LIKE %s OR model LIKE %s OR vin LIKE %s OR year = %s"
            like = f"%{q}%"
            params = (like, like, like, q if q.isdigit() else 0)
        vehicles_data = fetch_all(f"SELECT * FROM Vehicle {where} ORDER BY vehicle_id", params)
        return render_template('vehicles.html', vehicles=vehicles_data, q=q)
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('vehicles.html', vehicles=[], q='')
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for('directory.vehicles'))

@directory_bp.route('/sales', methods=['GET', 'POST'])
@role_required('Sales Staff')
def sales():
    try:
        if request.method == 'POST':
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            vehicle_id = request.form['vehicle_id']
            require_positive_decimal(request.form.get('sale_price'), "Sale price")
            payment_method = require_choice(request.form.get('payment_method'), PAYMENT_METHODS, "Payment method")
            cursor.execute("SELECT status FROM Vehicle WHERE vehicle_id=%s", (vehicle_id,))
            vehicle = cursor.fetchone()
            if not vehicle or vehicle['status'] != 'Available':
                flash("Selected vehicle is not available.", "error")
            else:
                cursor.execute(
                    """
                    INSERT INTO Sales (customer_id, vehicle_id, user_id, department_id, sale_price, sale_date, payment_method, financing_option)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        request.form['customer_id'],
                        vehicle_id,
                        request.form['user_id'],
                        request.form['department_id'],
                        request.form['sale_price'],
                        request.form['sale_date'],
                        payment_method,
                        1 if request.form.get('financing_option') else 0
                    )
                )
                cursor.execute("UPDATE Vehicle SET status='Sold' WHERE vehicle_id=%s", (vehicle_id,))
                cursor.execute(
                    "INSERT INTO Accounting (type, amount, transaction_date, department_id) VALUES ('Sales', %s, %s, %s)",
                    (request.form['sale_price'], request.form['sale_date'], request.form['department_id'])
                )
                conn.commit()
                flash("Sale recorded and vehicle marked sold.", "success")
            cursor.close()
            conn.close()

        q = request.values.get('q', '')
        start_date = request.values.get('start_date', '')
        end_date = request.values.get('end_date', '')
        where_parts = []
        params = []
        if q:
            where_parts.append("(c.name LIKE %s OR v.model LIKE %s OR v.vin LIKE %s OR d.name LIKE %s)")
            like = f"%{q}%"
            params.extend([like, like, like, like])
        if start_date:
            where_parts.append("s.sale_date >= %s")
            params.append(start_date)
        if end_date:
            where_parts.append("s.sale_date <= %s")
            params.append(end_date)
        where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""

        sales_data = fetch_all(
            f"""
            SELECT s.sale_id, c.name AS customer, CONCAT(v.year, ' ', v.make, ' ', v.model) AS vehicle,
                   v.vin, e.name AS employee, d.name AS department, s.sale_price, s.sale_date,
                   s.payment_method, s.financing_option
            FROM Sales s
            JOIN Customer c ON s.customer_id = c.customer_id
            JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
            JOIN `User` e ON s.user_id = e.user_id
            JOIN Department d ON s.department_id = d.department_id
            {where_sql}
            ORDER BY s.sale_date DESC
            """,
            tuple(params)
        )
        return render_template('sales.html', sales=sales_data, q=q, start_date=start_date, end_date=end_date, **lookup_data())
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('sales.html', sales=[], q='', start_date='', end_date='', **lookup_data())
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for('directory.sales'))

@directory_bp.route('/services', methods=['GET', 'POST'])
@role_required('Service Staff')
def services():
    try:
        if request.method == 'POST':
            conn = get_db_connection()
            cursor = conn.cursor()
            action = request.form.get('action')
            if action == 'create':
                require_positive_decimal(request.form.get('cost'), "Total service cost")
                parts = split_csv(request.form.get('parts'))
                part_total_cost = 0
                if request.form.get('part_total_cost'):
                    require_positive_decimal(request.form.get('part_total_cost'), "Total parts cost", allow_zero=True)
                    part_total_cost = float(request.form.get('part_total_cost') or 0)
                if part_total_cost and not parts:
                    raise ValueError("Enter parts used if you enter a total parts cost.")
                part_cost = round(part_total_cost / len(parts), 2) if parts else 0
                cursor.execute(
                    """
                    INSERT INTO Service (customer_id, vehicle_id, user_id, service_type, service_date, cost)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        request.form['customer_id'],
                        request.form['vehicle_id'],
                        request.form['user_id'],
                        request.form['service_type'],
                        request.form['service_date'],
                        request.form['cost']
                    )
                )
                service_id = cursor.lastrowid
                for part_name in parts:
                    cursor.execute(
                        "INSERT INTO ServiceParts (service_id, part_name, part_cost) VALUES (%s, %s, %s)",
                        (service_id, part_name, part_cost)
                    )
                cursor.execute(
                    "INSERT INTO Accounting (type, amount, transaction_date, department_id) VALUES ('Service', %s, %s, 4)",
                    (request.form['cost'], request.form['service_date'])
                )
                conn.commit()
                flash("Service recorded.", "success")
            elif action == 'update':
                require_positive_decimal(request.form.get('cost'), "Service cost")
                cursor.execute(
                    """
                    UPDATE Service
                    SET service_type=%s, service_date=%s, cost=%s
                    WHERE service_id=%s
                    """,
                    (
                        request.form['service_type'],
                        request.form['service_date'],
                        request.form['cost'],
                        request.form['service_id']
                    )
                )
                conn.commit()
                flash("Service updated.", "success")
            cursor.close()
            conn.close()

        vin = request.values.get('vin', '')
        params = ()
        where = ""
        if vin:
            where = "WHERE v.vin LIKE %s OR v.vehicle_id = %s"
            params = (f"%{vin}%", vin if vin.isdigit() else 0)
        services_data = fetch_all(
            f"""
            SELECT sv.service_id, c.name AS customer, v.vin, CONCAT(v.year, ' ', v.make, ' ', v.model) AS vehicle,
                   e.name AS technician, sv.service_type, sv.service_date, sv.cost,
                   GROUP_CONCAT(sp.part_name SEPARATOR ', ') AS parts
            FROM Service sv
            JOIN Customer c ON sv.customer_id = c.customer_id
            JOIN Vehicle v ON sv.vehicle_id = v.vehicle_id
            JOIN `User` e ON sv.user_id = e.user_id
            LEFT JOIN ServiceParts sp ON sv.service_id = sp.service_id
            {where}
            GROUP BY sv.service_id, c.name, v.vin, vehicle, e.name, sv.service_type, sv.service_date, sv.cost
            ORDER BY sv.service_date DESC
            """,
            params
        )
        return render_template('services.html', services=services_data, vin=vin, **lookup_data())
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('services.html', services=[], vin='', **lookup_data())
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for('directory.services'))

@directory_bp.route('/loans', methods=['GET', 'POST'])
@role_required('Finance Staff')
def loans():
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'create':
                require_positive_decimal(request.form.get('amount'), "Loan amount")
                require_positive_decimal(request.form.get('interest_rate'), "Interest rate", allow_zero=True)
                require_positive_int(request.form.get('term'), "Loan term")
                require_positive_decimal(request.form.get('monthly_payment'), "Monthly payment")
                approval_status = require_choice(request.form.get('approval_status'), LOAN_STATUSES, "Approval status")
                execute_simple(
                    """
                    INSERT INTO Loan (customer_id, vehicle_id, amount, interest_rate, term, monthly_payment, approval_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        request.form['customer_id'],
                        request.form['vehicle_id'],
                        request.form['amount'],
                        request.form['interest_rate'],
                        request.form['term'],
                        request.form['monthly_payment'],
                        approval_status
                    )
                )
                flash("Loan created.", "success")
            elif action == 'payment':
                add_loan_payment()
                flash("Loan payment recorded.", "success")
            elif action == 'update_loan':
                require_positive_decimal(request.form.get('amount'), "Loan amount")
                require_positive_decimal(request.form.get('interest_rate'), "Interest rate", allow_zero=True)
                require_positive_int(request.form.get('term'), "Loan term")
                require_positive_decimal(request.form.get('monthly_payment'), "Monthly payment")
                approval_status = require_choice(request.form.get('approval_status'), LOAN_STATUSES, "Approval status")
                execute_simple(
                    """UPDATE Loan SET approval_status=%s, amount=%s, interest_rate=%s, term=%s, monthly_payment=%s
                       WHERE loan_id=%s""",
                    (
                        approval_status,
                        request.form['amount'],
                        request.form['interest_rate'],
                        request.form['term'],
                        request.form['monthly_payment'],
                        request.form['loan_id']
                    )
                )
                flash("Loan updated.", "success")
            elif action == 'delete_loan':
                execute_simple("DELETE FROM LoanPayment WHERE loan_id=%s", (request.form['loan_id'],))
                execute_simple("DELETE FROM Loan WHERE loan_id=%s", (request.form['loan_id'],))
                flash("Loan deleted.", "success")

        q = request.values.get('q', '')
        params = ()
        where = ""
        if q:
            where = "WHERE c.name LIKE %s OR v.vin LIKE %s OR l.approval_status LIKE %s"
            like = f"%{q}%"
            params = (like, like, like)
        loans_data = fetch_all(
            f"""
            SELECT l.loan_id, c.name AS customer, v.vin, CONCAT(v.year, ' ', v.make, ' ', v.model) AS vehicle,
                   l.amount, l.interest_rate, l.term, l.monthly_payment, l.approval_status,
                   l.amount - COALESCE(SUM(lp.amount), 0) AS outstanding_balance
            FROM Loan l
            JOIN Customer c ON l.customer_id = c.customer_id
            JOIN Vehicle v ON l.vehicle_id = v.vehicle_id
            LEFT JOIN LoanPayment lp ON l.loan_id = lp.loan_id
            {where}
            GROUP BY l.loan_id, c.name, v.vin, vehicle, l.amount, l.interest_rate, l.term, l.monthly_payment, l.approval_status
            ORDER BY l.loan_id
            """,
            params
        )
        payments = fetch_all("SELECT * FROM LoanPayment ORDER BY payment_date DESC")
        return render_template('loans.html', loans=loans_data, payments=payments, q=q, **lookup_data())
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('loans.html', loans=[], payments=[], q='', **lookup_data())
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for('directory.loans'))

@directory_bp.route('/accounting', methods=['GET', 'POST'])
@role_required('Accountant')
def accounting():
    try:
        if request.method == 'POST':
            transaction_type = require_choice(request.form.get('type'), ACCOUNTING_TYPES, "Transaction type")
            require_positive_decimal(request.form.get('amount'), "Amount")
            execute_simple(
                "INSERT INTO Accounting (type, amount, transaction_date, department_id) VALUES (%s, %s, %s, %s)",
                (
                    transaction_type,
                    request.form['amount'],
                    request.form['transaction_date'],
                    request.form['department_id']
                )
            )
            flash("Accounting entry recorded.", "success")
        q = request.values.get('q', '')
        params = ()
        where = ""
        if q:
            where = "WHERE a.type LIKE %s OR d.name LIKE %s"
            like = f"%{q}%"
            params = (like, like)
        rows = fetch_all(
            f"""
            SELECT a.transaction_id, a.type, a.amount, a.transaction_date, d.name AS department
            FROM Accounting a
            LEFT JOIN Department d ON a.department_id = d.department_id
            {where}
            ORDER BY a.transaction_date DESC, a.transaction_id DESC
            """,
            params
        )
        return render_template('accounting.html', rows=rows, q=q, departments=fetch_all("SELECT * FROM Department ORDER BY name"))
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('accounting.html', rows=[], q='', departments=[])
    except ValueError as err:
        flash(str(err), "error")
        return redirect(url_for('directory.accounting'))

@directory_bp.route('/admin/users', methods=['GET', 'POST'])
@role_required('Administrator')
def admin_users():
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'create':
                execute_simple(
                    """
                    INSERT INTO `User` (username, password, name, address, email, department_id, role_id, active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                    """,
                    (
                        request.form['username'],
                        generate_password_hash(request.form['password'], method='pbkdf2:sha256'),
                        request.form.get('name'),
                        request.form.get('address'),
                        request.form.get('email'),
                        request.form.get('department_id') or None,
                        request.form['role_id']
                    )
                )
                flash("User created.", "success")
            elif action == 'update':
                execute_simple(
                    """
                    UPDATE `User`
                    SET name=%s, address=%s, email=%s, department_id=%s, role_id=%s, active=%s
                    WHERE user_id=%s
                    """,
                    (
                        request.form.get('name'),
                        request.form.get('address'),
                        request.form.get('email'),
                        request.form.get('department_id') or None,
                        request.form['role_id'],
                        1 if request.form.get('active') else 0,
                        request.form['user_id']
                    )
                )
                flash("User updated.", "success")
        users = fetch_all(
            """
            SELECT u.user_id, u.username, u.name, u.address, u.email, u.department_id, d.name AS department,
                   r.role_name, u.active
            FROM `User` u
            JOIN Role r ON u.role_id = r.role_id
            LEFT JOIN Department d ON u.department_id = d.department_id
            ORDER BY u.user_id
            """
        )
        return render_template(
            'admin_users.html',
            users=users,
            roles=fetch_all("SELECT * FROM Role ORDER BY role_name"),
            departments=fetch_all("SELECT * FROM Department WHERE active=TRUE ORDER BY name")
        )
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('admin_users.html', users=[], roles=[], departments=[])

@directory_bp.route('/admin/divisions', methods=['GET', 'POST'])
@role_required('Administrator')
def admin_divisions():
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'create':
                execute_simple("INSERT INTO Division (name) VALUES (%s)", (request.form['name'],))
                flash("Division added.", "success")
            elif action == 'update':
                execute_simple("UPDATE Division SET name=%s WHERE division_id=%s", (request.form['name'], request.form['division_id']))
                flash("Division updated.", "success")
        return render_template('admin_divisions.html', divisions=fetch_all("SELECT * FROM Division ORDER BY name"))
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('admin_divisions.html', divisions=[])

@directory_bp.route('/admin/departments', methods=['GET', 'POST'])
@role_required('Administrator')
def admin_departments():
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'create':
                execute_simple(
                    "INSERT INTO Department (name, division_id, active) VALUES (%s, %s, TRUE)",
                    (request.form['name'], request.form['division_id'])
                )
                flash("Department added.", "success")
            elif action == 'update':
                execute_simple(
                    "UPDATE Department SET name=%s, division_id=%s, active=%s WHERE department_id=%s",
                    (
                        request.form['name'],
                        request.form['division_id'],
                        1 if request.form.get('active') else 0,
                        request.form['department_id']
                    )
                )
                flash("Department updated.", "success")
        departments = fetch_all(
            """
            SELECT d.department_id, d.name, d.active, d.division_id, v.name AS division
            FROM Department d
            JOIN Division v ON d.division_id = v.division_id
            ORDER BY d.name
            """
        )
        return render_template('admin_departments.html', departments=departments, divisions=fetch_all("SELECT * FROM Division ORDER BY name"))
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return render_template('admin_departments.html', departments=[], divisions=[])

@directory_bp.route('/reports')
@login_required
def reports():
    data = {}
    current_role = request.args.get('role', '')
    try:
        data['sales_totals'] = fetch_all("SELECT COUNT(*) AS vehicles_sold, COALESCE(SUM(sale_price), 0) AS revenue FROM Sales")
        data['sales_by_department'] = fetch_all(
            """
            SELECT d.name AS department, COUNT(*) AS vehicles_sold, SUM(s.sale_price) AS revenue
            FROM Sales s
            JOIN Department d ON s.department_id = d.department_id
            GROUP BY d.name
            """
        )
        data['sales_by_month'] = fetch_all(
            """
            SELECT DATE_FORMAT(sale_date, '%Y-%m') AS sale_month, COUNT(*) AS vehicles_sold, SUM(sale_price) AS revenue
            FROM Sales
            GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
            ORDER BY sale_month
            """
        )
        data['service_totals'] = fetch_all("SELECT COUNT(*) AS service_count, COALESCE(SUM(cost), 0) AS service_revenue FROM Service")
        data['service_types'] = fetch_all("SELECT service_type, COUNT(*) AS count FROM Service GROUP BY service_type ORDER BY count DESC")
        data['loan_statuses'] = fetch_all("SELECT approval_status, COUNT(*) AS count FROM Loan GROUP BY approval_status")
        data['loan_balances'] = fetch_all(
            """
            SELECT l.loan_id, c.name AS customer, l.amount - COALESCE(SUM(lp.amount), 0) AS outstanding_balance
            FROM Loan l
            JOIN Customer c ON l.customer_id = c.customer_id
            LEFT JOIN LoanPayment lp ON l.loan_id = lp.loan_id
            GROUP BY l.loan_id, c.name, l.amount
            """
        )
        data['accounting_by_type'] = fetch_all("SELECT type, SUM(amount) AS total FROM Accounting GROUP BY type")
        data['accounting_by_department'] = fetch_all(
            """
            SELECT d.name AS department, SUM(a.amount) AS total
            FROM Accounting a
            LEFT JOIN Department d ON a.department_id = d.department_id
            GROUP BY d.name
            """
        )
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    return render_template('reports.html', data=data, current_role=current_role)

def split_csv(value):
    return [item.strip() for item in (value or '').split(',') if item.strip()]

def sales_or_admin():
    return session.get('role_name') in ('Sales Staff', 'Administrator')

def vehicle_form_values():
    vin = normalize_vehicle_vin(request.form.get('vin'))
    require_positive_int(request.form.get('year'), "Year", min_value=1900, max_value=2030)
    if request.form.get('price'):
        require_positive_decimal(request.form.get('price'), "Price")
    if request.form.get('mileage'):
        require_positive_int(request.form.get('mileage'), "Mileage", allow_zero=True)
    return (
        request.form.get('make'),
        request.form.get('model'),
        request.form.get('year'),
        vin,
        request.form.get('price'),
        request.form.get('mileage'),
        require_choice(request.form.get('condition_type'), VEHICLE_CONDITIONS, "Vehicle condition"),
        require_choice(request.form.get('status'), VEHICLE_STATUSES, "Vehicle status")
    )

def execute_simple(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def lookup_data():
    return {
        'customers': fetch_all("SELECT customer_id, name FROM Customer ORDER BY name"),
        'vehicles': fetch_all("SELECT vehicle_id, vin, make, model, year, status FROM Vehicle ORDER BY vehicle_id"),
        'available_vehicles': fetch_all("SELECT vehicle_id, vin, make, model, year FROM Vehicle WHERE status='Available' ORDER BY vehicle_id"),
        'employees': fetch_all("SELECT user_id, name FROM `User` WHERE active=TRUE ORDER BY name"),
        'sales_employees': fetch_all("SELECT u.user_id, u.name FROM `User` u JOIN Role r ON u.role_id = r.role_id WHERE r.role_name='Sales Staff' AND u.active=TRUE ORDER BY u.name"),
        'service_employees': fetch_all("SELECT u.user_id, u.name FROM `User` u JOIN Role r ON u.role_id = r.role_id WHERE r.role_name='Service Staff' AND u.active=TRUE ORDER BY u.name"),
        'sales_departments': fetch_all("""SELECT d.department_id, d.name FROM Department d
            JOIN Division dv ON d.division_id = dv.division_id
            WHERE dv.name = 'Sales' AND d.active = TRUE ORDER BY d.name"""),
        'departments': fetch_all("SELECT department_id, name FROM Department WHERE active=TRUE ORDER BY name")
    }

def add_loan_payment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        loan_id = request.form['loan_id']
        payment_amount = float(request.form['payment_amount'])
        if payment_amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        payment_method = require_choice(request.form.get('payment_method'), LOAN_PAYMENT_METHODS, "Loan payment method")
        cursor.execute(
            """
            SELECT l.amount - COALESCE(SUM(lp.amount), 0) AS balance
            FROM Loan l
            LEFT JOIN LoanPayment lp ON l.loan_id = lp.loan_id
            WHERE l.loan_id = %s
            GROUP BY l.loan_id, l.amount
            """,
            (loan_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError("Select a valid loan before recording a payment.")
        remaining_balance = max(float(row['balance']) - payment_amount, 0) if row else 0
        cursor.execute(
            "INSERT INTO LoanPayment (loan_id, payment_date, amount, payment_method, remaining_balance) VALUES (%s, %s, %s, %s, %s)",
            (loan_id, request.form['payment_date'], payment_amount, payment_method, remaining_balance)
        )
        cursor.execute(
            "INSERT INTO Accounting (type, amount, transaction_date, department_id) VALUES ('Loan', %s, %s, %s)",
            (payment_amount, request.form['payment_date'], finance_department_id())
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()