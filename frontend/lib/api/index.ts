/**
 * Fresco — API Layer (Phase 2: Live Backend Integration)
 * ========================================================
 * All API interaction goes through this layer.
 * No component should call fetch() directly.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ============================================
// Error Handling
// ============================================

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "An unknown error occurred" }));
    throw new ApiError(res.status, body.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

// ============================================
// Scan API
// ============================================

export async function scanFruit(file: File): Promise<ScanResult> {
  const formData = new FormData();
  formData.append("image", file);

  const res = await fetch(`${API_BASE}/api/scan/`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<ScanResult>(res);
}

// ============================================
// Fruits API
// ============================================

export async function getFruits(page = 1, perPage = 50): Promise<FruitListResponse> {
  const res = await fetch(
    `${API_BASE}/api/fruits/?page=${page}&per_page=${perPage}`
  );
  return handleResponse<FruitListResponse>(res);
}

// ============================================
// Inventory API
// ============================================

export async function getInventory(
  sortBy: string = "expiry",
  includeExpired: boolean = true,
): Promise<InventoryListResponse> {
  const res = await fetch(
    `${API_BASE}/api/inventory/?sort_by=${sortBy}&include_expired=${includeExpired}`
  );
  return handleResponse<InventoryListResponse>(res);
}

export async function addToInventory(
  fruitId: number,
  freshnessScore: number,
  storageMethod: string,
): Promise<InventoryItemResponse> {
  const res = await fetch(`${API_BASE}/api/inventory/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fruit_id: fruitId,
      freshness_score: freshnessScore,
      storage_method: storageMethod,
    }),
  });
  return handleResponse<InventoryItemResponse>(res);
}

export async function deleteInventoryItem(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/inventory/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Delete failed" }));
    throw new ApiError(res.status, body.detail);
  }
}

// ============================================
// Compatibility API
// ============================================

export async function checkCompatibility(fruits: string[]): Promise<CompatibilityResult> {
  const res = await fetch(
    `${API_BASE}/api/fruits/compatibility?fruits=${fruits.join(",")}`
  );
  return handleResponse<CompatibilityResult>(res);
}

// ============================================
// Types (matched to backend Pydantic schemas)
// ============================================

/** Matches backend FruitResponse */
export interface FruitData {
  id: number;
  name: string;
  subcategory: string;
  shelf_life_room_temp_days: number;
  shelf_life_fridge_days: number;
  shelf_life_freezer_days: number;
  is_ethylene_producer: boolean;
  is_ethylene_sensitive: boolean;
  optimal_temp_min: number | null;
  optimal_temp_max: number | null;
  ripeness_indicator: string | null;
  storage_tips: string | null;
  image_url: string | null;
}

/** Matches backend FruitList */
export interface FruitListResponse {
  items: FruitData[];
  total: number;
  page: number;
  per_page: number;
}

/** Matches backend ScanResponse (the 3-tier contract) */
export interface ScanResult {
  // Tier 1: Decision
  status: "FRESH" | "EAT_SOON" | "EAT_TODAY" | "SPOILED";
  confidence: number;
  days_left: number;
  recommendation: string;

  // Tier 2: Details
  fruit: FruitData;
  classification_confidence: number;
  freshness_score: number;
  freshness_label: string;
  estimated_shelf_life: Record<string, number>;
  best_storage: string;
  storage_tip: string;

  // Tier 3: Context
  ethylene_note: string | null;
  compatibility_warnings: CompatibilityPair[];

  // Metadata
  image_path: string | null;
}

/** Matches backend InventoryItemResponse */
export interface InventoryItemResponse {
  id: number;
  user_id: number;
  fruit_id: number;
  freshness_score: number;
  storage_method: string;
  estimated_days_remaining: number;
  scanned_at: string;
  estimated_expiry: string;
  is_expired: boolean;
  is_consumed: boolean;
  image_path: string | null;
  quantity: number;
  notes: string | null;
  fruit: FruitData;
}

/** Matches backend InventoryListResponse */
export interface InventoryListResponse {
  items: InventoryItemResponse[];
  total: number;
  expiring_soon: number;
  expired: number;
}

/** Matches backend CompatibilityPair */
export interface CompatibilityPair {
  producer: string;
  sensitive: string;
  warning: string;
}

/** Matches backend CompatibilityResponse */
export interface CompatibilityResult {
  compatible_groups: string[][];
  incompatible_pairs: CompatibilityPair[];
  recommendation: string;
}
