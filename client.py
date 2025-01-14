import socket
import tkinter as tk
import threading
import subprocess
import random
import os

HOST = '127.0.0.1'  # عنوان الخادم المحلي
PORT = 12345
ID_FILE = "searched_ids.txt"  # ملف لحفظ المعرفات والأسماء المخصصة

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

def receive_messages(sock, text_widget):
    try:
        while True:
            message = sock.recv(1024).decode('utf-8')
            if message:
                text_widget.insert(tk.END, f"{message}\n")
                text_widget.yview(tk.END)  # للتمرير التلقائي لأسفل عند تلقي رسالة جديدة
    except Exception as e:
        print(f"Error receiving message: {e}")
        text_widget.insert(tk.END, "Error receiving message.\n")

def send_message(sock, entry):
    message = entry.get()
    if message:
        try:
            sock.send(message.encode('utf-8'))
            entry.delete(0, tk.END)
        except Exception as e:
            print(f"Error sending message: {e}")

def search_user_by_id(sock, search_entry, result_frame):
    search_query = f"بحث:{search_entry.get()}"
    try:
        sock.send(search_query.encode('utf-8'))

        # مسح أي نتائج قديمة
        for widget in result_frame.winfo_children():
            widget.pack_forget()  # أو grid_forget إذا كنت تستخدم grid

        # محاكاة الرد من الخادم (يفترض أنه وجد المستخدم)
        response = "المستخدم موجود"  # هنا سيعود الخادم برد حقيقي

        if response == "المستخدم موجود":
            user_id = search_entry.get()
            user_name = load_user_name(user_id)  # جلب الاسم المخزن لهذا المعرف
            user_button = tk.Button(result_frame, text=user_name, bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised", command=lambda: open_chat_window(user_id))
            user_button.pack(pady=5)

            # حفظ المعرف في الملف
            save_searched_id(user_id, user_name)
    except Exception as e:
        print(f"Error in searching user: {e}")

def open_chat_window(user_id):
    try:
        # إنشاء نافذة شات جديدة مع المستخدم
        chat_window = tk.Toplevel()
        chat_window.title(f"Chat with {user_id}")
        chat_window.geometry("500x500")  # حجم نافذة الشات

        # تصميم النصوص
        text_area = tk.Text(chat_window, height=20, width=50, font=("Arial", 12), wrap=tk.WORD, bg="#f4f4f4", fg="black", bd=2, relief="solid")
        text_area.pack(pady=10, padx=10)

        # تحميل الرسائل السابقة من الملف
        load_chat_messages(user_id, text_area)

        entry = tk.Entry(chat_window, width=50, font=("Arial", 12))
        entry.pack(pady=5)

        send_button = tk.Button(chat_window, text="Send", bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised", command=lambda: send_message_to_chat(text_area, entry, user_id))
        send_button.pack(pady=5)

        # إضافة خاصية تعديل الاسم
        name_change_button = tk.Button(chat_window, text="Change Name", bg="#FFC107", fg="black", font=("Arial", 12), relief="raised", command=lambda: change_user_name(user_id))
        name_change_button.pack(pady=5)
    except Exception as e:
        print(f"Error opening chat window: {e}")

def send_message_to_chat(text_area, entry, user_id):
    message = entry.get()
    if message:
        text_area.insert(tk.END, f"You: {message}\n")
        save_chat_messages(user_id, f"You: {message}")  # حفظ الرسالة
        entry.delete(0, tk.END)

def save_chat_messages(user_id, message):
    try:
        # حفظ الرسائل في ملف خاص بكل محادثة
        chat_file = f"chat_{user_id}.txt"
        with open(chat_file, "a") as file:
            file.write(f"{message}\n")
    except Exception as e:
        print(f"Error saving chat message: {e}")

def load_chat_messages(user_id, text_area):
    try:
        # تحميل الرسائل من الملف الخاص بكل محادثة
        chat_file = f"chat_{user_id}.txt"
        if os.path.exists(chat_file):
            with open(chat_file, "r") as file:
                messages = file.readlines()
            for message in messages:
                text_area.insert(tk.END, f"{message}")
            text_area.yview(tk.END)  # التمرير التلقائي لأسفل
    except Exception as e:
        print(f"Error loading chat messages: {e}")

def save_searched_id(user_id, user_name):
    try:
        # حفظ المعرف مع الاسم في ملف نصي
        with open(ID_FILE, "a") as file:
            file.write(f"{user_id},{user_name}\n")
    except Exception as e:
        print(f"Error saving searched ID: {e}")

def load_searched_ids():
    try:
        # تحميل المعرفات المخزنة من الملف
        if os.path.exists(ID_FILE):
            with open(ID_FILE, "r") as file:
                ids = file.readlines()
            return [id.strip().split(",") for id in ids]
        return []
    except Exception as e:
        print(f"Error loading searched IDs: {e}")
        return []

def load_user_name(user_id):
    try:
        # تحميل الاسم المرتبط بالمعرف من الملف
        searched_ids = load_searched_ids()
        for id, name in searched_ids:
            if id == user_id:
                return name
        return user_id  # إذا لم يتم العثور على الاسم، نعرض المعرف كاسم
    except Exception as e:
        print(f"Error loading user name: {e}")
        return user_id

def change_user_name(user_id):
    try:
        # نافذة لتغيير الاسم
        change_name_window = tk.Toplevel()
        change_name_window.title(f"Change Name for {user_id}")
        change_name_window.geometry("300x150")

        label = tk.Label(change_name_window, text="Enter new name:", font=("Arial", 12))
        label.pack(pady=10)

        name_entry = tk.Entry(change_name_window, font=("Arial", 12))
        name_entry.pack(pady=5)

        def save_new_name():
            new_name = name_entry.get()
            if new_name:
                # تحديث الاسم في الملف
                update_user_name(user_id, new_name)
                change_name_window.destroy()

        save_button = tk.Button(change_name_window, text="Save", bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised", command=save_new_name)
        save_button.pack(pady=10)
    except Exception as e:
        print(f"Error changing user name: {e}")

def update_user_name(user_id, new_name):
    try:
        # تحديث الاسم في الملف
        searched_ids = load_searched_ids()
        with open(ID_FILE, "w") as file:
            for id, name in searched_ids:
                if id == user_id:
                    file.write(f"{user_id},{new_name}\n")  # تحديث الاسم
                else:
                    file.write(f"{id},{name}\n")
    except Exception as e:
        print(f"Error updating user name: {e}")

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return

    # استخراج السيريال الخاص باللوحة الأم وإنشاء المعرف الفريد
    serial = get_motherboard_serial()
    if serial is None:
        print("Error fetching motherboard serial.")
        return

    user_id = generate_unique_id(serial)
    print(f"YOUR ID IS: {user_id}")
    
    client.send(user_id.encode('utf-8'))

    root = tk.Tk()
    root.title("Chat Application")
    root.geometry("600x400")  # حجم النافذة
    root.config(bg="#f1f1f1")

    # عرض المعرف في أعلى واجهة العميل
    user_id_label = tk.Label(root, text=f"YOUR ID: {user_id}", font=("Arial", 14), bg="#f1f1f1")
    user_id_label.pack(pady=10)

    search_label = tk.Label(root, text="Search User by ID:", font=("Arial", 12), bg="#f1f1f1")
    search_label.pack(pady=5)

    search_entry = tk.Entry(root, font=("Arial", 12))
    search_entry.pack(pady=5)

    result_frame = tk.Frame(root, bg="#f1f1f1")
    result_frame.pack(pady=10)

    search_button = tk.Button(root, text="Search", bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised", command=lambda: search_user_by_id(client, search_entry, result_frame))
    search_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    start_client()
