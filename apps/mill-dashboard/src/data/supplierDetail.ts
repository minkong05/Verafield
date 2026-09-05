import {
  getConsent,
  getDeforestationCheck,
  getFieldVerificationCheck,
  getGapAssessment,
  getLabourDeclaration,
  getLandOwnership,
  getNationalSystems,
  getPlots,
  getYieldLicenceCheck,
} from "../api/supplierDetail";
import { usesMockData } from "./dashboard";
import { supplierDetails } from "../mocks/dashboard";
import type { MillDashboardSupplier, RenewalStatus } from "../types/api";
import type { SupplierDetail } from "../types/ui";

export async function loadSupplierDetail(
  supplier: MillDashboardSupplier,
  renewal: RenewalStatus | null,
): Promise<SupplierDetail> {
  if (usesMockData) return supplierDetails[supplier.household_id];

  const { mill_id: millId, household_id: householdId } = supplier;
  const [gapAssessment, landOwnership, labourDeclaration, consent, plots, yieldLicenceCheck, nationalSystems] =
    await Promise.all([
      getGapAssessment(millId, householdId),
      getLandOwnership(millId, householdId),
      getLabourDeclaration(millId, householdId),
      getConsent(millId, householdId),
      getPlots(millId, householdId),
      getYieldLicenceCheck(millId, householdId),
      getNationalSystems(millId, householdId),
    ]);

  const [deforestationResults, fieldResults] = await Promise.all([
    Promise.all(plots.map((plot) => getDeforestationCheck(millId, householdId, plot.id))),
    Promise.all(plots.map((plot) => getFieldVerificationCheck(millId, householdId, plot.id))),
  ]);

  return {
    supplier,
    email: null,
    postalAddress: null,
    gapAssessment,
    landOwnership,
    labourDeclaration,
    consent,
    plots,
    deforestationChecks: deforestationResults.filter((item) => item !== null),
    fieldVerificationChecks: fieldResults.filter((item) => item !== null),
    yieldLicenceCheck,
    nationalSystems,
    renewal,
  };
}
