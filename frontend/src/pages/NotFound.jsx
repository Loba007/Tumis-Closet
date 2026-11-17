import { Link } from "react-router-dom";

import usePageMeta from "../hooks/usePageMeta";

export default function NotFound() {
  usePageMeta({ title: "Page Not Found", noIndex: true });

  return (
    <div className="max-w-md mx-auto px-5 py-32 text-center">
      <p className="label-track text-xs text-gold-dark mb-4">404</p>
      <h1 className="font-display text-3xl mb-6">Page Not Found</h1>
      <Link to="/" className="btn btn-primary">
        Back Home
      </Link>
    </div>
  );
}
