import type { Psychologist } from "./types";

export const translit = (s: string): string => {
  const map: Record<string, string> = {
    а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ё: "yo", ж: "zh", з: "z", и: "i",
    й: "y", к: "k", л: "l", м: "m", н: "n", о: "o", п: "p", р: "r", с: "s", т: "t",
    у: "u", ф: "f", х: "h", ц: "ts", ч: "ch", ш: "sh", щ: "sch", ъ: "", ы: "y", ь: "",
    э: "e", ю: "yu", я: "ya",
  };
  return s.toLowerCase().split("").map((c) => map[c] || c).join("").replace(/[^a-z0-9]/g, "");
};

export const getPsychologistSlug = (psychologist: Partial<Psychologist>): string => {
  const first = psychologist.firstName ? translit(psychologist.firstName.trim()) : "";
  const last = psychologist.lastName ? translit(psychologist.lastName.trim()) : "";
  const id = psychologist.id ? psychologist.id.slice(-4) : ""
  let slug = last ? `${first}-${last}` : first || "noname";
  if (id) {
    slug = `${id}-${slug}`;
  }

  return slug;
};

export const getTimezones = (): string[] => {
  try {
    const timezones = Intl.supportedValuesOf("timeZone");
    return timezones.map((tz) => {
      try {
        const formatter = new Intl.DateTimeFormat("ru", {
          timeZone: tz,
          timeZoneName: "shortOffset",
        });
        const parts = formatter.formatToParts(new Date());
        const offset = parts.find((p) => p.type === "timeZoneName")?.value || "";
        return `${tz} (${offset})`;
      } catch {
        return tz;
      }
    });
  } catch {
    return [];
  }
};

export const getLocalTimezone = (): string => {
  const timezones = getTimezones();
  if (timezones.length === 0) return "Europe/Moscow (GMT+03:00)";
  const localTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const localOption = timezones.find((t) => t.startsWith(localTz));
  if (localOption) return localOption;
  return timezones[0];
};