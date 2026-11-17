import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import client from "../api/client";
import usePageMeta from "../hooks/usePageMeta";

const statusColor = {
  pending: "text-stone",
  paid: "text-gold-dark",
  processing: "text-gold-dark",
  shipped: "text-gold-dark",
  delivered: "text-green-700",
  cancelled: "text-red-700",
};

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [next, setNext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");

  usePageMeta({
    title: "My Orders",
    description: "Track your Tunmis Closet orders and payments.",
    noIndex: true,
  });

  const load = async (url = null) => {
    if (url) setLoadingMore(true);
    else setLoading(true);
    try {
      const { data } = await client.get(url || "/orders/");
      setOrders((current) => (url ? [...current, ...(data.results || [])] : data.results || data));
      setNext(data.next || null);
      setError("");
    } catch {
      setError("We could not load your orders. Please try again.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const fmt = (n) =>
    Number(n).toLocaleString("en-NG", { style: "currency", currency: "NGN", maximumFractionDigits: 0 });

  return (
    <div className="max-w-4xl mx-auto px-5 md:px-8 py-14">
      <h1 className="font-display text-4xl mb-10">Your Orders</h1>

      {loading ? (
        <p className="text-stone text-sm">Loading orders…</p>
      ) : error ? (
        <div>
          <p className="text-stone text-sm mb-4">{error}</p>
          <button onClick={() => load()} className="btn btn-outline">Retry</button>
        </div>
      ) : orders.length === 0 ? (
        <div>
          <p className="text-stone text-sm mb-6">No orders yet.</p>
          <Link to="/shop" className="btn btn-primary">Start shopping</Link>
        </div>
      ) : (
        <>
          <div className="space-y-6">
            {orders.map((order) => (
              <Link
                key={order.id}
                to={`/orders/${order.id}`}
                className="block border border-stone/20 p-6 hover:border-gold/60 transition-colors"
              >
                <div className="flex justify-between items-start mb-4 gap-4">
                  <div>
                    <p className="font-medium">{order.order_number}</p>
                    <p className="text-xs text-stone">
                      {new Date(order.created_at).toLocaleDateString("en-NG", { dateStyle: "medium" })}
                    </p>
                  </div>
                  <span className={`label-track text-xs ${statusColor[order.status] || "text-stone"}`}>
                    {order.status}
                  </span>
                </div>
                <div className="space-y-1 mb-4">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span>{item.product_name} × {item.quantity}</span>
                      <span>{fmt(item.subtotal)}</span>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between items-center text-sm font-medium border-t border-stone/15 pt-3">
                  <span>Total {fmt(order.total_amount)}</span>
                  <span className="inline-flex items-center gap-1 text-gold-dark">
                    View <ChevronRight size={15} />
                  </span>
                </div>
              </Link>
            ))}
          </div>

          {next && (
            <div className="text-center mt-10">
              <button onClick={() => load(next)} disabled={loadingMore} className="btn btn-outline">
                {loadingMore ? "Loading…" : "Load more"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
