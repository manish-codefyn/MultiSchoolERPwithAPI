from gtts import gTTS
import os

# English Text
script_en = {
    "01_intro": "Running a school is complex. Managing multiple schools is a challenge. Meet EduERP: The ultimate multi-tenant platform designed to streamline education management from a single, powerful hub.",
    "02_saas_experience": "Built for the SaaS era. EduERP offers a seamless onboarding experience. With our public-facing portal, prospective schools can explore plans, sign up, and deploy their own dedicated ERP instance in seconds—not days.",
    "03_dashboard": "Welcome to your command center. The Master Dashboard gives administrators a real-time pulse on their institution. Attendance trends, fee collections, and staff activity—everything you need, right at a glance.",
    "04_student_lifecycle": "From the first day of admission to graduation. Manage the entire student lifecycle with intuitive onboarding forms, digital profiles, and comprehensive academic tracking including automated timetables and exam management.",
    "05_operations": "Operations made effortless. Handle complex payrolls, track organizational assets, and configure flexible fee structures. EduERP brings your Finance and HR departments onto the same page.",
    "06_modules": "Transportation, Hostels, Library, and Inventory. No module is left behind. We provide specialized tools for every operational wing of your campus.",
    "07_security": "Security is standard. With role-based access control, encrypted data, and isolated tenant Schemas, your data remains yours. And as you grow? EduERP grows with you. Add new branches instantly.",
    "08_outro": "EduERP by Codefyn. Smart. Scalable. Secure. Transform your institution today."
}

# Hindi Text (Translated)
script_hi = {
    "01_intro": "School chalana mushkil hai. Kai schools ko manage karna ek chunauti hai. Miliye EduERP se. Yeh ek multi-tenant platform hai jo education management ko aasaan banata hai.",
    "02_saas_experience": "SaaS era ke liye banaaya gaya. EduERP onboarding ko aasaan banata hai. Hamare public portal se, naye schools plans dekh sakte hain, sign up kar sakte hain, aur seconds mein apna ERP shuru kar sakte hain.",
    "03_dashboard": "Aapke command center mein swagat hai. Master Dashboard administrators ko institution ki poori jaankaari deta hai. Attendance, fees, aur staff activity—sab kuch ek hi jagah par.",
    "04_student_lifecycle": "Admission ke pehle din se graduation tak. Poore student lifecycle ko manage karein. Ismein onboarding forms, digital profiles, aur academic tracking shaamil hain.",
    "05_operations": "Operations hue aasaan. Payroll handle karein, assets track karein, aur fee structures configure karein. EduERP aapke Finance aur HR departments ko ek saath laata hai.",
    "06_modules": "Transportation, Hostels, Library, aur Inventory. Koi bhi module choota nahi hai. Hum aapke campus ke har hisse ke liye tools dete hain.",
    "07_security": "Security standard hai. Role-based control, encrypted data, aur alag tenant schemas ke saath, aapka data surakshit hai. Aur jaise aap badhte hain, EduERP bhi aapke saath badhta hai.",
    "08_outro": "EduERP by Codefyn. Smart. Scalable. Secure. Aaj hi apne institution ko badle."
}

def generate_audio(script, lang, tld, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    print(f"Generating {lang} ({tld}) voiceovers in {output_folder}...")
    for filename, text in script.items():
        try:
            tts = gTTS(text=text, lang=lang, tld=tld)
            save_path = os.path.join(output_folder, f"{filename}.mp3")
            tts.save(save_path)
            print(f"Saved: {save_path}")
        except Exception as e:
            print(f"Error generating {filename}: {e}")

# Generate Indian English (en-in)
generate_audio(script_en, 'en', 'co.in', 'voiceovers_indian_english')

# Generate Hindi (hi)
generate_audio(script_hi, 'hi', 'co.in', 'voiceovers_hindi')

print("All voiceovers generated.")
