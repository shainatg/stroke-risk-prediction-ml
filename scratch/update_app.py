import os

app_path = r"c:\Users\shaina\OneDrive\Desktop\mini project\TrueTest\frontend\src\App.tsx"
with open(app_path, "r", encoding="utf-8") as f:
    app_content = f.read()

# 1. Update lucide imports in App.tsx
old_imports = """import {
  Activity,
  ArrowRight,
  Building2,
  CalendarClock,
  CalendarCheck,
  CheckCircle2,
  ChevronDown,
  FileHeart,
  HeartPulse,
  Menu,
  Microscope,
  PhoneCall,
  Search,
  ShieldCheck,
  Stethoscope,
  TestTube2,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";"""

new_imports = """import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Building2,
  CalendarClock,
  CalendarCheck,
  CheckCircle2,
  ChevronDown,
  FileHeart,
  FileText,
  HeartPulse,
  LogOut,
  Mail,
  Menu,
  Microscope,
  PhoneCall,
  Search,
  Send,
  ShieldCheck,
  Stethoscope,
  TestTube2,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { supabase } from "./supabase";"""

assert old_imports.replace("\r\n", "\n") in app_content.replace("\r\n", "\n"), "Imports block not found"
app_content = app_content.replace(old_imports, new_imports)
if old_imports not in app_content:
    # try replacing with normalized newlines
    app_content = app_content.replace(old_imports.replace("\n", "\r\n"), new_imports.replace("\n", "\r\n"))

# 2. Add user state & footer modal state in App component
old_state_target = """  const [_backendMessage, setBackendMessage] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);"""

new_state_insert = """  const [_backendMessage, setBackendMessage] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Authenticated user state
  const [currentUser, setCurrentUser] = useState<{
    id: string;
    name: string;
    email: string;
    initial: string;
  } | null>(null);

  // Footer Modal State: "privacy" | "terms" | "disclaimer" | "contact" | null
  const [activeFooterModal, setActiveFooterModal] = useState<
    "privacy" | "terms" | "disclaimer" | "contact" | null
  >(null);
  const [contactFormStatus, setContactFormStatus] = useState<string>("");
  const [contactForm, setContactForm] = useState({
    name: "",
    email: "",
    subject: "General Question",
    message: "",
  });

  const loadCurrentUser = async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (user) {
        const meta = user.user_metadata || {};
        let displayName = "";

        if (meta.first_name && typeof meta.first_name === "string" && meta.first_name.trim()) {
          displayName = meta.first_name.trim();
        } else if (meta.full_name && typeof meta.full_name === "string" && meta.full_name.trim()) {
          displayName = meta.full_name.trim().split(" ")[0];
        } else if (user.email) {
          const raw = user.email.split("@")[0];
          const clean = raw.replace(/[^a-zA-Z]/g, " ").trim().split(" ")[0];
          displayName = clean ? clean.charAt(0).toUpperCase() + clean.slice(1) : raw;
        }

        if (!displayName) displayName = "User";
        displayName = displayName.charAt(0).toUpperCase() + displayName.slice(1);

        setCurrentUser({
          id: user.id,
          name: displayName,
          email: user.email || "",
          initial: displayName.charAt(0).toUpperCase(),
        });
      } else {
        setCurrentUser(null);
      }
    } catch {
      setCurrentUser(null);
    }
  };

  useEffect(() => {
    loadCurrentUser();
  }, [location.pathname]);

  useEffect(() => {
    if (currentUser) {
      setContactForm((prev) => ({
        ...prev,
        name: prev.name || currentUser.name,
        email: prev.email || currentUser.email,
      }));
    }
  }, [currentUser, activeFooterModal]);

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
    } catch {}
    localStorage.removeItem("truetest_local_user");
    setCurrentUser(null);
    navigate("/");
  };"""

if old_state_target in app_content:
    app_content = app_content.replace(old_state_target, new_state_insert)
else:
    app_content = app_content.replace(old_state_target.replace("\n", "\r\n"), new_state_insert.replace("\n", "\r\n"))

