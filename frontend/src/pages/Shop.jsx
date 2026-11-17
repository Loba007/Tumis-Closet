import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import client from "../api/client";
import { listCategories, listProducts } from "../api/products";
import ProductCard from "../components/ProductCard";
import usePageMeta from "../hooks/usePageMeta";

export default function Shop() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoriesError, setCategoriesError] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const activeCategory = searchParams.get("category") || "";
  const activeOrdering = searchParams.get("ordering") || "-created_at";
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [next, setNext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");

  usePageMeta({
    title: activeCategory ? `Shop — ${activeCategory}` : "Shop",
    description: "Browse ready-to-wear and bespoke pieces from Tunmis Closet.",
  });

  const setCategory = (slug) => {
    const nextParams = new URLSearchParams(searchParams);
    if (slug) nextParams.set("category", slug);
    else nextParams.delete("category");
    setSearchParams(nextParams, { replace: true });
  };

  const setOrdering = (ordering) => {
    const nextParams = new URLSearchParams(searchParams);
    if (ordering === "-created_at") nextParams.delete("ordering");
    else nextParams.set("ordering", ordering);
    setSearchParams(nextParams, { replace: true });
  };

  useEffect(() => {
    listCategories()
      .then((data) => setCategories(data.results || data))
      .catch(() => setCategoriesError(true));
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search.trim()), 400);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    setLoading(true);
    setProducts([]);
    setNext(null);
    const params = {};
    if (activeCategory) params.category__slug = activeCategory;
    if (debouncedSearch) params.search = debouncedSearch;
    if (activeOrdering) params.ordering = activeOrdering;
    listProducts(params)
      .then((data) => {
        setProducts(data.results || []);
        setNext(data.next || null);
        setError("");
      })
      .catch(() => setError("We could not load the collection. Please try again."))
      .finally(() => setLoading(false));
  }, [activeCategory, activeOrdering, debouncedSearch]);

  const loadMore = async () => {
    if (!next) return;
    setLoadingMore(true);
    try {
      const { data } = await client.get(next);
      setProducts((current) => [...current, ...(data.results || [])]);
      setNext(data.next || null);
    } catch {
      setError("Could not load more pieces.");
    } finally {
      setLoadingMore(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-5 md:px-8 py-14">
      <div className="mb-12">
        <p className="label-track text-xs text-gold-dark mb-2">The Shop</p>
        <h1 className="font-display text-4xl">Full Collection</h1>
      </div>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-12">
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={() => setCategory("")}
            className={`label-track text-xs px-4 py-2 border transition-colors ${activeCategory === "" ? "bg-ink text-porcelain border-ink" : "border-stone/30 hover:border-gold-dark"}`}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => setCategory(c.slug)}
              className={`label-track text-xs px-4 py-2 border transition-colors ${activeCategory === c.slug ? "bg-ink text-porcelain border-ink" : "border-stone/30 hover:border-gold-dark"}`}
            >
              {c.name}
            </button>
          ))}
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <label htmlFor="shop-sort" className="sr-only">Sort pieces</label>
          <select
            id="shop-sort"
            value={activeOrdering}
            onChange={(e) => setOrdering(e.target.value)}
            className="border border-stone/30 px-4 py-2 text-sm w-full sm:w-auto focus:outline-none focus:border-gold-dark"
          >
            <option value="-created_at">Newest</option>
            <option value="price">Price: Low to High</option>
            <option value="-price">Price: High to Low</option>
          </select>
          <label htmlFor="shop-search" className="sr-only">Search pieces</label>
          <input
            id="shop-search"
            type="search"
            placeholder="Search pieces…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border border-stone/30 px-4 py-2 text-sm w-full md:w-64 focus:outline-none focus:border-gold-dark"
          />
        </div>
      </div>
      {categoriesError && (
        <p className="text-sm text-stone -mt-8 mb-8">
          Categories could not load; you can still browse all available pieces.
        </p>
      )}

      {loading ? (
        <p className="text-stone text-sm">Loading…</p>
      ) : error ? (
        <div>
          <p className="text-stone text-sm mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn btn-outline">Retry</button>
        </div>
      ) : products.length > 0 ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 md:gap-8">
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
          {next && (
            <div className="text-center mt-12">
              <button onClick={loadMore} disabled={loadingMore} className="btn btn-outline">
                {loadingMore ? "Loading…" : "Load more"}
              </button>
            </div>
          )}
        </>
      ) : (
        <p className="text-stone text-sm">No pieces match yet — try a different search or category.</p>
      )}
    </div>
  );
}
