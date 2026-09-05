import { AlertTriangle, ArrowRight } from "lucide-react";

import PageState from "../components/PageState";
import type { UUID } from "../types/api";
import type { ReviewItem } from "../types/ui";

interface ReviewQueuePageProps {
  items: ReviewItem[];
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  onSelectSupplier: (householdId: UUID) => void;
}

function ReviewQueuePage({ items, loading, error, onRetry, onSelectSupplier }: ReviewQueuePageProps) {
  return (
    <>
      <header className="page-heading">
        <div>
          <p className="eyebrow">Analyst worklist</p>
          <h1>Review queue</h1>
          <p className="text-muted">
            A frontend view composed from unresolved verification and renewal results.
          </p>
        </div>
        <span className="data-source-note">Derived from verification responses</span>
      </header>

      <section className="data-panel">
        <header className="data-panel__header">
          <div>
            <h2>Open items</h2>
            <p>{items.length} records require analyst attention.</p>
          </div>
        </header>
        {loading ? <PageState kind="loading" message="Checking supplier compliance records." /> : error ? <PageState kind="error" message={error} onRetry={onRetry} /> : items.length === 0 ? <PageState kind="empty" message="All supplier checks are currently clear." /> : <div className="review-list">
          {items.map((item) => (
            <button
              className="review-row"
              key={item.id}
              type="button"
              onClick={() => onSelectSupplier(item.householdId)}
            >
              <span className={`priority-icon priority-icon--${item.priority}`}>
                <AlertTriangle aria-hidden="true" />
              </span>
              <span className="review-row__content">
                <strong>{item.summary}</strong>
                <small>{item.supplierName} · {item.district} · {item.category}</small>
              </span>
              <span className={`priority priority--${item.priority}`}>{item.priority}</span>
              <ArrowRight aria-hidden="true" />
            </button>
          ))}
        </div>}
      </section>
    </>
  );
}

export default ReviewQueuePage;
