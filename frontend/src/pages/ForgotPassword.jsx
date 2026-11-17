import { useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { requestPasswordReset } from "../api/auth";
import usePageMeta from "../hooks/usePageMeta";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  usePageMeta({ title: "Reset Password", noIndex: true });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (err) {
      const data = err.response?.data;
      toast.error(data ? Object.values(data).flat().join(" ") : "Could not send the reset link.");
    } finally {
      setSubmitting(false);
    }
  };

  const input =
    "w-full border border-stone/40 px-4 py-3 text-sm focus:outline-none focus:border-gold-dark";

  return (
    <div className="max-w-md mx-auto px-5 py-24">
      <h1 className="font-display text-3xl mb-4 text-center">Reset Password</h1>
      {sent ? (
        <div className="text-center space-y-5">
          <p className="text-sm text-stone">
            If an account exists for {email}, we have sent a password reset link.
            The link expires in one hour.
          </p>
          <Link to="/login" className="btn btn-primary">Back to Sign In</Link>
        </div>
      ) : (
        <>
          <p className="text-sm text-stone text-center mb-8">
            Enter the email address for your account and we will send you a reset link.
          </p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              required
              type="email"
              placeholder="Email"
              className={input}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
            <button type="submit" disabled={submitting} className="btn btn-primary w-full">
              {submitting ? "Sending…" : "Send Reset Link"}
            </button>
          </form>
          <p className="text-sm text-stone text-center mt-6">
            Remembered it? <Link to="/login" className="text-gold-dark hover:underline">Sign in</Link>
          </p>
        </>
      )}
    </div>
  );
}
