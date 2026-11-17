import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listPortfolio, listProducts } from "../api/products";
import ProductCard from "../components/ProductCard";
import GoldFlourish from "../components/GoldFlourish";
import InstagramFeed from "../components/InstagramFeed";
import usePageMeta from "../hooks/usePageMeta";

export default function Home() {
  const [featured, setFeatured] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [featuredLoading, setFeaturedLoading] = useState(true);
  const [portfolioLoading, setPortfolioLoading] = useState(true);
  const [featuredError, setFeaturedError] = useState(false);
  const [portfolioError, setPortfolioError] = useState(false);

  usePageMeta({
    title: "Fashion is the Language",
    description: "Considered, well-made fashion from the Tunmis Closet studio in Ikorodu, Lagos — ready-to-wear and bespoke pieces.",
  });

  useEffect(() => {
    let active = true;
    listProducts({ is_featured: true })
      .then((data) => {
        if (active) setFeatured((data.results || []).slice(0, 4));
      })
      .catch(() => {
        if (active) setFeaturedError(true);
      })
      .finally(() => {
        if (active) setFeaturedLoading(false);
      });
    listPortfolio()
      .then((data) => {
        if (active) setPortfolio((data.results || []).slice(0, 3));
      })
      .catch(() => {
        if (active) setPortfolioError(true);
      })
      .finally(() => {
        if (active) setPortfolioLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div>
      {/* Use the first featured product image until a dedicated campaign image is configured. */}
      <section className="relative bg-ink text-porcelain overflow-hidden min-h-[85vh] flex items-center">
        {featured[0]?.primary_image && (
          <img
            src={featured[0].primary_image}
            alt=""
            aria-hidden="true"
            fetchPriority="high"
            className="absolute inset-0 w-full h-full object-cover opacity-30"
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-br from-ink/90 via-ink/80 to-ink-soft/60" />
        <div className="relative z-10 max-w-4xl mx-auto px-5 md:px-8 py-28 md:py-36 text-center">
          <p className="label-track text-xs text-gold-light mb-8">Tunmis Closet — Igbogbo, Ikorodu, Lagos</p>
          <h1 className="font-display text-5xl sm:text-6xl md:text-7xl leading-[1.08] mb-8">
            Fashion is the <em className="text-gold-light font-medium">language</em>
            <br className="hidden sm:block" /> you speak without saying a word.
          </h1>
          <p className="text-stone max-w-lg mx-auto mb-12 leading-relaxed">
            Considered, well-made pieces from our Lagos studio — built for the runway,
            tailored for everyday wear. Owambe season, Detty December, or a quiet
            Sunday in Ikorodu — we have your look.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/shop" className="btn btn-primary">Shop the Collection</Link>
            <Link to="/portfolio" className="btn btn-outline-light">View Portfolio</Link>
          </div>
          {/* Subtle scroll hint */}
          <p className="text-stone/40 text-xs label-track mt-16 animate-pulse">↓ Scroll to explore</p>
        </div>
      </section>

      {/* Brand values / Owambe-ready banner */}
      <section className="border-y border-stone/10 py-6 bg-porcelain">
        <div className="max-w-7xl mx-auto px-5 md:px-8 flex flex-wrap justify-center gap-x-12 gap-y-3 text-xs label-track text-stone">
          <span className="text-gold-dark">✦ Made in Lagos</span>
          <span className="text-gold-dark">✦ Ready-to-wear & Bespoke</span>
          <span className="text-gold-dark">✦ Delivery across Nigeria</span>
          <span className="text-gold-dark">✦ Secure Paystack Checkout</span>
        </div>
      </section>

      {/* Featured products */}
      <section className="max-w-7xl mx-auto px-5 md:px-8 py-20">
        <div className="flex items-end justify-between mb-10">
          <div>
            <p className="label-track text-xs text-gold-dark mb-2">New In</p>
            <h2 className="font-display text-3xl">Featured Pieces</h2>
          </div>
          <Link to="/shop" className="label-track text-xs hover:text-gold-dark hidden sm:block">
            View All →
          </Link>
        </div>
        {featuredLoading ? (
          <p className="text-stone text-sm">Loading featured pieces…</p>
        ) : featuredError ? (
          <p className="text-stone text-sm">
            Featured pieces could not load. <Link to="/shop" className="underline">Browse the shop</Link>.
          </p>
        ) : featured.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
            {featured.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        ) : (
          <p className="text-stone text-sm">
            No featured pieces yet — mark a product as &ldquo;featured&rdquo; in the admin to show it here.
          </p>
        )}
      </section>

      {/* Owambe / Cultural moment banner */}
      <section className="bg-ink text-porcelain py-16">
        <div className="max-w-3xl mx-auto px-5 md:px-8 text-center">
          <p className="label-track text-xs text-gold-light mb-3">The Occasion Edit</p>
          <h2 className="font-display text-4xl mb-4">Dress for the Moments That Matter</h2>
          <p className="text-stone max-w-lg mx-auto mb-8 leading-relaxed">
            From Aso Ebi to wedding guest, engagement turban to Sunday service —
            explore pieces made for celebrations, gatherings, and the everyday.
          </p>
          <Link to="/shop?category=owambe" className="btn btn-outline-light">Shop Owambe Edit</Link>
        </div>
      </section>

      {/* Portfolio teaser */}
      <section className="bg-porcelain-deep py-20">
        <div className="max-w-7xl mx-auto px-5 md:px-8">
          <GoldFlourish className="mb-10 text-stone" />
          <div className="flex items-end justify-between mb-10">
            <div>
              <p className="label-track text-xs text-gold-dark mb-2">The Gallery</p>
              <h2 className="font-display text-3xl">From the Portfolio</h2>
            </div>
            <Link to="/portfolio" className="label-track text-xs hover:text-gold-dark hidden sm:block">
              See Full Gallery →
            </Link>
          </div>
          {portfolioLoading ? (
            <p className="text-stone text-sm">Loading the gallery…</p>
          ) : portfolioError ? (
            <p className="text-stone text-sm">
              The gallery could not load. <Link to="/portfolio" className="underline">View the portfolio</Link>.
            </p>
          ) : portfolio.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {portfolio.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          ) : (
            <p className="text-stone text-sm">
              Showcase pieces will appear here once added with &ldquo;portfolio only&rdquo; enabled.
            </p>
          )}
        </div>
      </section>

      {/* Instagram feed */}
      <InstagramFeed />

      {/* Trust / FAQ prompt */}
      <section className="max-w-3xl mx-auto px-5 md:px-8 py-20 text-center">
        <h2 className="font-display text-3xl mb-4">Questions? — Abeg ask!</h2>
        <p className="text-stone mb-8 max-w-md mx-auto leading-relaxed">
          Delivery to Abuja? How long does tailoring take? Can I pick up from your
          Ikorodu studio? We answer all of them.
        </p>
        <Link to="/faq" className="btn btn-outline">Read the FAQ</Link>
      </section>
    </div>
  );
}
