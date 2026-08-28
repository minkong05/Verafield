import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

type Theme = "light" | "dark";

const getInitialTheme = (): Theme => {
  const savedTheme = window.localStorage.getItem("tapak-theme");

  if (savedTheme === "light" || savedTheme === "dark") {
    return savedTheme;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("tapak-theme", theme);
  }, [theme]);

  const nextTheme = theme === "light" ? "dark" : "light";

  return (
    <button
      aria-label={`Use ${nextTheme} mode`}
      className="icon-button"
      type="button"
      onClick={() => setTheme(nextTheme)}
    >
      {theme === "light" ? <Moon aria-hidden="true" /> : <Sun aria-hidden="true" />}
    </button>
  );
}

export default ThemeToggle;
