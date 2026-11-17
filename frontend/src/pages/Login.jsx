import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";
import usePageMeta from "../hooks/usePageMeta";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  usePageMeta({ title: "Sign In", noIndex: true });
  const [form, setForm] = useState({ email: "", password: "" });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login(form.email, form.password);
      toast.success("Welcome back");
      navigate(location.state?.from || "/", { replace: true });
    } catch {
      toast.error("Invalid email or password.");
    } finally {
      setSubmitting(false);
    }
  };

  const input = "w-full border border-stone/40 px-4 py-3 text-sm focus:outline-none focus:border-gold-dark";

  return (
    <div className="max-w-md mx-auto px-5 py-24">
      <h1 className="font-display text-3xl mb-8 text-center">Sign In</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input required type="email" placeholder="Email" className={input} value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input required type="password" placeholder="Password" className={input} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button type="submit" disabled={submitting} className="btn btn-primary w-full">
          {submitting ? "Signing in…" : "Sign In"}
        </button>
      </form>
      <p className="text-sm text-center mt-4">
        <Link to="/forgot-password" className="text-stone hover:text-gold-dark underline">
          Forgot your password?
        </Link>
      </p>
      <p className="text-sm text-stone text-center mt-6">
        New here? <Link to="/register" className="text-gold-dark hover:underline">Create an account</Link>
      </p>
    </div>
  );
}
