import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { checkout, getShippingQuote, initializePayment } from "../api/orders";
import { listAddresses } from "../api/auth";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import usePageMeta from "../hooks/usePageMeta";

const emptyForm = {
  full_name: "",
  phone_number: "",
  line1: "",
  line2: "",
  city: "",
  state: "",
  country: "Nigeria",
};

export default function Checkout() {
  const navigate = useNavigate();
  const { cart, cartLoading, cartError, refresh } = useCart() || {};
  const { user } = useAuth();
  const [form, setForm] = useState(emptyForm);
  const [addresses, setAddresses] = useState([]);
  const [addressId, setAddressId] = useState("");
  const [shippingMethod, setShippingMethod] = useState("delivery");
  const [shippingFee, setShippingFee] = useState(null);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  usePageMeta({
    title: "Checkout",
    description: "Complete your Tunmis Closet order and pay securely.",
    noIndex: true,
  });

  useEffect(() => {
    listAddresses()
      .then((data) => {
        const list = data.results || data;
        setAddresses(list);
        const preferred = list.find((address) => address.is_default) || list[0];
        if (preferred) setAddressId(String(preferred.id));
      })
      .catch(() => setAddresses([]));
  }, []);

  useEffect(() => {
    if (!user) return;
    setForm((current) => ({
      ...current,
      full_name: current.full_name || `${user.first_name || ""} ${user.last_name || ""}`.trim(),
      phone_number: current.phone_number || user.phone_number || "",
    }));
  }, [user]);

  const selectedAddress = useMemo(
    () => addresses.find((address) => String(address.id) === addressId),
    [addresses, addressId]
  );

  useEffect(() => {
    if (shippingMethod === "pickup") {
      setShippingFee(0);
      return;
    }
    const state = selectedAddress?.state || form.state;
    const city = selectedAddress?.city || form.city;
    if (!state.trim()) {
      setShippingFee(null);
      return;
    }

    setQuoteLoading(true);
    let active = true;
    const timer = setTimeout(() => {
      getShippingQuote({ state, city, shipping_method: "delivery" })
        .then((data) => {
          if (active) setShippingFee(Number(data.shipping_fee));
        })
        .catch(() => {
          if (!active) return;
          setShippingFee(null);
          toast.error("Could not calculate shipping. Please try again.");
        })
        .finally(() => {
          if (active) setQuoteLoading(false);
        });
    }, 400);
    return () => {
      active = false;
      clearTimeout(timer);
      setQuoteLoading(false);
    };
  }, [shippingMethod, form.state, form.city, selectedAddress]);

  const fmt = (n) =>
    Number(n).toLocaleString("en-NG", { style: "currency", currency: "NGN", maximumFractionDigits: 0 });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (shippingFee === null) {
      toast.error("Add your delivery state so we can calculate shipping.");
      return;
    }
    setSubmitting(true);
    try {
      const payload = { shipping_method: shippingMethod };
      if (addressId) payload.address_id = Number(addressId);
      else Object.assign(payload, form);

      const order = await checkout(payload);
      await refresh();
      toast.success(`Order ${order.order_number} created`);

      try {
        const payment = await initializePayment(order.id);
        window.location.href = payment.authorization_url;
      } catch {
        toast.error("Payment could not start. You can retry from your order page.");
        navigate(`/orders/${order.id}`);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not place order.");
    } finally {
      setSubmitting(false);
    }
  };

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
    return <div className="max-w-3xl mx-auto px-5 py-24 text-center text-stone">Your bag is empty.</div>;
  }

  const input =
    "w-full border border-stone/40 px-4 py-3 text-sm focus:outline-none focus:border-gold-dark";
  const total = Number(cart.total) + (shippingFee ?? 0);

  return (
    <div className="max-w-5xl mx-auto px-5 md:px-8 py-14 grid md:grid-cols-2 gap-12">
      <div>
        <h1 className="font-display text-3xl mb-8">Shipping Details</h1>

        {user && user.email_verified === false && (
          <div className="border border-gold/40 bg-porcelain-deep px-4 py-3 mb-6 text-xs text-stone">
            Your email is not verified yet.{" "}
            <Link to="/account" className="text-gold-dark underline">
              Verify it from your account
            </Link>{" "}
            so we can send order updates.
          </div>
        )}

        <div className="flex gap-3 mb-6">
          {[
            ["delivery", "Deliver to me"],
            ["pickup", "Studio pickup"],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setShippingMethod(value)}
              className={`label-track text-xs px-4 py-3 border transition-colors ${
                shippingMethod === value
                  ? "bg-ink text-porcelain border-ink"
                  : "border-stone/30 hover:border-gold-dark"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {addresses.length > 0 && (
            <label className="block">
              <span className="label-track text-xs text-stone">Saved address</span>
              <select
                value={addressId}
                onChange={(e) => setAddressId(e.target.value)}
                className={`${input} mt-2`}
              >
                <option value="">Use a new address</option>
                {addresses.map((address) => (
                  <option key={address.id} value={address.id}>
                    {address.full_name} — {address.line1}, {address.city}, {address.state}
                  </option>
                ))}
              </select>
            </label>
          )}

          {selectedAddress ? (
            <div className="border border-stone/20 p-4 text-sm text-stone leading-relaxed">
              <p className="text-ink font-medium mb-1">{selectedAddress.full_name}</p>
              <p>{selectedAddress.phone_number}</p>
              <p>
                {selectedAddress.line1}
                {selectedAddress.line2 ? `, ${selectedAddress.line2}` : ""}
              </p>
              <p>
                {selectedAddress.city}, {selectedAddress.state}, {selectedAddress.country}
              </p>
              <button
                type="button"
                onClick={() => setAddressId("")}
                className="text-xs text-gold-dark underline mt-3"
              >
                Use a different address
              </button>
            </div>
          ) : (
            <>
              <input
                required={shippingMethod === "delivery"}
                placeholder="Full name"
                className={input}
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
              <input
                required={shippingMethod === "delivery"}
                placeholder="Phone number"
                className={input}
                value={form.phone_number}
                onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
              />
              {shippingMethod === "delivery" && (
                <>
                  <input required placeholder="Address line 1" className={input} value={form.line1} onChange={(e) => setForm({ ...form, line1: e.target.value })} />
                  <input placeholder="Address line 2 (optional)" className={input} value={form.line2} onChange={(e) => setForm({ ...form, line2: e.target.value })} />
                  <div className="grid grid-cols-2 gap-4">
                    <input required placeholder="City" className={input} value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
                    <input required placeholder="State" className={input} value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} />
                  </div>
                  <input required placeholder="Country" className={input} value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} />
                  <p className="text-xs text-stone">
                    Not sure about sizing? <Link to="/size-guide" className="text-gold-dark underline">Check the size guide</Link>.
                  </p>
                </>
              )}
            </>
          )}

          {shippingMethod === "pickup" && (
            <p className="text-xs text-stone">
              Pick up free from 44 Yusuf Street, Selewu, Igbogbo, Ikorodu, Lagos. We will message you when your order is ready.
            </p>
          )}

          <button type="submit" disabled={submitting} className="btn btn-primary w-full">
            {submitting ? "Placing Order…" : "Continue to Payment"}
          </button>
        </form>
      </div>

      <div>
        <h2 className="font-display text-2xl mb-8">Order Summary</h2>
        <div className="space-y-3 mb-6">
          {cart.items.map((item) => (
            <div key={item.id} className="flex justify-between text-sm">
              <span>
                {item.product_name} × {item.quantity}
                {item.size ? <span className="text-stone"> — {item.size}</span> : null}
              </span>
              <span>{fmt(item.subtotal)}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-stone/20 pt-4 space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-stone">Subtotal</span><span>{fmt(cart.total)}</span></div>
          <div className="flex justify-between">
            <span className="text-stone">Shipping</span>
            <span>
              {shippingMethod === "pickup"
                ? "Free"
                : shippingFee === null
                  ? "Enter state"
                  : quoteLoading
                    ? "Calculating…"
                    : fmt(shippingFee)}
            </span>
          </div>
          <div className="flex justify-between font-medium text-base pt-2">
            <span>Total</span>
            <span>{shippingFee === null ? "—" : fmt(total)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
