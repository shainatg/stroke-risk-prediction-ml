path = r"c:\Users\shaina\OneDrive\Desktop\mini project\TrueTest\frontend\src\pages\WearableHealth.tsx"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("  Clock,\n", "").replace("  Clock,\r\n", "")
text = text.replace("import { useEffect, useMemo, useState }", "import { useEffect, useState }")
text = text.replace("  const [loading, setLoading] = useState(false);\n", "")
text = text.replace("  const [loading, setLoading] = useState(false);\r\n", "")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Cleaned WearableHealth.tsx")

