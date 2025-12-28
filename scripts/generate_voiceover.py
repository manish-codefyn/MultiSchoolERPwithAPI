from gtts import gTTS
import os

# Script Segments from demo_video_script.md
script_segments = {
    "01_intro": "Running a school is complex. Managing multiple schools is a challenge. Meet EduERP: The ultimate multi-tenant platform designed to streamline education management from a single, powerful hub.",
    "02_saas_experience": "Built for the SaaS era.  EduERP offers a seamless onboarding experience. With our public-facing portal, prospective schools can explore plans, sign up, and deploy their own dedicated ERP instance in seconds—not days.",
    "03_dashboard": "Welcome to your command center. The Master Dashboard gives administrators a real-time pulse on their institution. Attendance trends, fee collections, and staff activity—everything you need, right at a glance.",
    "04_student_lifecycle": "From the first day of admission to graduation. Manage the entire student lifecycle with intuitive onboarding forms, digital profiles, and comprehensive academic tracking including automated timetables and exam management.",
    "05_operations": "Operations made effortless. Handle complex payrolls, track organizational assets, and configure flexible fee structures. EduERP brings your Finance and HR departments onto the same page.",
    "06_modules": "Transportation, Hostels, Library, and Inventory. No module is left behind. We provide specialized tools for every operational wing of your campus.",
    "07_security": "Security is standard. With role-based access control, encrypted data, and isolated tenant Schemas, your data remains yours. And as you grow? EduERP grows with you. Add new branches instantly.",
    "08_outro": "EduERP by Codefyn. Smart. Scalable. Secure. Transform your institution today."
}

output_dir = "voiceovers"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Generating voiceovers...")

for filename, text in script_segments.items():
    print(f"Generating {filename}...")
    try:
        tts = gTTS(text=text, lang='en', tld='com')
        # specific tld 'com' (US) or 'co.uk' (British) - script asked for neutral. 'com' is fine.
        save_path = os.path.join(output_dir, f"{filename}.mp3")
        tts.save(save_path)
        print(f"Saved: {save_path}")
    except Exception as e:
        print(f"Error generating {filename}: {e}")

print("Done.")
