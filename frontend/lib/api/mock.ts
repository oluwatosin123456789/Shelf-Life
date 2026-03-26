/**
 * Separated mock data so it can be imported by pages during development.
 * Remove this file entirely in Phase 2.
 */
import type { ScanResult } from "./index";

export const MOCK_SCAN_RESULT: ScanResult = {
  status: "EAT_SOON",
  confidence: 0.62,
  days_left: 3,
  recommendation: "Your Banana is still good but showing signs of age. Best consumed within 4 days.",
  fruit: { id: 2, name: "Banana", subcategory: "common" },
  classification_confidence: 0.94,
  freshness_score: 0.72,
  freshness_label: "Slightly Aged",
  estimated_shelf_life: { room_temp: 3.5, fridge: 7.2, freezer: 140 },
  best_storage: "fridge",
  storage_tip: "Store at room temperature until ripe. Once ripe, move to fridge to slow decay.",
  ethylene_note: "Banana both produces and is sensitive to ethylene gas. Store away from other ethylene-producing fruits.",
  compatibility_warnings: [],
};
