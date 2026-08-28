import { Check, MapPin, X } from "lucide-react";

import type { SupplierDetail } from "../types/ui";

interface SupplierDrawerProps {
  detail: SupplierDetail | null;
  onClose: () => void;
}

const label = (value: string) =>
  value.replaceAll("_", " ").replace(/^\w/, (character) => character.toUpperCase());

function SupplierDrawer({ detail, onClose }: SupplierDrawerProps) {
  if (!detail) return null;

  const { supplier } = detail;
  const initials = supplier.name
    .split(" ")
    .map((part) => part[0])
    .join("");

  return (
    <>
      <button className="drawer-backdrop" aria-label="Close supplier details" onClick={onClose} />
      <aside className="detail-drawer" aria-label={`${supplier.name} details`}>
        <header className="drawer-header">
          <span>Supplier record</span>
          <button className="icon-button" aria-label="Close supplier details" onClick={onClose}>
            <X aria-hidden="true" />
          </button>
        </header>

        <div className="drawer-profile">
          <span className="drawer-avatar">{initials}</span>
          <div>
            <h2>{supplier.name}</h2>
            <p>
              <MapPin aria-hidden="true" /> {supplier.district}
            </p>
          </div>
          <span className={`status status--${supplier.status}`}>{label(supplier.status)}</span>
        </div>

        <dl className="detail-grid">
          <div><dt>MPOB licence</dt><dd>{detail.nationalSystems.mpob_licence_number}</dd></div>
          <div><dt>Plots</dt><dd>{detail.plots.length}</dd></div>
          <div><dt>Land type</dt><dd>{label(detail.landOwnership.land_type)}</dd></div>
          <div><dt>Rule version</dt><dd>{detail.landOwnership.rule_version}</dd></div>
          <div className="detail-grid__wide"><dt>Email</dt><dd>{detail.email}</dd></div>
        </dl>

        <section className="drawer-section">
          <h3>Evidence checklist</h3>
          <div className="check-list">
            {detail.gapAssessment.items.map((item) => (
              <div className="check-row" key={item.id}>
                <span className={`check-icon check-icon--${item.status}`}>
                  <Check aria-hidden="true" />
                </span>
                <span>{label(item.category)}</span>
                <strong>{label(item.status)}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="drawer-section">
          <h3>Verification</h3>
          <div className="check-list">
            <div className="check-row"><span>Land ownership</span><strong>{label(detail.landOwnership.status)}</strong></div>
            <div className="check-row"><span>Deforestation</span><strong>{label(detail.deforestationChecks[0].status)}</strong></div>
            <div className="check-row"><span>Field signals</span><strong>{label(detail.fieldVerificationChecks[0].status)}</strong></div>
            <div className="check-row"><span>Yield and licence</span><strong>{label(detail.yieldLicenceCheck.status)}</strong></div>
          </div>
        </section>

        <section className="drawer-section">
          <h3>National systems</h3>
          <div className="system-row"><span>SIMS volume</span><strong>{Number(detail.nationalSystems.sims_transaction_volume_kg).toLocaleString()} kg</strong></div>
          <div className="system-row"><span>GeoSAWIT mapping</span><strong>{detail.nationalSystems.geosawit_mapping_exists ? "Available" : "Not found"}</strong></div>
          <div className="system-row"><span>e-MSPO</span><strong>{detail.nationalSystems.emspo_certification_status}</strong></div>
        </section>
      </aside>
    </>
  );
}

export default SupplierDrawer;
