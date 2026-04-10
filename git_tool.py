import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
except ModuleNotFoundError as e:
    print("Missing Python dependency:", e)
    print("Run this command then retry:")
    print("python -m pip install customtkinter packaging")
    input("Press Enter to exit...")
    sys.exit(1)

# إعداد شكل التطبيق
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.repo_dir = self.detect_repo_dir()

        self.title("مساعد جيت هاب - SEBAQ")
        self.geometry("460x620")

        # العنوان
        self.label = ctk.CTkLabel(self, text="لوحة تحكم Git", font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        # زر تحديث الكل
        self.btn_all = ctk.CTkButton(self, text="تحديث كل الملفات (.)", 
                                     command=self.update_all, 
                                     fg_color="#2ecc71", hover_color="#27ae60",
                                     height=50, font=("Arial", 16))
        self.btn_all.pack(pady=15, padx=20, fill="x")

        # زر اختيار ملف واحد
        self.btn_file = ctk.CTkButton(self, text="اختيار ملف واحد ورفعه", 
                                      command=self.update_file,
                                      height=50, font=("Arial", 16))
        self.btn_file.pack(pady=15, padx=20, fill="x")

        # زر حذف ملف
        self.btn_delete_file = ctk.CTkButton(
            self,
            text="حذف ملف من Git",
            command=self.delete_file,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=50,
            font=("Arial", 16),
        )
        self.btn_delete_file.pack(pady=8, padx=20, fill="x")

        # زر push فقط (بدون commit جديد)
        self.btn_push_only = ctk.CTkButton(
            self,
            text="رفع آخر Commit فقط (Push)",
            command=self.push_only,
            fg_color="#6c5ce7",
            hover_color="#5a4bcf",
            height=46,
            font=("Arial", 15),
        )
        self.btn_push_only.pack(pady=8, padx=20, fill="x")

        # رسالة commit مخصصة
        self.commit_label = ctk.CTkLabel(self, text="رسالة الـ Commit (اختياري):")
        self.commit_label.pack(pady=(12, 4))
        self.commit_entry = ctk.CTkEntry(self, placeholder_text="مثال: تحديث أسئلة جديدة")
        self.commit_entry.pack(padx=20, fill="x")

        self.log_label = ctk.CTkLabel(self, text="سجل العمليات:")
        self.log_label.pack(pady=(14, 4))
        self.log_box = ctk.CTkTextbox(self, height=180)
        self.log_box.pack(padx=20, pady=(0, 12), fill="both", expand=True)
        self.log_box.insert("1.0", "جاهز.\n")
        self.log_box.configure(state="disabled")

        # حالة الرفع
        self.status = ctk.CTkLabel(self, text="الحالة: جاهز", text_color="gray")
        self.status.pack(side="bottom", pady=10)

    def detect_repo_dir(self):
        script_dir = Path(__file__).resolve().parent
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=script_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                repo_root = result.stdout.strip()
                if repo_root:
                    return str(Path(repo_root).resolve())
        except Exception:
            pass
        return str(script_dir)

    def detect_branch_name(self):
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
            )
            branch = result.stdout.strip()
            return branch or "main"
        except Exception:
            return "main"

    def run_git(self, args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )

    def build_error(self, step_name, result):
        details = (result.stderr or result.stdout or "").strip()
        if not details:
            details = "Unknown git error"
        return f"{step_name} failed:\n{details}"

    def append_log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message.strip() + "\n\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def get_commit_message(self, default_message):
        user_message = self.commit_entry.get().strip()
        msg = user_message if user_message else default_message
        return msg.replace('"', "'")

    def get_relative_repo_path(self, file_path):
        repo_path = Path(self.repo_dir).resolve()
        selected_path = Path(file_path).resolve()

        try:
            return str(selected_path.relative_to(repo_path)).replace("\\", "/")
        except ValueError:
            return None

    def run_git_flow(self, add_args, default_commit_message):
        try:
            branch_name = self.detect_branch_name()
            self.append_log(f"بدء العملية على الفرع: {branch_name}")

            add_result = self.run_git(add_args)
            if add_result.returncode != 0:
                raise RuntimeError(self.build_error("git add/rm", add_result))
            self.append_log("تم تنفيذ add/rm بنجاح.")

            has_staged = self.run_git(["diff", "--cached", "--quiet"])
            if has_staged.returncode == 0:
                messagebox.showinfo("معلومة", "لا توجد تغييرات جديدة للرفع.")
                self.status.configure(text="الحالة: لا توجد تغييرات", text_color="gray")
                self.append_log("لا توجد تغييرات جديدة بعد add/rm.")
                return

            commit_message = self.get_commit_message(default_commit_message)
            commit_result = self.run_git(["commit", "-m", commit_message])
            if commit_result.returncode != 0:
                raise RuntimeError(self.build_error("git commit", commit_result))
            self.append_log(f"تم إنشاء commit: {commit_message}")

            push_result = self.run_git(["push", "origin", branch_name])
            if push_result.returncode != 0:
                raise RuntimeError(self.build_error("git push", push_result))
            self.append_log(f"تم push بنجاح إلى origin/{branch_name}")

            messagebox.showinfo("نجاح", "تم الرفع بنجاح إلى GitHub!")
            self.status.configure(text="الحالة: تم الرفع بنجاح", text_color="green")
        except Exception as e:
            self.append_log(f"فشل العملية:\n{e}")
            messagebox.showerror("خطأ", f"فشل الرفع:\n{e}")
            self.status.configure(text="الحالة: فشل الرفع", text_color="red")

    def update_all(self):
        self.status.configure(text="جاري الرفع...", text_color="orange")
        self.append_log("طلب: تحديث كل الملفات.")
        self.run_git_flow(["add", "-A"], "تحديث تلقائي شامل")

    def update_file(self):
        file_path = filedialog.askopenfilename(initialdir=self.repo_dir)
        if file_path:
            relative_file = self.get_relative_repo_path(file_path)
            if not relative_file:
                messagebox.showerror("خطأ", "اختر ملفًا من داخل فولدر المشروع فقط.")
                return

            self.status.configure(text=f"جاري رفع {relative_file}...", text_color="orange")
            self.append_log(f"طلب: رفع ملف واحد: {relative_file}")
            self.run_git_flow(
                ["add", "--", relative_file],
                f"تحديث ملف: {relative_file}"
            )

    def delete_file(self):
        file_path = filedialog.askopenfilename(initialdir=self.repo_dir)
        if not file_path:
            return

        relative_file = self.get_relative_repo_path(file_path)
        if not relative_file:
            messagebox.showerror("خطأ", "اختر ملفًا من داخل فولدر المشروع فقط.")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("خطأ", "الملف غير موجود.")
            return

        ok = messagebox.askyesno(
            "تأكيد الحذف",
            f"هل تريد حذف الملف من GitHub والمشروع؟\n\n{relative_file}"
        )
        if not ok:
            return

        self.status.configure(text=f"جاري حذف {relative_file}...", text_color="orange")
        self.append_log(f"طلب: حذف ملف: {relative_file}")
        self.run_git_flow(
            ["rm", "--", relative_file],
            f"حذف ملف: {relative_file}"
        )

    def push_only(self):
        self.status.configure(text="جاري push فقط...", text_color="orange")
        try:
            branch_name = self.detect_branch_name()
            self.append_log(f"طلب: push فقط إلى origin/{branch_name}")
            result = self.run_git(["push", "origin", branch_name])
            if result.returncode != 0:
                raise RuntimeError(self.build_error("git push", result))
            self.append_log(f"تم push فقط بنجاح إلى origin/{branch_name}")
            messagebox.showinfo("نجاح", "تم تنفيذ push بنجاح.")
            self.status.configure(text="الحالة: تم push بنجاح", text_color="green")
        except Exception as e:
            self.append_log(f"فشل push:\n{e}")
            messagebox.showerror("خطأ", f"فشل push:\n{e}")
            self.status.configure(text="الحالة: فشل push", text_color="red")

if __name__ == "__main__":
    app = GitApp()
    app.mainloop()