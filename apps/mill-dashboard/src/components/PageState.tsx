import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";

interface PageStateProps {
  kind: "loading" | "error" | "empty";
  message: string;
  onRetry?: () => void;
}

function PageState({ kind, message, onRetry }: PageStateProps) {
  const Icon = kind === "loading" ? LoaderCircle : kind === "error" ? AlertCircle : Inbox;

  return (
    <section className="page-state" role={kind === "error" ? "alert" : "status"}>
      <Icon aria-hidden="true" className={kind === "loading" ? "page-state__spinner" : ""} />
      <h2>{kind === "loading" ? "Loading workspace" : kind === "error" ? "Could not load data" : "Nothing here yet"}</h2>
      <p>{message}</p>
      {onRetry && <button className="button button--primary" type="button" onClick={onRetry}>Try again</button>}
    </section>
  );
}

export default PageState;
