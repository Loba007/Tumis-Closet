import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { confirmPasswordReset } from "../api/auth";
import usePageMeta from "../hooks/usePageMeta";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const uid = searchParams.get("uid") || "";
  const token = searchParams.get("token") || "";
  const [form, setForm] = useState({ new_password: "", confirm: "" });
  const [submitting, setSubmitting] = useState(false);
  usePageMeta({ title: "Choose New Password", noIndex: true });

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (form.new_password !== form.confirm) {
      toast.error("The passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await confirmPasswordReset({ uid, token, new_password: form.new_password });
      toast.success("Password updated. You can now sign in.");
      navigate("/login", { replace: true });
    } catch (err) {
      const data = err.response?.data;
      toast.error(data ? Object.values(data).flat().join(" ") : "Could not reset the password.");
    } finally {
      setSubmitting(false);
    }
  };

  const input =
    "w-full border border-stone/40 px-4 py-3 text-sm focus:outline-none focus:border-gold-dark";

  if (!uid || !token) {
    return (
      <div className="max-w-md mx-auto px-5 py-24 text-center">
        <h1 className="font-display text-3xl mb-4">Invalid Reset Link</h1>
        <p className="text-sm text-stone mb-8">
          This password reset link is incomplete or has expired.
        </p>
        <Link to="/forgot-password" className="btn btn-primary">Request a New Link</Link>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-5 py-24">
      <h1 className="font-display text-3xl mb-8 text-center">Choose a New Password</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          required
          type="password"
          placeholder="New password"
          className={input}
          value={form.new_password}
          onChange={(event) => setForm({ ...form, new_password: event.target.value })}
        />
        <input
          required
          type="password"
          placeholder="Confirm new password"
          className={input}
          value={form.confirm}
          onChange={(event) => setForm({ ...form, confirm: event.target.value })}
        />
        <button type="submit" disabled={submitting} className="btn btn-primary w-full">
          {submitting ? "Updating…" : "Update Password"}
        </button>
      </form>
    </div>
  );
}
