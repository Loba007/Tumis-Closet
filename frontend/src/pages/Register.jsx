import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";
import usePageMeta from "../hooks/usePageMeta";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  usePageMeta({ title: "Create Account", noIndex: true });
  const [form, setForm] = useState({ email: "", username: "", first_name: "", phone_number: "", password: "" });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await register(form);
      toast.success("Account created — check your email to verify your address.");
      navigate("/account");
    } catch (err) {
      const data = err.response?.data;
      toast.error(data ? Object.values(data).flat().join(" ") : "Could not create account.");
    } finally {
      setSubmitting(false);
    }
  };

  const input = "w-full border border-stone/40 px-4 py-3 text-sm focus:outline-none focus:border-gold-dark";

  return (
    <div className="max-w-md mx-auto px-5 py-24">
      <h1 className="font-display text-3xl mb-8 text-center">Create Account</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input required placeholder="First name" className={input} value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
        <input required placeholder="Username" className={input} value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input required type="email" placeholder="Email" className={input} value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Phone number" className={input} value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
        <input required type="password" placeholder="Password" className={input} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button type="submit" disabled={submitting} className="btn btn-primary w-full">
          {submitting ? "Creating…" : "Create Account"}
        </button>
      </form>
      <p className="text-sm text-stone text-center mt-6">
        Already have an account? <Link to="/login" className="text-gold-dark hover:underline">Sign in</Link>
      </p>
    </div>
  );
}
