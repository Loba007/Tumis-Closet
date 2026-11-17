import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import {
  createAddress,
  deleteAddress,
  listAddresses,
  resendEmailVerification,
  updateAddress,
  updateMe,
} from "../api/auth";
import { useAuth } from "../context/AuthContext";
import usePageMeta from "../hooks/usePageMeta";

const emptyAddress = {
  full_name: "",
  phone_number: "",
  line1: "",
  line2: "",
  city: "",
  state: "",
  country: "Nigeria",
  is_default: false,
};

export default function Account() {
  const { user, setUser } = useAuth();
  const [profile, setProfile] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone_number: user?.phone_number || "",
  });
  const [addresses, setAddresses] = useState([]);
  const [address, setAddress] = useState(emptyAddress);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingAddress, setSavingAddress] = useState(false);
  const [sendingVerification, setSendingVerification] = useState(false);

  usePageMeta({ title: "My Account", noIndex: true });

  const loadAddresses = () => {
    listAddresses()
      .then((data) => setAddresses(data.results || data))
      .catch(() => toast.error("Could not load your addresses."));
  };

  useEffect(() => {
    loadAddresses();
  }, []);

  const handleProfile = async (event) => {
    event.preventDefault();
    setSavingProfile(true);
    try {
      const updated = await updateMe(profile);
      setUser(updated);
      toast.success("Profile updated.");
    } catch {
      toast.error("Could not update your profile.");
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddress = async (event) => {
    event.preventDefault();
    setSavingAddress(true);
    try {
      await createAddress(address);
      setAddress(emptyAddress);
      setShowAddressForm(false);
      loadAddresses();
      toast.success("Address saved.");
    } catch (err) {
      const data = err.response?.data;
      toast.error(data ? Object.values(data).flat().join(" ") : "Could not save this address.");
    } finally {
      setSavingAddress(false);
    }
  };

  const handleResendVerification = async () => {
    setSendingVerification(true);
    try {
      await resendEmailVerification();
      toast.success("Verification email sent.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not send the verification email.");
    } finally {
      setSendingVerification(false);
    }
  };

  const makeDefault = async (id) => {
    try {
      await updateAddress(id, { is_default: true });
      loadAddresses();
      toast.success("Default address updated.");
    } catch {
      toast.error("Could not update the default address.");
    }
  };

  const removeAddress = async (id) => {
    if (!window.confirm("Remove this saved address?")) return;
    try {
      await deleteAddress(id);
      setAddresses((current) => current.filter((item) => item.id !== id));
      toast.success("Address removed.");
    } catch {
      toast.error("Could not remove this address.");
    }
  };

  const input =
    "w-full border border-stone/40 px-4 py-3 text-sm focus:outline-none focus:border-gold-dark";

  return (
    <div className="max-w-4xl mx-auto px-5 md:px-8 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-10">
        <div>
          <p className="label-track text-xs text-gold-dark mb-2">Your Account</p>
          <h1 className="font-display text-4xl">Profile & Addresses</h1>
        </div>
        <Link to="/orders" className="btn btn-outline">My Orders</Link>
      </div>

      {user && !user.email_verified && (
        <div className="border border-gold/40 bg-porcelain-deep px-5 py-4 mb-8 flex flex-wrap items-center justify-between gap-4 text-sm">
          <p className="text-stone">
            Please verify <strong className="text-ink">{user.email}</strong> so we can send order updates.
          </p>
          <button
            type="button"
            onClick={handleResendVerification}
            disabled={sendingVerification}
            className="text-xs text-gold-dark underline disabled:opacity-60"
          >
            {sendingVerification ? "Sending…" : "Resend verification email"}
          </button>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-12">
        <section>
          <h2 className="font-display text-2xl mb-5">Profile</h2>
          <p className="text-sm text-stone mb-5">{user?.email}</p>
          <form onSubmit={handleProfile} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <label className="block">
                <span className="text-xs text-stone">First name</span>
                <input className={`${input} mt-1`} value={profile.first_name} onChange={(e) => setProfile({ ...profile, first_name: e.target.value })} />
              </label>
              <label className="block">
                <span className="text-xs text-stone">Last name</span>
                <input className={`${input} mt-1`} value={profile.last_name} onChange={(e) => setProfile({ ...profile, last_name: e.target.value })} />
              </label>
            </div>
            <label className="block">
              <span className="text-xs text-stone">Phone number</span>
              <input className={`${input} mt-1`} value={profile.phone_number} onChange={(e) => setProfile({ ...profile, phone_number: e.target.value })} />
            </label>
            <button type="submit" disabled={savingProfile} className="btn btn-primary">
              {savingProfile ? "Saving…" : "Save Profile"}
            </button>
          </form>
        </section>

        <section>
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-display text-2xl">Addresses</h2>
            <button onClick={() => setShowAddressForm((open) => !open)} className="text-xs text-gold-dark underline">
              {showAddressForm ? "Cancel" : "Add address"}
            </button>
          </div>

          {addresses.length === 0 && !showAddressForm && (
            <p className="text-sm text-stone">No saved addresses yet.</p>
          )}

          <div className="space-y-4 mb-6">
            {addresses.map((item) => (
              <div key={item.id} className="border border-stone/20 p-4 text-sm">
                <div className="flex justify-between gap-3">
                  <div className="text-stone leading-relaxed">
                    <p className="text-ink font-medium">
                      {item.full_name}
                      {item.is_default && <span className="ml-2 text-[10px] label-track text-gold-dark">Default</span>}
                    </p>
                    <p>{item.phone_number}</p>
                    <p>{item.line1}{item.line2 ? `, ${item.line2}` : ""}</p>
                    <p>{item.city}, {item.state}, {item.country}</p>
                  </div>
                  <div className="flex flex-col gap-2 text-right shrink-0">
                    {!item.is_default && (
                      <button onClick={() => makeDefault(item.id)} className="text-xs text-gold-dark underline">Make default</button>
                    )}
                    <button onClick={() => removeAddress(item.id)} className="text-xs text-stone underline">Remove</button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {showAddressForm && (
            <form onSubmit={handleAddress} className="space-y-3 border border-stone/20 p-5">
              <input required placeholder="Full name" className={input} value={address.full_name} onChange={(e) => setAddress({ ...address, full_name: e.target.value })} />
              <input required placeholder="Phone number" className={input} value={address.phone_number} onChange={(e) => setAddress({ ...address, phone_number: e.target.value })} />
              <input required placeholder="Address line 1" className={input} value={address.line1} onChange={(e) => setAddress({ ...address, line1: e.target.value })} />
              <input placeholder="Address line 2 (optional)" className={input} value={address.line2} onChange={(e) => setAddress({ ...address, line2: e.target.value })} />
              <div className="grid grid-cols-2 gap-3">
                <input required placeholder="City" className={input} value={address.city} onChange={(e) => setAddress({ ...address, city: e.target.value })} />
                <input required placeholder="State" className={input} value={address.state} onChange={(e) => setAddress({ ...address, state: e.target.value })} />
              </div>
              <input required placeholder="Country" className={input} value={address.country} onChange={(e) => setAddress({ ...address, country: e.target.value })} />
              <label className="flex items-center gap-2 text-sm text-stone">
                <input type="checkbox" checked={address.is_default} onChange={(e) => setAddress({ ...address, is_default: e.target.checked })} />
                Use as my default address
              </label>
              <button type="submit" disabled={savingAddress} className="btn btn-primary">
                {savingAddress ? "Saving…" : "Save Address"}
              </button>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}
