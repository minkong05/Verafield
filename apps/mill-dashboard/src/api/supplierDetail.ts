import type {
  ConsentRecord,
  DeforestationCheck,
  FieldVerificationCheck,
  GapAssessment,
  LabourDeclaration,
  LandOwnershipAssessment,
  NationalSystemsLookup,
  Plot,
  UUID,
  YieldLicenceCheck,
} from "../types/api";
import { ApiError, apiRequest } from "./client";

const householdPath = (millId: UUID, householdId: UUID) =>
  `/mills/${millId}/households/${householdId}`;

async function optionalRequest<T>(path: string): Promise<T | null> {
  try {
    return await apiRequest<T>(path);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export function getGapAssessment(millId: UUID, householdId: UUID) {
  return optionalRequest<GapAssessment>(`${householdPath(millId, householdId)}/gap-assessment`);
}

export function getLandOwnership(millId: UUID, householdId: UUID) {
  return optionalRequest<LandOwnershipAssessment>(`${householdPath(millId, householdId)}/land-ownership-assessment`);
}

export function getLabourDeclaration(millId: UUID, householdId: UUID) {
  return optionalRequest<LabourDeclaration>(`${householdPath(millId, householdId)}/labour-declaration`);
}

export function getConsent(millId: UUID, householdId: UUID) {
  return optionalRequest<ConsentRecord>(`${householdPath(millId, householdId)}/consent`);
}

export function getPlots(millId: UUID, householdId: UUID) {
  return apiRequest<Plot[]>(`${householdPath(millId, householdId)}/plots`);
}

export function getYieldLicenceCheck(millId: UUID, householdId: UUID) {
  return optionalRequest<YieldLicenceCheck>(`${householdPath(millId, householdId)}/yield-licence-check`);
}

export function getNationalSystems(millId: UUID, householdId: UUID) {
  return optionalRequest<NationalSystemsLookup>(`${householdPath(millId, householdId)}/national-systems-lookup`);
}

export function getDeforestationCheck(millId: UUID, householdId: UUID, plotId: UUID) {
  return optionalRequest<DeforestationCheck>(`${householdPath(millId, householdId)}/plots/${plotId}/deforestation-check`);
}

export function getFieldVerificationCheck(millId: UUID, householdId: UUID, plotId: UUID) {
  return optionalRequest<FieldVerificationCheck>(`${householdPath(millId, householdId)}/plots/${plotId}/field-verification-check`);
}
