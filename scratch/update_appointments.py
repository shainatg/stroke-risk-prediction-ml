import os

apt_path = r"c:\Users\shaina\OneDrive\Desktop\mini project\TrueTest\frontend\src\pages\Appointments.tsx"
with open(apt_path, "r", encoding="utf-8") as f:
    apt_content = f.read()

# 1. Add import { supabase } from "../supabase";
old_import = 'import { hospitals } from "../data/hospitals";'
new_import = 'import { hospitals } from "../data/hospitals";\nimport { supabase } from "../supabase";'

if old_import in apt_content:
    apt_content = apt_content.replace(old_import, new_import)
else:
    apt_content = apt_content.replace(old_import.replace("\n", "\r\n"), new_import.replace("\n", "\r\n"))

# 2. Add currentUser state and useEffect
old_state = """  const [patientName, setPatientName] = useState("");
  const [phone, setPhone] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("Male");
  const [notes, setNotes] = useState(initialTest ? `Test requested: ${initialTest}` : "");"""

new_state = """  const [patientName, setPatientName] = useState("");
  const [phone, setPhone] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("Male");
  const [notes, setNotes] = useState(initialTest ? `Test requested: ${initialTest}` : "");

  // Authenticated user state & prefill
  const [currentUser, setCurrentUser] = useState<{
    name: string;
    phone: string;
    age: string;
    gender: string;
    email: string;
  } | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser();
        if (user) {
          const meta = user.user_metadata || {};
          let name = "";
          if (meta.first_name) {
            name = meta.first_name + (meta.last_name ? ` ${meta.last_name}` : "");
          } else if (meta.full_name) {
            name = meta.full_name;
          } else if (user.email) {
            const raw = user.email.split("@")[0];
            const clean = raw.replace(/[^a-zA-Z]/g, " ").trim().split(" ")[0];
            name = clean ? clean.charAt(0).toUpperCase() + clean.slice(1) : raw;
          }

          if (name) {
            name = name.charAt(0).toUpperCase() + name.slice(1);
          }

          const phoneVal = meta.contact_number || user.phone || "";
          const ageVal = meta.age ? String(meta.age) : "";
          const genderVal = meta.gender || "Male";

          setCurrentUser({
            name,
            phone: phoneVal,
            age: ageVal,
            gender: genderVal,
            email: user.email || "",
          });

          // Pre-fill form fields if not already populated
          setPatientName((prev) => prev || name);
          setPhone((prev) => prev || phoneVal);
          setAge((prev) => prev || ageVal);
          if (meta.gender) setGender(meta.gender);
        }
      } catch (err) {
        console.warn("Could not load user in appointments:", err);
      }
    };
    fetchUser();
  }, []);"""

if old_state in apt_content:
    apt_content = apt_content.replace(old_state, new_state)
else:
    apt_content = apt_content.replace(old_state.replace("\n", "\r\n"), new_state.replace("\n", "\r\n"))

# 3. Add user greeting in Appointments Header
old_header_actions = """          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => navigate("/price-comparison")}
              className="hidden sm:inline-flex items-center gap-1.5 text-sm font-semibold text-[#315c47] hover:underline"
            >
              <TestTube2 size={16} />
              Compare Prices
            </button>
            <button
              type="button"
              onClick={() => navigate("/hospital-finder")}
              className="hidden md:inline-flex items-center gap-1.5 text-sm font-semibold text-slate-600 hover:text-[#315c47]"
            >
              <Building2 size={16} />
              Hospital Finder
            </button>
          </div>"""

new_header_actions = """          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => navigate("/price-comparison")}
              className="hidden sm:inline-flex items-center gap-1.5 text-sm font-semibold text-[#315c47] hover:underline"
            >
              <TestTube2 size={16} />
              Compare Prices
            </button>
            <button
              type="button"
              onClick={() => navigate("/hospital-finder")}
              className="hidden md:inline-flex items-center gap-1.5 text-sm font-semibold text-slate-600 hover:text-[#315c47]"
            >
              <Building2 size={16} />
              Hospital Finder
            </button>
            {currentUser && (
              <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50/90 px-3 py-1.5 text-xs font-semibold text-[#274c3b]">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#315c47] text-[10px] text-white">
                  {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : "U"}
                </span>
                <span>Hi, {currentUser.name.split(" ")[0]}</span>
              </div>
            )}
          </div>"""

if old_header_actions in apt_content:
    apt_content = apt_content.replace(old_header_actions, new_header_actions)
else:
    apt_content = apt_content.replace(old_header_actions.replace("\n", "\r\n"), new_header_actions.replace("\n", "\r\n"))

# 4. Step 4 Patient Details badge
old_step4_label = """                {/* 4. Patient Information */}
                <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                  <label className="block text-sm font-bold text-slate-800">
                    Step 4: Patient Details
                  </label>"""

new_step4_label = """                {/* 4. Patient Information */}
                <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="flex items-center justify-between">
                    <label className="block text-sm font-bold text-slate-800">
                      Step 4: Patient Details
                    </label>
                    {currentUser && (
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-[#274c3b]">
                        <CheckCircle2 size={13} className="text-[#315c47]" />
                        Auto-filled for {currentUser.name}
                      </span>
                    )}
                  </div>"""

if old_step4_label in apt_content:
    apt_content = apt_content.replace(old_step4_label, new_step4_label)
else:
    apt_content = apt_content.replace(old_step4_label.replace("\n", "\r\n"), new_step4_label.replace("\n", "\r\n"))

with open(apt_path, "w", encoding="utf-8") as f:
    f.write(apt_content)

print("Appointments.tsx updated successfully!")

