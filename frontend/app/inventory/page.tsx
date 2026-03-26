"use client";

import { useEffect, useState, useCallback } from "react";
import { InventoryList, FloatingAddButton, type InventoryItemData } from "@/components/inventory";
import { getInventory, deleteInventoryItem, ApiError, type InventoryListResponse } from "@/lib/api";

type FilterTab = "all" | "eat_first" | "fresh" | "expired";

function filterItems(items: InventoryItemData[], tab: FilterTab): InventoryItemData[] {
  switch (tab) {
    case "eat_first":
      return items
        .filter((i) => !i.isExpired && i.daysLeft <= 3)
        .sort((a, b) => a.daysLeft - b.daysLeft);
    case "fresh":
      return items
        .filter((i) => !i.isExpired && i.daysLeft > 3)
        .sort((a, b) => b.daysLeft - a.daysLeft);
    case "expired":
      return items.filter((i) => i.isExpired);
    default:
      return [...items].sort((a, b) => a.daysLeft - b.daysLeft);
  }
}

const tabs: { value: FilterTab; label: string }[] = [
  { value: "all", label: "All" },
  { value: "eat_first", label: "Eat First" },
  { value: "fresh", label: "Fresh" },
  { value: "expired", label: "Expired" },
];

export default function InventoryPage() {
  const [activeTab, setActiveTab] = useState<FilterTab>("eat_first");
  const [items, setItems] = useState<InventoryItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ total: 0, expiring_soon: 0, expired: 0 });

  const fetchInventory = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data: InventoryListResponse = await getInventory();

      // Transform backend InventoryItemResponse → frontend InventoryItemData
      const mapped: InventoryItemData[] = data.items.map((item) => ({
        id: item.id,
        fruitName: item.fruit.name,
        subcategory: item.fruit.subcategory,
        storageMethod: item.storage_method,
        daysLeft: item.estimated_days_remaining,
        isExpired: item.is_expired,
      }));

      setItems(mapped);
      setStats({
        total: data.total,
        expiring_soon: data.expiring_soon,
        expired: data.expired,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to load inventory. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  const handleDelete = async (id: number) => {
    try {
      await deleteInventoryItem(id);
      // Remove from local state immediately (optimistic update)
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch {
      // Refetch on failure
      fetchInventory();
    }
  };

  const freshCount = items.filter((i) => !i.isExpired && i.daysLeft > 3).length;
  const filtered = filterItems(items, activeTab);

  return (
    <div className="flex flex-col px-4 pt-4 pb-24">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Inventory</h1>
        <span className="text-[13px] text-text-muted">{stats.total} items</span>
      </div>

      {/* Summary strip */}
      <div className="flex gap-2 mb-5 overflow-x-auto">
        <span className="text-[13px] font-medium text-warning bg-surface border border-border rounded-lg px-3 py-1.5 whitespace-nowrap">
          {stats.expiring_soon} expiring
        </span>
        <span className="text-[13px] font-medium text-danger bg-surface border border-border rounded-lg px-3 py-1.5 whitespace-nowrap">
          {stats.expired} expired
        </span>
        <span className="text-[13px] font-medium text-safe bg-surface border border-border rounded-lg px-3 py-1.5 whitespace-nowrap">
          {freshCount} fresh
        </span>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-4 border-b border-border mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={`
              pb-2 text-sm font-medium min-h-0
              transition-colors duration-150
              ${
                activeTab === tab.value
                  ? "text-accent border-b-2 border-accent"
                  : "text-text-muted"
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center py-12">
          <span className="h-6 w-6 rounded-full border-2 border-accent border-t-transparent animate-spin" />
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="p-4 bg-danger/10 border border-danger/20 rounded-xl mb-4">
          <p className="text-sm text-danger">{error}</p>
          <button
            onClick={fetchInventory}
            className="text-xs text-danger/70 underline mt-1 min-h-0"
          >
            Tap to retry
          </button>
        </div>
      )}

      {/* List */}
      {!loading && !error && (
        <InventoryList items={filtered} onItemClick={handleDelete} />
      )}

      {/* FAB */}
      <FloatingAddButton />
    </div>
  );
}