# 3. Update Desktop Navbar Login / User Display
old_desktop_auth = """          <div className="hidden items-center gap-3 lg:flex">
            <button
              type="button"
              onClick={() => navigate("/login")}
              className="rounded-xl border border-[#6f8f72] px-5 py-2.5 text-sm font-semibold text-[#315c47] transition hover:bg-emerald-50"
            >
              Log in
            </button>

            <button
              type="button"
              onClick={() => navigate("/signup")}
              className="rounded-xl bg-[#5f7f65] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#4d6d54]"
            >
              Create account
            </button>
          </div>"""

new_desktop_auth = """          <div className="hidden items-center gap-3 lg:flex">
            {currentUser ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50/90 px-3.5 py-1.5 shadow-sm">
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#315c47] text-xs font-bold text-white shadow-sm">
                    {currentUser.initial}
                  </div>
                  <span className="text-sm font-semibold text-[#203f32]">
                    Hi, {currentUser.name}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:border-red-300 hover:bg-red-50 hover:text-red-600 shadow-sm"
                  title="Sign out of TrueTest"
                >
                  <LogOut size={14} />
                  <span>Log out</span>
                </button>
              </div>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => navigate("/login")}
                  className="rounded-xl border border-[#6f8f72] px-5 py-2.5 text-sm font-semibold text-[#315c47] transition hover:bg-emerald-50"
                >
                  Log in
                </button>

                <button
                  type="button"
                  onClick={() => navigate("/signup")}
                  className="rounded-xl bg-[#5f7f65] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#4d6d54]"
                >
                  Create account
                </button>
              </>
            )}
          </div>"""

if old_desktop_auth in app_content:
    app_content = app_content.replace(old_desktop_auth, new_desktop_auth)
else:
    app_content = app_content.replace(old_desktop_auth.replace("\n", "\r\n"), new_desktop_auth.replace("\n", "\r\n"))

# 4. Update Mobile Menu Drawer
old_mobile_auth = """              <div className="mt-2 grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    navigate("/login");
                  }}
                  className="rounded-xl border border-[#6f8f72] py-2.5 font-semibold text-[#315c47]"
                >
                  Log in
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    navigate("/signup");
                  }}
                  className="rounded-xl bg-[#5f7f65] py-2.5 font-semibold text-white"
                >
                  Sign up
                </button>
              </div>"""

new_mobile_auth = """              <div className="mt-2">
                {currentUser ? (
                  <div className="rounded-2xl border border-emerald-200 bg-emerald-50/80 p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#315c47] font-bold text-white shadow-sm">
                        {currentUser.initial}
                      </div>
                      <div>
                        <p className="font-bold text-[#203f32]">Hi, {currentUser.name}</p>
                        <p className="text-xs text-slate-500">{currentUser.email}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setMobileMenuOpen(false);
                        handleLogout();
                      }}
                      className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl border border-red-200 bg-white py-2 text-center text-xs font-semibold text-red-600 shadow-sm transition hover:bg-red-50"
                    >
                      <LogOut size={14} />
                      Log out
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        setMobileMenuOpen(false);
                        navigate("/login");
                      }}
                      className="rounded-xl border border-[#6f8f72] py-2.5 font-semibold text-[#315c47]"
                    >
                      Log in
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setMobileMenuOpen(false);
                        navigate("/signup");
                      }}
                      className="rounded-xl bg-[#5f7f65] py-2.5 font-semibold text-white"
                    >
                      Sign up
                    </button>
                  </div>
                )}
              </div>"""

if old_mobile_auth in app_content:
    app_content = app_content.replace(old_mobile_auth, new_mobile_auth)
else:
    app_content = app_content.replace(old_mobile_auth.replace("\n", "\r\n"), new_mobile_auth.replace("\n", "\r\n"))

# 5. Update Hero greeting
old_hero_badge = """              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-4 py-2 text-sm font-medium text-[#315c47] shadow-sm">
                <ShieldCheck size={17} />
                Reliable educational health guidance
              </div>"""

new_hero_badge = """              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-4 py-2 text-sm font-medium text-[#315c47] shadow-sm">
                <ShieldCheck size={17} />
                {currentUser ? `Welcome back, ${currentUser.name}! • Health Portal` : "Reliable educational health guidance"}
              </div>

              {currentUser && (
                <div className="mb-3 inline-flex items-center gap-2 rounded-xl bg-emerald-100/70 px-3.5 py-1.5 text-xs font-semibold text-[#203f32]">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                  Logged in as {currentUser.name}
                </div>
              )}"""

