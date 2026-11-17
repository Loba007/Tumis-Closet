import { Link } from "react-router-dom";
import { Trash2 } from "lucide-react";
import { useCart } from "../context/CartContext";
import usePageMeta from "../hooks/usePageMeta";

export default function Cart() {
  const { cart, cartLoading, cartError, refresh, updateItem, removeItem } = useCart() || {};
  usePageMeta({ title: "Your Bag", noIndex: true });

  const fmt = (n) =>
    Number(n).toLocaleString("en-NG", { style: "currency", currency: "NGN", maximumFractionDigits: 0 });

  if (cartLoading) {
    return <div className="max-w-3xl mx-auto px-5 py-24 text-center text-stone">Loading your bag…</div>;
  }

  if (cartError) {
    return (
      <div className="max-w-3xl mx-auto px-5 py-24 text-center">
        <h1 className="font-display text-3xl mb-4">Your bag could not load</h1>
        <p className="text-stone mb-8">{cartError}</p>
        <button onClick={refresh} className="btn btn-outline">Try Again</button>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-5 py-24 text-center">
        <h1 className="font-display text-3xl mb-4">Your bag is empty</h1>
        <p className="text-stone mb-8">Pieces you add will show up here.</p>
        <Link to="/shop" className="btn btn-primary">
          Browse the Shop
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-5 md:px-8 py-14">
      <h1 className="font-display text-3xl sm:text-4xl mb-10">Your Bag</h1>
      <div className="space-y-6">
        {cart.items.map((item) => (
          <div key={item.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-stone/15 pb-6">
            <div>
              <p className="font-medium">{item.product_name}</p>
              <p className="text-sm text-stone">
                {item.variant_detail?.size}{item.variant_detail?.color ? ` / ${item.variant_detail.color}` : ""}
              </p>
            </div>
            <div className="flex items-center justify-between sm:justify-end gap-4 sm:gap-6">
              <div className="flex items-center border border-stone/40">
                <button
                  onClick={() => updateItem(item.id, item.quantity - 1)}
                  disabled={item.quantity <= 1}
                  className="w-8 h-8 disabled:opacity-30"
                  aria-label="Decrease quantity"
                >
                  −
                </button>
                <span className="w-8 text-center text-sm">{item.quantity}</span>
                <button
                  onClick={() => updateItem(item.id, item.quantity + 1)}
                  disabled={item.quantity >= (item.variant_detail?.stock_quantity ?? Infinity)}
                  className="w-8 h-8 disabled:opacity-30"
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>
              <p className="w-20 sm:w-24 text-right text-sm">{fmt(item.subtotal)}</p>
              <button onClick={() => removeItem(item.id)} aria-label="Remove item" className="text-stone hover:text-ink shrink-0">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-end mt-10">
        <div className="w-full md:w-80">
          <div className="flex justify-between mb-2 text-sm">
            <span className="text-stone">Subtotal</span>
            <span>{fmt(cart.total)}</span>
          </div>
          <p className="text-xs text-stone mb-6">Shipping calculated at checkout.</p>
          <Link to="/checkout" className="btn btn-primary block w-full">
            Proceed to Checkout
          </Link>
        </div>
      </div>
    </div>
  );
}
