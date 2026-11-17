import { useEffect, useState } from "react";
import { listPortfolio, listProducts } from "../api/products";

const fallbackTiles = ["New drops", "Behind the seams", "Studio days", "Styling notes"];

function InstagramIcon({ className = "" }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      className={className}
      aria-hidden="true"
    >
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

function GalleryTile({ product, featured, username }) {
  const [failed, setFailed] = useState(false);

  return (
    <a
      href={`https://instagram.com/${username}`}
      target="_blank"
      rel="noopener noreferrer"
      className={`group relative block overflow-hidden bg-ink-soft ${
        featured
          ? "col-span-2 aspect-[4/3] md:col-span-2 md:row-span-2 md:aspect-auto"
          : "aspect-square"
      }`}
    >
      {product.primary_image && !failed ? (
        <img
          src={product.primary_image}
          alt={product.name}
          loading="lazy"
          decoding="async"
          onError={() => setFailed(true)}
          className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-ink-soft via-ink to-ink-soft">
          <InstagramIcon className="h-9 w-9 text-gold-dark/60" />
        </div>
      )}
      <div className="absolute inset-0 bg-gradient-to-t from-ink/90 via-ink/20 to-transparent opacity-80 transition-opacity duration-300 group-hover:opacity-95" />
      <div className="absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-full border border-porcelain/20 bg-ink/35 text-porcelain/80 backdrop-blur-sm transition-colors group-hover:border-gold-light group-hover:text-gold-light">
        <InstagramIcon className="h-4 w-4" />
      </div>
      <div className="absolute inset-x-0 bottom-0 p-4 md:p-5">
        <p className="label-track text-[10px] text-gold-light">
          {product.is_portfolio_only ? "Portfolio piece" : "Shop the look"}
        </p>
        <p className="font-display text-lg leading-tight text-porcelain md:text-xl">
          {product.name}
        </p>
      </div>
    </a>
  );
}

export default function InstagramFeed({ username = "tunmiscloset" }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.allSettled([listPortfolio(), listProducts()])
      .then((results) => {
        if (!active) return;
        const merged = results.flatMap((result) =>
          result.status === "fulfilled"
            ? result.value.results || result.value || []
            : []
        );
        setProducts(merged);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const images = products
    .filter((product) => product?.primary_image)
    .filter(
      (product, index, list) =>
        list.findIndex(
          (item) =>
            item.id === product.id ||
            item.primary_image === product.primary_image
        ) === index
    )
    .slice(0, 6);
  const featureFirst = images.length >= 5;
  const columns = images.length === 5 ? "md:grid-cols-4" : "md:grid-cols-3";

  return (
    <section className="relative overflow-hidden bg-ink py-24 text-porcelain">
      <div className="pointer-events-none absolute -right-24 -top-32 h-96 w-96 rounded-full bg-gold/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 -left-24 h-96 w-96 rounded-full bg-gold-dark/10 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-5 md:px-8">
        <div className="mb-12 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="label-track mb-3 text-xs text-gold-light">@{username}</p>
            <h2 className="font-display text-4xl leading-tight md:text-5xl">
              From the studio, <em className="text-gold-light">in motion.</em>
            </h2>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-stone">
              Recent pieces, studio days and the details behind the cloth — a little
              more of what you see on our Instagram.
            </p>
          </div>
          <a
            href={`https://instagram.com/${username}`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline-light shrink-0"
          >
            Follow on Instagram
          </a>
        </div>

        {loading && images.length === 0 ? (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4">
            {Array.from({ length: 6 }).map((_, index) => (
              <div
                key={index}
                className={`animate-pulse bg-ink-soft ${
                  index === 0
                    ? "col-span-2 aspect-[4/3] md:col-span-2 md:row-span-2 md:aspect-auto"
                    : "aspect-square"
                }`}
              />
            ))}
          </div>
        ) : images.length > 0 ? (
          <div className={`grid grid-cols-2 gap-3 md:gap-4 ${columns}`}>
            {images.map((product, index) => (
              <GalleryTile
                key={product.id}
                product={product}
                username={username}
                featured={featureFirst && index === 0}
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
            {fallbackTiles.map((label) => (
              <a
                key={label}
                href={`https://instagram.com/${username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="group relative flex aspect-square items-center justify-center overflow-hidden border border-porcelain/10 bg-gradient-to-br from-ink-soft via-ink to-ink-soft text-center"
              >
                <div className="absolute inset-0 bg-gold/0 transition-colors duration-300 group-hover:bg-gold/10" />
                <div className="relative px-4">
                  <InstagramIcon className="mx-auto mb-3 h-7 w-7 text-gold-dark transition-colors group-hover:text-gold-light" />
                  <p className="label-track text-[10px] text-stone transition-colors group-hover:text-porcelain">
                    {label}
                  </p>
                </div>
              </a>
            ))}
          </div>
        )}

        <div className="mt-10 flex flex-col items-start justify-between gap-4 border-t border-porcelain/10 pt-8 sm:flex-row sm:items-center">
          <p className="max-w-md text-sm leading-relaxed text-stone">
            New drops, behind-the-seams and styling notes — first on Instagram.
          </p>
          <a
            href={`https://instagram.com/${username}`}
            target="_blank"
            rel="noopener noreferrer"
            className="group inline-flex items-center gap-2 label-track text-xs text-gold-light transition-colors hover:text-gold"
          >
            @{username}
            <span className="transition-transform duration-300 group-hover:translate-x-1">
              →
            </span>
          </a>
        </div>
      </div>
    </section>
  );
}