if old_hero_badge in app_content:
    app_content = app_content.replace(old_hero_badge, new_hero_badge)
else:
    app_content = app_content.replace(old_hero_badge.replace("\n", "\r\n"), new_hero_badge.replace("\n", "\r\n"))

# 6. Update Footer "Important" section
old_footer_important = """          <div>
            <h3 className="font-bold">Important</h3>
            <div className="mt-4 flex flex-col gap-3 text-sm text-emerald-50/70">
              <a href="#">Privacy</a>
              <a href="#">Terms</a>
              <a href="#">Safety Disclaimer</a>
              <a href="#">Contact</a>
            </div>
          </div>"""

new_footer_important = """          <div>
            <h3 className="font-bold text-white">Important</h3>
            <div className="mt-4 flex flex-col items-start gap-2 text-sm text-emerald-100/80">
              <button
                type="button"
                onClick={() => setActiveFooterModal("privacy")}
                className="flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-emerald-100 transition hover:bg-white/10 hover:text-white"
              >
                <ShieldCheck size={16} className="text-emerald-300" />
                <span>Privacy</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveFooterModal("terms")}
                className="flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-emerald-100 transition hover:bg-white/10 hover:text-white"
              >
                <FileText size={16} className="text-emerald-300" />
                <span>Terms</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveFooterModal("disclaimer")}
                className="flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-emerald-100 transition hover:bg-white/10 hover:text-white"
              >
                <AlertTriangle size={16} className="text-amber-300" />
                <span>Safety Disclaimer</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveFooterModal("contact")}
                className="flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-emerald-100 transition hover:bg-white/10 hover:text-white"
              >
                <Mail size={16} className="text-emerald-300" />
                <span>Contact</span>
              </button>
            </div>
          </div>"""

if old_footer_important in app_content:
    app_content = app_content.replace(old_footer_important, new_footer_important)
else:
    app_content = app_content.replace(old_footer_important.replace("\n", "\r\n"), new_footer_important.replace("\n", "\r\n"))

# 7. Render Footer Modal before closing </div>
old_footer_end = """        <div className="mx-auto mt-10 max-w-7xl border-t border-white/10 pt-6 text-sm text-emerald-50/60">
          © 2026 TrueTest. Educational demonstration project.
        </div>
      </footer>
    </div>
  );
}

export default App;"""

