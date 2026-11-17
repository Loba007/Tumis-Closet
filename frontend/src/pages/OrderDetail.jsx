import { useEffect, useRef, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { ArrowLeft, CheckCircle2, Clock, XCircle } from "lucide-react";
import {
  cancelOrder,
  getOrder,
  initializePayment,
  verifyPayment,
} from "../api/orders";
import usePageMeta from "../hooks/usePageMeta";

const statusColor = {
  pending: "text-stone",
  paid: "text-gold-dark",
  processing: "text-gold-dark",
  shipped: "text-gold-dark",
  delivered: "text-green-700",
  cancelled: "text-red-700",
};

export default function OrderDetail() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState("");
  const verifiedRef = useRef(false);

  usePageMeta({
    title: order ? `Order ${order.order_number}` : "Order",
    description: "View your Tunmis Closet order and payment status.",
    noIndex: true,
  });

  const loadOrder = async () => {
    try {
      const data = await getOrder(id);
      setOrder(data);
      setError("");
    } catch {
      setError("We could not find that order.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    setOrder(null);
    verifiedRef.current = false;
    loadOrder();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    const reference = searchParams.get("reference") || searchParams.get("trxref");
    if (!reference || !order || verifiedRef.current || order.payment_status === "success") return;

    verifiedRef.current = true;
    setVerifying(true);
    verifyPayment(reference)
      .then((payment) => {
        if (payment.status === "success") {
          toast.success("Payment confirmed — thank you!");
        } else {
          toast.error("Payment was not successful. You can try again.");
        }
        return loadOrder();
      })
      .catch(() => toast.error("We could not confirm the payment yet."))
      .finally(() => setVerifying(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [order, searchParams]);

  const handlePay = async () => {
    setPaying(true);
    try {
      const payment = await initializePayment(order.id);
      window.location.href = payment.authorization_url;
    } catch (err) {
      toast.error(err.response?.data?.detail || "Payment could not start.");
    } finally {
      setPaying(false);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm("Cancel this unpaid order and return the items to stock?")) return;
    try {
      const data = await cancelOrder(order.id);
      setOrder(data);
      toast.success("Order cancelled.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not cancel this order.");
    }
  };

  const fmt = (n) =>
    Number(n).toLocaleString("en-NG", { style: "currency", currency: "NGN", maximumFractionDigits: 0 });

  if (loading) {
    return <div className="max-w-3xl mx-auto px-5 py-20 text-sm text-stone">Loading order…</div>;
  }

  if (error || !order) {
    return (
      <div className="max-w-xl mx-auto px-5 py-24 text-center">
        <h1 className="font-display text-3xl mb-4">Order not found</h1>
        <p className="text-stone mb-8">{error || "Please check the link and try again."}</p>
        <Link to="/orders" className="btn btn-primary">Back to Orders</Link>
      </div>
    );
  }

  const isPaid = ["paid", "processing", "shipped", "delivered"].includes(order.status);

  return (
    <div className="max-w-3xl mx-auto px-5 md:px-8 py-14">
      <Link to="/orders" className="inline-flex items-center gap-2 text-sm text-stone hover:text-gold-dark mb-8">
        <ArrowLeft size={16} /> All orders
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4 mb-8">
        <div>
          <p className="label-track text-xs text-gold-dark mb-2">Order</p>
          <h1 className="font-display text-3xl">{order.order_number}</h1>
          <p className="text-xs text-stone mt-1">
            Placed {new Date(order.created_at).toLocaleDateString("en-NG", { dateStyle: "medium" })}
          </p>
        </div>
        <span className={`label-track text-xs ${statusColor[order.status] || "text-stone"}`}>
          {order.status}
        </span>
      </div>

      {verifying && (
        <div className="flex items-center gap-3 border border-gold/40 bg-porcelain-deep px-5 py-4 mb-6 text-sm">
          <Clock size={18} className="text-gold-dark" /> Confirming your payment…
        </div>
      )}

      {!verifying && isPaid && !order.refunded_at && (
        <div className="flex items-center gap-3 border border-green-700/30 bg-green-50 px-5 py-4 mb-6 text-sm text-green-800">
          <CheckCircle2 size={18} /> Payment received. We are preparing your piece.
        </div>
      )}

      {!verifying && order.status === "cancelled" && (
        <div className="flex items-center gap-3 border border-red-700/30 bg-red-50 px-5 py-4 mb-6 text-sm text-red-800">
          <XCircle size={18} /> This order was cancelled.
        </div>
      )}

      {order.refund_required && (
        <div className="flex items-center gap-3 border border-gold/40 bg-porcelain-deep px-5 py-4 mb-6 text-sm text-stone">
          <Clock size={18} className="text-gold-dark" />
          A payment was received for this cancelled order. The studio will contact you to arrange a refund.
        </div>
      )}

      {order.refunded_at && (
        <div className="flex items-center gap-3 border border-green-700/30 bg-green-50 px-5 py-4 mb-6 text-sm text-green-800">
          <CheckCircle2 size={18} /> Your payment has been refunded.
        </div>
      )}

      <div className="border border-stone/20 p-6 mb-6">
        <h2 className="font-display text-xl mb-4">Items</h2>
        <div className="space-y-3">
          {order.items.map((item) => (
            <div key={item.id} className="flex justify-between text-sm">
              <span>
                {item.product_name} × {item.quantity}
                <span className="text-stone">
                  {item.size ? ` — ${item.size}` : ""}{item.color ? ` / ${item.color}` : ""}
                </span>
              </span>
              <span>{fmt(item.subtotal)}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-stone/15 mt-5 pt-4 space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-stone">Subtotal</span><span>{fmt(order.subtotal)}</span></div>
          <div className="flex justify-between">
            <span className="text-stone">
              Shipping {order.shipping_method === "pickup" ? "(studio pickup)" : ""}
            </span>
            <span>{fmt(order.shipping_fee)}</span>
          </div>
          <div className="flex justify-between font-medium text-base pt-2"><span>Total</span><span>{fmt(order.total_amount)}</span></div>
        </div>
      </div>

      <div className="border border-stone/20 p-6 mb-8">
        <h2 className="font-display text-xl mb-3">Delivery</h2>
        {order.shipping_method === "pickup" ? (
          <p className="text-sm text-stone">Studio pickup — 44 Yusuf Street, Selewu, Igbogbo, Ikorodu, Lagos.</p>
        ) : (
          <p className="text-sm text-stone leading-relaxed">
            {order.shipping_full_name}<br />
            {order.shipping_line1}{order.shipping_line2 ? `, ${order.shipping_line2}` : ""}<br />
            {order.shipping_city}, {order.shipping_state}<br />
            {order.shipping_country} · {order.shipping_phone_number}
          </p>
        )}
      </div>

      {order.status === "pending" && order.payment_status !== "success" && (
        <div className="flex flex-col sm:flex-row gap-3">
          <button onClick={handlePay} disabled={paying} className="btn btn-primary flex-1">
            {paying ? "Starting payment…" : "Pay Now"}
          </button>
          {!["initialized", "success"].includes(order.payment_status) && (
            <button onClick={handleCancel} className="btn btn-outline">Cancel Order</button>
          )}
        </div>
      )}
      {order.status === "pending" && order.payment_status === "initialized" && (
        <p className="text-xs text-stone mt-3">
          Payment was started but not completed. Use Pay Now to finish, or contact the studio for help.
        </p>
      )}
      {order.status === "pending" && order.payment_status === "success" && (
        <p className="text-sm text-gold-dark">Payment received — the studio is confirming your order.</p>
      )}

      {order.payment_reference && (
        <p className="text-xs text-stone mt-6">Payment reference: {order.payment_reference}</p>
      )}
    </div>
  );
}
