import { useEffect, useState } from "react";
import client from "../api/client";
import { listPortfolio } from "../api/products";
import ProductCard from "../components/ProductCard";
import GoldFlourish from "../components/GoldFlourish";
import usePageMeta from "../hooks/usePageMeta";

export default function Portfolio() {
  const [pieces, setPieces] = useState([]);
  const [next, setNext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");

  usePageMeta({
    title: "Portfolio",
    description: "Showcase pieces and runway work from the Tunmis Closet archive.",
  });

  useEffect(() => {
    listPortfolio()
      .then((data) => {
        setPieces(data.results || []);
        setNext(data.next || null);
      })
      .catch(() => setError("The portfolio could not be loaded. Please try again."))
      .finally(() => setLoading(false));
  }, []);

  const loadMore = async () => {
    if (!next) return;
    setLoadingMore(true);
    try {
      const { data } = await client.get(next);
      setPieces((current) => [...current, ...(data.results || [])]);
      setNext(data.next || null);
    } catch {
      setError("Could not load more portfolio pieces.");
    } finally {
      setLoadingMore(false);
    }
  };

  return (
    <div>
      <section className="bg-ink text-porcelain py-24">
        <div className="max-w-2xl mx-auto px-5 md:px-8 text-center">
          <p className="label-track text-xs text-gold-light mb-4">The Gallery</p>
          <h1 className="font-display text-5xl md:text-6xl mb-6">Portfolio</h1>
          <p className="text-stone max-w-xl mx-auto leading-relaxed">
            Showcase pieces from past collections and runway work — crafted to be seen,
            not all of them for sale.
          </p>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-5 md:px-8 py-16">
        <GoldFlourish className="text-stone mb-12" />
        {loading ? (
          <p className="text-stone text-sm text-center">Loading portfolio…</p>
        ) : error ? (
          <div className="text-center">
            <p className="text-stone text-sm mb-4">{error}</p>
            <button onClick={() => window.location.reload()} className="btn btn-outline">Retry</button>
          </div>
        ) : pieces.length === 0 ? (
          <p className="text-stone text-sm text-center">
            Portfolio pieces will appear here once added with &ldquo;portfolio only&rdquo; enabled in the admin.
          </p>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
              {pieces.map((p) => (
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
        )}
      </div>
    </div>
  );
}
