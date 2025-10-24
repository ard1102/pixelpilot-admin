import sqlite3
import os
from datetime import datetime
from urllib.parse import quote_plus
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    make_response,
    send_from_directory,
)

app = Flask(__name__)


@app.route('/hello')
def hello():
    return 'Hello from Flask'


@app.route('/')
def index():
    # Query approved images newest first
    approved_rows = query_db(
        "SELECT id, filename, price, date_uploaded FROM images WHERE status = 'approved' ORDER BY date_uploaded DESC"
    )

    # Prepare data for template: format date, build WhatsApp link
    images = []
    for row in approved_rows:
        dv = row['date_uploaded']
        date_str = (
            dv.strftime('%B %d, %Y') if hasattr(dv, 'strftime') else (dv if dv else '')
        )
        images.append(
            {
                'id': row['id'],
                'filename': row['filename'],
                'price': row['price'],
                'date_str': date_str,
                'wa_link': generate_wa_link(row['filename']),
            }
        )

    return render_template('home.html', images=images)


# ---- DB Helpers ----
def get_db():
    conn = sqlite3.connect('site.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    db.close()
    return (rv[0] if rv else None) if one else rv


# ---- Minimal Security ----
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')


def is_admin_request(req: request) -> bool:
    # Check token via query param, header, or cookie
    token = (
        req.args.get('token')
        or req.headers.get('X-Admin-Token')
        or req.cookies.get('admin_token')
    )
    return token == ADMIN_TOKEN


# ---- Public Image Serving ----
@app.route('/images/<path:filename>')
def serve_image(filename: str):
    return send_from_directory('images', filename)


# ---- WhatsApp Helper ----
WA_PHONE = os.environ.get('WA_PHONE', '')  # Set to your number, no '+' or spaces


def generate_wa_link(filename: str) -> str:
    base_text = 'Hello! I am interested in the image: '
    inquiry_text = f"{base_text}{filename}"
    encoded = quote_plus(inquiry_text)
    return f"https://wa.me/{WA_PHONE}?text={encoded}"


# ---- Admin Dashboard ----
@app.route('/admin')
def admin_dashboard():
    # Security check
    if not is_admin_request(request):
        return (
            'Unauthorized. Set ADMIN_TOKEN env var and append ?token=<your token> or send X-Admin-Token header.',
            401,
        )

    # Persist token in cookie if provided via query
    resp = None
    if request.args.get('token') == ADMIN_TOKEN:
        resp = make_response()
        resp.set_cookie('admin_token', ADMIN_TOKEN, httponly=True)

    # Filter status (default pending)
    filter_status = request.args.get('status', 'pending')

    query = 'SELECT * FROM images'
    args = []
    if filter_status in ['pending', 'approved', 'trash']:
        query += ' WHERE status = ?'
        args.append(filter_status)
    query += ' ORDER BY date_uploaded DESC'

    images = query_db(query, args)

    if resp is None:
        return render_template('admin.html', images=images, current_filter=filter_status)
    else:
        # Attach rendered template to response so cookie is set
        resp.response = [
            render_template('admin.html', images=images, current_filter=filter_status)
        ]
        resp.mimetype = 'text/html'
        return resp


# ---- Admin APIs ----
@app.route('/api/set_status', methods=['POST'])
def set_image_status():
    if not is_admin_request(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    image_id = data.get('id')
    new_status = data.get('status')

    if image_id is None or new_status not in ['pending', 'approved', 'trash']:
        return jsonify({'success': False, 'error': 'Invalid payload'}), 400

    trash_date = None
    if new_status == 'trash':
        trash_date = datetime.now()

    db = get_db()
    db.execute(
        '''
        UPDATE images
        SET status = ?, trash_date = ?
        WHERE id = ?
        ''',
        (new_status, trash_date, image_id),
    )
    db.commit()
    db.close()

    return jsonify({'success': True, 'message': f'Image {image_id} status set to {new_status}'}), 200


@app.route('/api/edit_price', methods=['POST'])
def edit_image_price():
    if not is_admin_request(request):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    image_id = data.get('id')
    price = data.get('price')

    try:
        price_val = float(price) if price is not None else None
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Invalid price'}), 400

    if image_id is None:
        return jsonify({'success': False, 'error': 'Invalid payload'}), 400

    db = get_db()
    db.execute(
        'UPDATE images SET price = ? WHERE id = ?',
        (price_val, image_id),
    )
    db.commit()
    db.close()

    return jsonify({'success': True, 'message': f'Image {image_id} price updated', 'price': price_val}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)