import { useState, useEffect } from "react";
import { Globe } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const languages = [
  { code: "en", name: "English" },
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "it", name: "Italian" },
  { code: "pt", name: "Portuguese" },
  { code: "ru", name: "Russian" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "zh-CN", name: "Chinese (Simplified)" },
  { code: "zh-TW", name: "Chinese (Traditional)" },
  { code: "ar", name: "Arabic" },
  { code: "hi", name: "Hindi" },
  { code: "bn", name: "Bengali" },
  { code: "pa", name: "Punjabi" },
  { code: "te", name: "Telugu" },
  { code: "mr", name: "Marathi" },
  { code: "ta", name: "Tamil" },
  { code: "gu", name: "Gujarati" },
  { code: "kn", name: "Kannata" },
  { code: "ml", name: "Malayalam" },
  { code: "or", name: "Odia" },
  { code: "th", name: "Thai" },
  { code: "vi", name: "Vietnamese" },
  { code: "id", name: "Indonesian" },
  { code: "ms", name: "Malay" },
  { code: "fil", name: "Filipino" },
];

const LanguageSelector = () => {
  const [currentLanguage, setCurrentLanguage] = useState<string>("en");

  useEffect(() => {
    // Load saved language preference
    const savedLanguage = localStorage.getItem("agricare-language") || "en";
    setCurrentLanguage(savedLanguage);

    // Add Google Translate script
    const addGoogleTranslateScript = () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const gWindow = window as any;

      if (gWindow.google && gWindow.google.translate) {
        return;
      }

      const script = document.createElement("script");
      script.src =
        "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
      script.async = true;
      document.head.appendChild(script);

      // Define the callback function
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).googleTranslateElementInit = () => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const gWin = window as any;
        if (gWin.google && gWin.google.translate) {
          new gWin.google.translate.TranslateElement(
            {
              pageLanguage: "en",
              includedLanguages: languages.map((l) => l.code).join(","),
              layout:
                gWin.google.translate.TranslateElement.InlineLayout.SIMPLE,
              autoDisplay: false,
            },
            "google_translate_element"
          );
        }
      };
    };

    addGoogleTranslateScript();

    // After the script loads, poll for the widget select. This ensures the
    // injected Google select exists so we can programmatically change it.
    let tries = 0;
    const poll = setInterval(() => {
      tries += 1;
      const sel = document.querySelector(
        ".goog-te-combo"
      ) as HTMLSelectElement | null;
      if (sel) {
        // hide the original widget select (we use our own UI)
        sel.style.display = "none";
        clearInterval(poll);
      }
      if (tries > 30) {
        clearInterval(poll);
      }
    }, 300);
  }, []);

  const handleLanguageChange = (languageCode: string) => {
    setCurrentLanguage(languageCode);
    localStorage.setItem("agricare-language", languageCode);

    // Trigger Google Translate via the injected select if present
    const translateElement = document.querySelector(
      ".goog-te-combo"
    ) as HTMLSelectElement | null;
    if (translateElement) {
      translateElement.value = languageCode;
      const evt = new Event("change", { bubbles: true, cancelable: true });
      translateElement.dispatchEvent(evt);
      return;
    }

    // Fallback: set the googtrans cookie and reload. This forces the
    // Google Translate widget to apply the requested language even when the
    // injected select isn't available yet (e.g., script hasn't initialized).
    try {
      const from = "en";
      const to = languageCode;
      const cookieValue = `/${from}/${to}`;
      document.cookie = `googtrans=${cookieValue};path=/`;
      // Also set cookie with domain to be safe
      document.cookie = `googtrans=${cookieValue};path=/;domain=${window.location.hostname}`;
      setTimeout(() => window.location.reload(), 300);
    } catch (err) {
      console.error("Translation fallback failed", err);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Globe className="w-4 h-4 text-primary" />
      <Select value={currentLanguage} onValueChange={handleLanguageChange}>
        <SelectTrigger className="w-[160px] bg-background border-border/50 hover:bg-muted">
          <SelectValue placeholder="Select language" />
        </SelectTrigger>
        <SelectContent className="max-h-[300px]">
          {languages.map((lang) => (
            <SelectItem key={lang.code} value={lang.code}>
              {lang.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Hidden Google Translate Element */}
      <div id="google_translate_element" className="hidden"></div>
    </div>
  );
};

export default LanguageSelector;