new_modal_and_end = """        <div className="mx-auto mt-10 max-w-7xl border-t border-white/10 pt-6 text-sm text-emerald-50/60">
          © 2026 TrueTest. Educational demonstration project.
        </div>
      </footer>

      {/* FOOTER POLICIES & CONTACT INTERACTIVE MODAL */}
      {activeFooterModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity"
          onClick={() => setActiveFooterModal(null)}
        >
          <div
            className="relative flex max-h-[90vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl bg-white shadow-2xl transition-all"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="border-b border-emerald-100 bg-[#f4f9f5] px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#315c47] text-white">
                    <ShieldCheck size={20} />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-[#203f32]">TrueTest Information & Policies</h2>
                    <p className="text-xs text-slate-500">Student Health-Informatics Demonstration Project</p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setActiveFooterModal(null)}
                  className="rounded-xl p-2 text-slate-400 hover:bg-slate-200/60 hover:text-slate-700"
                  aria-label="Close dialog"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Modal Navigation Tabs */}
              <div className="mt-4 flex flex-wrap gap-2 border-t border-emerald-100/80 pt-3">
                <button
                  type="button"
                  onClick={() => setActiveFooterModal("privacy")}
                  className={`flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition ${
                    activeFooterModal === "privacy"
                      ? "bg-[#315c47] text-white shadow-sm"
                      : "bg-white text-slate-600 hover:bg-emerald-50 hover:text-[#315c47]"
                  }`}
                >
                  <ShieldCheck size={14} />
                  Privacy Policy
                </button>

                <button
                  type="button"
                  onClick={() => setActiveFooterModal("terms")}
                  className={`flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition ${
                    activeFooterModal === "terms"
                      ? "bg-[#315c47] text-white shadow-sm"
                      : "bg-white text-slate-600 hover:bg-emerald-50 hover:text-[#315c47]"
                  }`}
                >
                  <FileText size={14} />
                  Terms of Service
                </button>

                <button
                  type="button"
                  onClick={() => setActiveFooterModal("disclaimer")}
                  className={`flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition ${
                    activeFooterModal === "disclaimer"
                      ? "bg-[#b91c1c] text-white shadow-sm"
                      : "bg-white text-red-700 hover:bg-red-50 hover:text-red-800"
                  }`}
                >
                  <AlertTriangle size={14} />
                  Safety Disclaimer
                </button>

                <button
                  type="button"
                  onClick={() => setActiveFooterModal("contact")}
                  className={`flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition ${
                    activeFooterModal === "contact"
                      ? "bg-[#315c47] text-white shadow-sm"
                      : "bg-white text-slate-600 hover:bg-emerald-50 hover:text-[#315c47]"
                  }`}
                >
                  <Mail size={14} />
                  Contact & Support
                </button>
              </div>
            </div>

            {/* Modal Scrollable Body */}
            <div className="overflow-y-auto p-6 md:p-8">
              {activeFooterModal === "privacy" && (
                <div className="space-y-5 text-sm text-slate-600">
                  <div className="flex items-center justify-between border-b pb-3">
                    <h3 className="text-xl font-bold text-[#203f32]">Privacy & Data Protection Policy</h3>
                    <span className="text-xs text-slate-400">Updated October 2026</span>
                  </div>

                  <p className="leading-relaxed">
                    At TrueTest, we treat personal health inquiries and diagnostic data with the highest
                    level of confidentiality. As an educational health-informatics platform, we adhere
                    strictly to data minimization and privacy-by-design standards.
                  </p>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl border border-emerald-100 bg-[#edf6ed]/40 p-4">
                      <h4 className="font-bold text-[#274c3b]">1. Zero Commercial Data Selling</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        We never sell, rent, license, or exchange your test searches, symptom checker inputs,
                        or personal records with third-party advertisers, pharmaceutical marketers, or data brokers.
                      </p>
                    </div>

                    <div className="rounded-2xl border border-emerald-100 bg-[#edf6ed]/40 p-4">
                      <h4 className="font-bold text-[#274c3b]">2. Secure Storage & Local Fallback</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        Your appointment drafts, health reminders, and insurance cards are securely managed
                        via authenticated cloud storage and encrypted client-side storage so your data remains accessible even offline.
                      </p>
                    </div>

                    <div className="rounded-2xl border border-emerald-100 bg-[#edf6ed]/40 p-4">
                      <h4 className="font-bold text-[#274c3b]">3. What Information We Store</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        Only the details you deliberately provide: your display name, contact email/phone,
                        diagnostic test selections, and wearable demo readings. Anonymous telemetry is only used to improve search speed.
                      </p>
                    </div>

                    <div className="rounded-2xl border border-emerald-100 bg-[#edf6ed]/40 p-4">
                      <h4 className="font-bold text-[#274c3b]">4. Complete User Control & Deletion</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        You retain full ownership of your records. You may delete saved appointments, purge Health Locker documents,
                        or remove your account credentials at any time.
                      </p>
                    </div>
                  </div>

                  <p className="text-xs text-slate-500 pt-2">
                    For any privacy inquiries or to request data removal, contact our data protection team at{" "}
                    <span className="font-semibold text-[#315c47]">privacy@truetest-health.org</span>.
                  </p>
                </div>
              )}

              {activeFooterModal === "terms" && (
                <div className="space-y-5 text-sm text-slate-600">
                  <div className="flex items-center justify-between border-b pb-3">
                    <h3 className="text-xl font-bold text-[#203f32]">Terms of Service</h3>
                    <span className="text-xs text-slate-400">Effective October 2026</span>
                  </div>

                  <p className="leading-relaxed">
                    Welcome to TrueTest. By browsing our website, comparing diagnostic test prices, or scheduling
                    laboratory and doctor appointments, you agree to these Terms of Service.
                  </p>

                  <div className="space-y-4">
                    <div className="rounded-2xl border border-slate-200 p-4">
                      <h4 className="font-bold text-slate-800">1. Educational & Informational Scope</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        TrueTest is designed as a student health-informatics educational resource. It compiles medical test preparation protocols, indicative price ranges across major hospital chains, and disease overviews to improve patient health literacy.
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 p-4">
                      <h4 className="font-bold text-slate-800">2. No Doctor-Patient Relationship</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        Interacting with TrueTest—including using the symptom guidance tool, generating health summary cards, or reviewing diagnostic price comparisons—does not create a doctor-patient relationship, nor does it constitute licensed medical practice.
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 p-4">
                      <h4 className="font-bold text-slate-800">3. Price Estimations & Third-Party Lab Billing</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        Prices listed for diagnostic tests (e.g., Complete Blood Count, TSH, MRI scans) are estimated demonstration figures based on regional hospital benchmarks. Final billing may vary depending on patient comorbidities, specialized contrast reagents, or hospital billing policies.
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 p-4">
                      <h4 className="font-bold text-slate-800">4. Permitted Usage</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        Users agree to use TrueTest for personal, non-commercial, and lawful healthcare discovery only. Automated scraping, malicious probing, or unauthorized disruption of services is prohibited.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeFooterModal === "disclaimer" && (
                <div className="space-y-5 text-sm text-slate-600">
                  <div className="flex items-center justify-between border-b pb-3">
                    <h3 className="text-xl font-bold text-red-700">Safety & Medical Emergency Disclaimer</h3>
                    <span className="rounded-full bg-red-100 px-3 py-0.5 text-xs font-bold text-red-700">Crucial</span>
                  </div>

                  {/* Emergency Red Banner */}
                  <div className="rounded-2xl border-2 border-red-300 bg-red-50 p-5 text-red-900">
                    <div className="flex items-start gap-3">
                      <AlertTriangle size={24} className="shrink-0 text-red-600 mt-0.5" />
                      <div>
                        <h4 className="font-bold text-base text-red-800">EMERGENCY PROTOCOL — NOT FOR CRITICAL CARE</h4>
                        <p className="mt-1.5 text-xs text-red-700 leading-relaxed">
                          TrueTest does <strong>NOT</strong> provide real-time emergency medical intervention.
                          If you or someone around you is suffering from severe chest tightness, sudden shortness of breath,
                          unconsciousness, facial drooping, speech difficulty, heavy bleeding, or severe head injury:
                        </p>
                        <div className="mt-3 flex flex-wrap items-center gap-3">
                          <a
                            href="tel:112"
                            className="inline-flex items-center gap-1.5 rounded-xl bg-red-700 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-red-800"
                          >
                            <PhoneCall size={14} />
                            Call 112 (National Emergency Helpline)
                          </a>
                          <span className="text-xs text-red-800 font-semibold">
                            Or rush to the nearest 24/7 Casualty / Trauma Center immediately.
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4 pt-2">
                    <div className="rounded-2xl border border-slate-200 p-4">
                      <h4 className="font-bold text-slate-800">1. Guidance Does Not Replace Clinical Evaluation</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        Information on tests (such as fasting rules for FBS or Lipid Profile), normal reference ranges, and symptoms are educational summaries. Only licensed physicians, specialists, and certified pathologists can provide diagnosis and treatment plans.
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 p-4">
                      <h4 className="font-bold text-slate-800">2. Consumer Wearable Health Data</h4>
                      <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                        Smartwatch biometric indicators (such as optical heart rate, SpO₂ estimation, and sleep score) shown in TrueTest are for general wellness tracking only. They are not cleared as diagnostic medical telemetry and must never be used to adjust prescription medications.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeFooterModal === "contact" && (
                <div className="space-y-6 text-sm text-slate-600">
                  <div className="flex items-center justify-between border-b pb-3">
                    <div>
                      <h3 className="text-xl font-bold text-[#203f32]">Contact & Support Desk</h3>
                      <p className="text-xs text-slate-500">Reach the TrueTest informatics team and hospital partners</p>
                    </div>
                  </div>

                  {contactFormStatus && (
                    <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-800">
                      <div className="flex items-center gap-2 font-bold text-sm">
                        <CheckCircle2 size={18} className="text-emerald-600" />
                        Message Received!
                      </div>
                      <p className="mt-1 text-xs text-emerald-700">
                        {contactFormStatus}
                      </p>
                    </div>
                  )}

                  <div className="grid gap-6 md:grid-cols-5">
                    {/* Form (3 cols) */}
                    <div className="md:col-span-3">
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          if (!contactForm.name || !contactForm.email || !contactForm.message) {
                            alert("Please fill in your name, email, and message.");
                            return;
                          }
                          const ticketId = Math.floor(10000 + Math.random() * 90000);
                          setContactFormStatus(
                            `Thank you, ${contactForm.name}! Ticket #TT-${ticketId} has been logged. Our health support team will reply to ${contactForm.email} within 24 hours.`
                          );
                          setContactForm({
                            name: currentUser?.name || "",
                            email: currentUser?.email || "",
                            subject: "General Question",
                            message: "",
                          });
                        }}
                        className="space-y-4"
                      >
                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Your Name
                          </label>
                          <input
                            type="text"
                            value={contactForm.name}
                            onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                            placeholder="e.g. Shyna"
                            required
                            className="mt-1.5 w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-800 outline-none focus:border-[#315c47] focus:ring-1 focus:ring-[#315c47]"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Email Address
                          </label>
                          <input
                            type="email"
                            value={contactForm.email}
                            onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                            placeholder="e.g. name@example.com"
                            required
                            className="mt-1.5 w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-800 outline-none focus:border-[#315c47] focus:ring-1 focus:ring-[#315c47]"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Subject
                          </label>
                          <select
                            value={contactForm.subject}
                            onChange={(e) => setContactForm({ ...contactForm, subject: e.target.value })}
                            className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none focus:border-[#315c47] focus:ring-1 focus:ring-[#315c47]"
                          >
                            <option value="General Question">General Question</option>
                            <option value="Hospital / Diagnostic Lab Partner Inquiry">Hospital / Diagnostic Lab Partner Inquiry</option>
                            <option value="Test Pricing Verification">Test Pricing Verification</option>
                            <option value="Technical Issue or Bug Report">Technical Issue or Bug Report</option>
                            <option value="Feedback & Suggestions">Feedback & Suggestions</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Your Message
                          </label>
                          <textarea
                            rows={3}
                            value={contactForm.message}
                            onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                            placeholder="How can we assist you with test booking, hospital verification, or health tools?"
                            required
                            className="mt-1.5 w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-800 outline-none focus:border-[#315c47] focus:ring-1 focus:ring-[#315c47]"
                          />
                        </div>

                        <button
                          type="submit"
                          className="flex items-center justify-center gap-2 rounded-xl bg-[#315c47] px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#203f32]"
                        >
                          <Send size={15} />
                          Send Message
                        </button>
                      </form>
                    </div>

                    {/* Info Card (2 cols) */}
                    <div className="md:col-span-2 flex flex-col justify-between rounded-2xl border border-emerald-100 bg-[#edf6ed]/50 p-5">
                      <div className="space-y-4">
                        <h4 className="font-bold text-[#203f32]">TrueTest Support Channels</h4>

                        <div className="space-y-3 text-xs text-slate-600">
                          <div>
                            <p className="font-semibold text-slate-700">Email Inquiries</p>
                            <p className="text-[#315c47] font-medium">support@truetest-health.org</p>
                          </div>

                          <div>
                            <p className="font-semibold text-slate-700">Partner Helpline</p>
                            <p className="text-slate-800 font-medium">+91 40 6821 4400</p>
                            <p className="text-[11px] text-slate-400">Mon – Sat, 9:00 AM – 6:00 PM IST</p>
                          </div>

                          <div>
                            <p className="font-semibold text-slate-700">Informatics Lab</p>
                            <p className="text-slate-700">
                              Academic Medical Center & Innovation Hub, HITEC City, Hyderabad, 500081
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 rounded-xl border border-emerald-200 bg-white p-3 text-[11px] text-slate-500">
                        <p className="font-semibold text-[#274c3b]">Emergency Support Notice</p>
                        <p className="mt-0.5">For urgent medical attention, please bypass web forms and immediately call 112.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-100 bg-slate-50 px-6 py-3 flex items-center justify-between">
              <p className="text-xs text-slate-400">TrueTest Health Informatics Project</p>
              <button
                type="button"
                onClick={() => setActiveFooterModal(null)}
                className="rounded-xl bg-slate-200 px-4 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-300"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;"""

if old_footer_end in app_content:
    app_content = app_content.replace(old_footer_end, new_modal_and_end)
else:
    app_content = app_content.replace(old_footer_end.replace("\n", "\r\n"), new_modal_and_end.replace("\n", "\r\n"))

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_content)

print("App.tsx updated successfully!")

