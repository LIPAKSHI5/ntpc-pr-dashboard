from flask import Flask, render_template, request, redirect, jsonify, send_file
import sqlite3
import pandas as pd
from ai_ml_analysis import perform_analysis

app = Flask(__name__)
DATABASE = 'pr_database.db'


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pr_entries (
                pr_no TEXT,
                material_code TEXT,
                material_name TEXT,
                material_budget TEXT,
                item_text TEXT,
                updated_on_date TEXT,
                quantity TEXT,
                status TEXT,
                name TEXT,
                employee_id TEXT,
                location TEXT,
                bid_no TEXT,
                bod TEXT,
                remark_if_closed TEXT,
                result TEXT,
                po_number TEXT,
                vendor_code TEXT,
                vendor_name TEXT,
                vendor_mail_id TEXT,
                vendor_contact_no TEXT,
                delivery_completed_by_vendor TEXT,
                vendor_amount TEXT,
                vendor_payment_status TEXT,
                initiator TEXT,
                visible_to_user INTEGER DEFAULT 1
            )
        ''')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/user')
    return render_template('login.html')


@app.route('/user')
def user_dashboard():
    return render_template('index.html')


@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')


@app.route('/live_analysis')
def live_analysis_page():
    return render_template('live_analysis.html')


@app.route('/api/add', methods=['POST'])
def add_entry():
    data = request.json
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM pr_entries 
            WHERE pr_no = ? AND material_code = ? AND visible_to_user = 0
        ''', (data['pr_no'], data['material_code']))
        existing = cur.fetchone()
        if existing:
            conn.execute('''
                UPDATE pr_entries SET visible_to_user = 1,
                    material_name = ?, material_budget = ?, item_text = ?, updated_on_date = ?,
                    quantity = ?, status = ?, name = ?, employee_id = ?, location = ?, bid_no = ?, bod = ?,
                    remark_if_closed = ?, result = ?, po_number = ?, vendor_code = ?, vendor_name = ?,
                    vendor_mail_id = ?, vendor_contact_no = ?, delivery_completed_by_vendor = ?, vendor_amount = ?,
                    vendor_payment_status = ?, initiator = ?
                WHERE pr_no = ? AND material_code = ?
            ''', (data['material_name'], data['material_budget'], data['item_text'], data['updated_on_date'],
                  data['quantity'], data['status'], data['name'], data['employee_id'], data['location'],
                  data['bid_no'], data['bod'], data['remark_if_closed'], data['result'], data['po_number'],
                  data['vendor_code'], data['vendor_name'], data['vendor_mail_id'], data['vendor_contact_no'],
                  data['delivery_completed_by_vendor'], data['vendor_amount'], data['vendor_payment_status'],
                  data['initiator'], data['pr_no'], data['material_code']))
        else:
            conn.execute('''
                INSERT INTO pr_entries 
                (pr_no, material_code, material_name, material_budget, item_text, updated_on_date,
                 quantity, status, name, employee_id, location, bid_no, bod, remark_if_closed, result,
                 po_number, vendor_code, vendor_name, vendor_mail_id, vendor_contact_no, delivery_completed_by_vendor,
                 vendor_amount, vendor_payment_status, initiator, visible_to_user)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (data['pr_no'], data['material_code'], data['material_name'], data['material_budget'],
                  data['item_text'], data['updated_on_date'], data['quantity'], data['status'], data['name'],
                  data['employee_id'], data['location'], data['bid_no'], data['bod'], data['remark_if_closed'],
                  data['result'], data['po_number'], data['vendor_code'], data['vendor_name'], data['vendor_mail_id'],
                  data['vendor_contact_no'], data['delivery_completed_by_vendor'], data['vendor_amount'],
                  data['vendor_payment_status'], data['initiator']))
    return jsonify({"message": "Data added or updated successfully"})


@app.route('/api/list')
def list_user_data():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM pr_entries WHERE visible_to_user = 1')
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data = [dict(zip(columns, row)) for row in rows]
    return jsonify(data)


@app.route('/api/list_admin')
def list_admin_data():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM pr_entries')
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data = [dict(zip(columns, row)) for row in rows]
    return jsonify(data)


@app.route('/api/delete', methods=['POST'])
def delete_entry():
    data = request.json
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            UPDATE pr_entries SET visible_to_user = 0
            WHERE pr_no = ? AND material_code = ?
        ''', (data['pr_no'], data['material_code']))
    return jsonify({"message": "Entry hidden from user successfully"})


@app.route('/export_excel')
def export_excel():
    with sqlite3.connect(DATABASE) as conn:
        df = pd.read_sql_query('SELECT * FROM pr_entries', conn)
    df.to_excel('NTPC_PR_DATA.xlsx', index=False)
    return send_file('NTPC_PR_DATA.xlsx', as_attachment=True)


@app.route('/api/aiml_analysis')
def aiml_analysis():
    result = perform_analysis(DATABASE)
    return jsonify(result)


@app.route('/api/kpi_summary')
def kpi_summary():
    with sqlite3.connect(DATABASE) as conn:
        df = pd.read_sql_query('SELECT * FROM pr_entries WHERE visible_to_user = 1', conn)

    total_prs = len(df)
    open_prs = len(df[df['status'].str.lower() == 'open'])
    closed_prs = len(df[df['status'].str.lower() == 'closed'])
    total_vendors = df['vendor_name'].nunique()

    df['vendor_amount'] = pd.to_numeric(df['vendor_amount'], errors='coerce')
    total_amount = df['vendor_amount'].sum()

    return jsonify({
        'total_prs': total_prs,
        'open_prs': open_prs,
        'closed_prs': closed_prs,
        'total_vendors': total_vendors,
        'total_amount': f"₹{total_amount:,.2f}"
    })


import os

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

