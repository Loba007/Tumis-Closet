import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { fetchWishlist, removeFromWishlist } from "../api/wishlist";
import ProductCard from "../components/ProductCard";
import usePageMeta from "../hooks/usePageMeta";

export default function Wishlist() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  usePageMeta({ title: "Wishlist", noIndex: true });

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    fetchWishlist()
      .then((data) => {
        if (active) setItems(data);
      })
      .catch(() => {
        if (active) setError("Your wishlist could not load. Please try again.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [reload]);

  const handleRemove = async (product) => {
    try {
      await removeFromWishlist(product.id);
      setItems((current) => current.filter((item) => item.product !== product.id));
      toast.success("Removed from wishlist");
    } catch {
      toast.error("Could not remove this piece from your wishlist.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-5 md:px-8 py-14">
      <h1 className="font-display text-4xl mb-10">Your Wishlist</h1>
      {loading ? (
        <p className="text-stone text-sm">Loading your wishlist…</p>
      ) : error ? (
        <div>
          <p className="text-stone text-sm mb-4">{error}</p>
          <button onClick={() => setReload((value) => value + 1)} className="btn btn-outline">
            Try Again
          </button>
        </div>
      ) : items.length === 0 ? (
        <p className="text-stone text-sm">Nothing saved yet — tap the heart icon on a piece to save it here.</p>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
          {items.map((item) => (
            <ProductCard
              key={item.id}
              product={item.product_detail}
              onWishlist={() => handleRemove(item.product_detail)}
              wishlistActionLabel={`Remove ${item.product_detail.name} from wishlist`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
