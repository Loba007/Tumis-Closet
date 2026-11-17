import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, Clock, XCircle } from "lucide-react";
import { fetchMe, verifyEmail } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import usePageMeta from "../hooks/usePageMeta";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const { setUser } = useAuth();
  const [status, setStatus] = useState("loading");
  const uid = searchParams.get("uid") || "";
  const token = searchParams.get("token") || "";
  const started = useRef(false);
  usePageMeta({ title: "Verify Email", noIndex: true });

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    if (!uid || !token) {
      setStatus("invalid");
      return;
    }

    verifyEmail({ uid, token })
      .then(() => {
        setStatus("success");
        if (localStorage.getItem("tc_access")) {
          fetchMe().then(setUser).catch(() => {});
        }
      })
      .catch(() => setStatus("invalid"));
  }, [uid, token, setUser]);

  return (
    <div className="max-w-md mx-auto px-5 py-24 text-center">
      {status === "loading" && (
        <>
          <Clock size={36} className="mx-auto text-gold-dark mb-5" />
          <h1 className="font-display text-3xl mb-4">Verifying Your Email</h1>
          <p className="text-sm text-stone">This will only take a moment.</p>
        </>
      )}

      {status === "success" && (
        <>
          <CheckCircle2 size={36} className="mx-auto text-green-700 mb-5" />
          <h1 className="font-display text-3xl mb-4">Email Verified</h1>
          <p className="text-sm text-stone mb-8">
            Your email address is confirmed. You can now check out and receive order updates.
          </p>
          <Link to="/account" className="btn btn-primary">Go to My Account</Link>
        </>
      )}

      {status === "invalid" && (
        <>
          <XCircle size={36} className="mx-auto text-red-700 mb-5" />
          <h1 className="font-display text-3xl mb-4">Link Invalid or Expired</h1>
          <p className="text-sm text-stone mb-8">
            Sign in to your account and request a new verification email.
          </p>
          <Link to="/account" className="btn btn-primary">Go to My Account</Link>
        </>
      )}
    </div>
  );
}
