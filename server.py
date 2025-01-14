from flask import Flask, request, jsonify
import subprocess
import random
import os

app = Flask(__name__)

# استخدم الملف لحفظ المعرفات والأسماء المخصصة
ID_FILE = "searched_ids.txt"

def get_motherboard_serial():
    try:
        # استخدام WMIC لاستخراج السيريال الخاص باللوحة الأم
        serial = subprocess.check_output("wmic baseboard get serialnumber", shell=True)
        serial = serial.decode().split("\n")[1].strip()  # إزالة الأحرف الزائدة
        return serial
    except Exception as e:
        print("Error while fetching motherboard serial: ", e)
        return None

def generate_unique_id(serial):
    # إذا كان السيريال يحتوي على أكثر من 12 رقم، نأخذ جزءًا منه
    if len(serial) >= 12:
        return serial[:12]
    
    # إذا كان السيريال أقل من 12 رقمًا، نضيف أرقام عشوائية
    unique_id = serial + ''.join(random.choices('0123456789', k=12-len(serial)))
    return unique_id

@app.route('/generate_id', methods=['GET'])
def generate_id():
    serial = get_motherboard_serial()
    if serial is None:
        return jsonify({"error": "Unable to fetch motherboard serial."}), 500

    user_id = generate_unique_id(serial)
    return jsonify({"user_id": user_id})

@app.route('/search_user', methods=['GET'])
def search_user():
    user_id = request.args.get('user_id', '')
    if user_id:
        # محاكاة الرد من الخادم (يجب أن تحل محل هذا مع قاعدة بيانات أو منطق حقيقي)
        response = {"user_id": user_id, "status": "مستخدم موجود"}
        return jsonify(response)
    else:
        return jsonify({"error": "User ID is required"}), 400

@app.route('/save_searched_id', methods=['POST'])
def save_searched_id():
    data = request.get_json()
    user_id = data.get('user_id', '')
    user_name = data.get('user_name', '')

    if user_id and user_name:
        try:
            # حفظ المعرف مع الاسم في ملف نصي
            with open(ID_FILE, "a") as file:
                file.write(f"{user_id},{user_name}\n")
            return jsonify({"message": "User ID saved successfully!"}), 200
        except Exception as e:
            print(f"Error saving searched ID: {e}")
            return jsonify({"error": "Failed to save ID"}), 500
    else:
        return jsonify({"error": "User ID and User Name are required"}), 400

@app.route('/load_searched_ids', methods=['GET'])
def load_searched_ids():
    try:
        # تحميل المعرفات المخزنة من الملف
        if os.path.exists(ID_FILE):
            with open(ID_FILE, "r") as file:
                ids = file.readlines()
            return jsonify([id.strip().split(",") for id in ids])
        return jsonify([]), 200
    except Exception as e:
        print(f"Error loading searched IDs: {e}")
        return jsonify({"error": "Failed to load IDs"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
