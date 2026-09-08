import { LoaderCircle } from "lucide-react";
import { type FormEvent } from "react";

import ThemeToggle from "../components/ThemeToggle";
import type { LoginRequest } from "../types/api";

interface LoginPageProps {
  error: string | null;
  submitting: boolean;
  onSubmit: (credentials: LoginRequest) => void;
}

function LoginPage({ error, submitting, onSubmit }: LoginPageProps) {
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const values = new FormData(event.currentTarget);
    onSubmit({ email: String(values.get("email")), password: String(values.get("password")) });
  };

  return (
    <main className="auth-page">
      <header className="auth-page__header">
        <a className="brand" href="#" aria-label="TAPAK sign in"><span className="brand__mark">T</span><span>TAPAK</span></a>
        <ThemeToggle />
      </header>
      <section className="auth-card">
        <div><p className="eyebrow">Mill dashboard</p><h1>Sign in</h1><p className="text-muted">Use the account provided by your TAPAK administrator.</p></div>
        <form className="auth-form" onSubmit={submit}>
          <label><span>Email</span><input name="email" type="email" autoComplete="email" required autoFocus /></label>
          <label><span>Password</span><input name="password" type="password" minLength={12} autoComplete="current-password" required /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="button button--primary" type="submit" disabled={submitting}>{submitting && <LoaderCircle className="page-state__spinner" aria-hidden="true" />}{submitting ? "Signing in…" : "Sign in"}</button>
        </form>
      </section>
    </main>
  );
}

export default LoginPage;
