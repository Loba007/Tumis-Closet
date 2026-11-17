import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { BadgeCheck, Heart, Share2, Star } from "lucide-react";
import { getProduct } from "../api/products";
import { createReview, listReviews } from "../api/reviews";
import { addToWishlist } from "../api/wishlist";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import GoldFlourish from "../components/GoldFlourish";
import usePageMeta from "../hooks/usePageMeta";

export default function ProductDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const { addItem } = useCart() || {};

  const [product, setProduct] = useState(null);
  const [activeImage, setActiveImage] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [reviews, setReviews] = useState([]);
  const [reviewsError, setReviewsError] = useState(false);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: "" });
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    setError("");
    setNotFound(false);
    setProduct(null);
    setSelectedVariant(null);
    setActiveImage(0);
    setQuantity(1);
    setReviews([]);
    getProduct(slug)
      .then((data) => {
        setProduct(data);
        setSelectedVariant(data.variants?.find((variant) => variant.stock_quantity > 0) || data.variants?.[0] || null);
      })
      .catch((err) => {
        const missing = err.response?.status === 404;
        setNotFound(missing);
        setError(
          missing
            ? "This piece could not be found."
            : "We could not load this piece. Check your connection and try again."
        );
      });
  }, [slug, retryCount]);

  usePageMeta({
    title: product?.name || "Product",
    description: product?.description?.slice(0, 155),
    image: product?.images?.[0]?.image,
    type: "product",
  });

  useEffect(() => {
    if (product) {
      setReviewsError(false);
      listReviews(product.id)
        .then((data) => setReviews(Array.isArray(data) ? data : data?.results ?? []))
        .catch(() => {
          setReviews([]);
          setReviewsError(true);
        });
    }
  }, [product]);

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-5 py-24 text-center">
        <h1 className="font-display text-3xl mb-4">
          {notFound ? "Piece not found" : "Piece unavailable"}
        </h1>
        <p className="text-stone text-sm mb-8">{error}</p>
        {notFound ? (
          <Link to="/shop" className="btn btn-outline">Browse the Shop</Link>
        ) : (
          <button onClick={() => setRetryCount((count) => count + 1)} className="btn btn-outline">
            Try Again
          </button>
        )}
      </div>
    );
  }

  if (!product) return <div className="max-w-7xl mx-auto px-5 py-20 text-stone text-sm">Loading…</div>;

  const price = Number(product.current_price).toLocaleString("en-NG", {
    style: "currency",
    currency: "NGN",
    maximumFractionDigits: 0,
  });
  const selectedStock = selectedVariant?.stock_quantity ?? 0;
  const canAdd = product.in_stock && selectedVariant && selectedStock > 0;

  const handleAddToCart = () => {
    if (!user) return toast.error("Sign in to add items to your bag.");
    if (!selectedVariant) return toast.error("This piece has no sizes set up yet.");
    if (quantity > selectedStock) return toast.error("That is more than the stock we have available.");
    addItem(selectedVariant.id, quantity);
  };

  const handleWishlist = () => {
    if (!user) return toast.error("Sign in to save pieces to your wishlist.");
    addToWishlist(product.id)
      .then(() => toast.success("Saved to wishlist"))
      .catch(() => toast.error("Could not save this piece."));
  };

  const handleReviewSubmit = (e) => {
    e.preventDefault();
    if (!user) return toast.error("Sign in to leave a review.");
    createReview({ product: product.id, ...reviewForm })
      .then((r) => {
        setReviews([r, ...reviews]);
        setReviewForm({ rating: 5, comment: "" });
        getProduct(slug).then(setProduct).catch(() => {});
        toast.success(r.is_approved ? "Review posted" : "Review submitted for approval");
      })
      .catch(() => toast.error("Could not post review — you may have already reviewed this piece."));
  };

  return (
    <div className="max-w-7xl mx-auto px-5 md:px-8 py-14">
      <div className="grid md:grid-cols-2 gap-12">
        {/* Images */}
        <div>
          <div className="aspect-[3/4] bg-porcelain-deep mb-4 overflow-hidden">
            {product.images?.[activeImage] ? (
              <img
                src={product.images[activeImage].image}
                alt={`${product.name}${product.images[activeImage].alt_text ? ` — ${product.images[activeImage].alt_text}` : ""}`}
                className="w-full h-full object-cover"
                fetchPriority="high"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-stone label-track text-xs">No Image</div>
            )}
          </div>
          {product.images?.length > 1 && (
            <div className="flex gap-3 overflow-x-auto pb-1">
              {product.images.map((img, i) => (
                <button key={img.id} onClick={() => setActiveImage(i)} className={`shrink-0 w-16 h-20 bg-porcelain-deep overflow-hidden border ${i === activeImage ? "border-gold" : "border-transparent"}`} aria-label={`View image ${i + 1}`}>
                  <img src={img.image} alt="" className="w-full h-full object-cover" loading="lazy" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Details */}
        <div>
          <p className="label-track text-xs text-gold-dark mb-2">{product.category?.name}</p>
          <h1 className="font-display text-3xl sm:text-4xl mb-3">{product.name}</h1>
          <div className="flex items-center gap-2 mb-4">
            <Star size={16} className="text-gold fill-gold" />
            <span className="text-sm text-stone">
              {product.average_rating ? `${product.average_rating} / 5` : "No ratings yet"}
              {reviews.length ? ` · ${reviews.length} review${reviews.length === 1 ? "" : "s"}` : ""}
            </span>
          </div>
          <p className="text-2xl mb-6">{price}</p>
          <GoldFlourish className="text-stone mb-6" />
          <p className="text-sm text-stone leading-relaxed mb-8 whitespace-pre-line">{product.description}</p>

          {!product.is_portfolio_only && (
            <>
              {product.variants?.length > 0 && (
                <div className="mb-6">
                  <p className="label-track text-xs mb-3">Size</p>
                  <div className="flex gap-2 flex-wrap">
                    {product.variants.map((v) => (
                      <button
                        key={v.id}
                        onClick={() => setSelectedVariant(v)}
                        disabled={v.stock_quantity === 0}
                        className={`px-4 py-2 text-sm border ${
                          selectedVariant?.id === v.id ? "bg-ink text-porcelain border-ink" : "border-stone/40"
                        } ${v.stock_quantity === 0 ? "opacity-30 cursor-not-allowed" : "hover:border-ink"}`}
                      >
                        {v.size}{v.color ? ` / ${v.color}` : ""}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-8">
                <div className="flex items-center justify-between sm:justify-start gap-4">
                  <div className="flex items-center border border-stone/40 shrink-0">
                    <button onClick={() => setQuantity((q) => Math.max(1, q - 1))} className="w-9 h-9" aria-label="Decrease quantity">−</button>
                    <span className="w-10 text-center">{quantity}</span>
                    <button onClick={() => setQuantity((q) => Math.min(selectedStock, q + 1))} disabled={quantity >= selectedStock} className="w-9 h-9 disabled:opacity-30" aria-label="Increase quantity">+</button>
                  </div>
                  <button
                    onClick={handleWishlist}
                    aria-label="Add to wishlist"
                    className="sm:hidden w-11 h-11 border border-stone/40 flex items-center justify-center hover:border-gold shrink-0"
                  >
                    <Heart size={18} />
                  </button>
                </div>
                <button
                  onClick={handleAddToCart}
                  disabled={!canAdd}
                  className="btn btn-primary w-full sm:flex-1"
                >
                  {product.in_stock ? (selectedStock > 0 ? "Add to Bag" : "Select a size") : "Sold Out"}
                </button>
                <button
                  onClick={handleWishlist}
                  aria-label="Add to wishlist"
                  className="hidden sm:flex w-11 h-11 border border-stone/40 items-center justify-center hover:border-gold shrink-0"
                >
                  <Heart size={18} />
                </button>
              </div>
            </>
          )}

          {product.is_portfolio_only && (
            <p className="label-track text-xs text-stone border border-stone/30 px-4 py-3 inline-block">
              Portfolio Piece — Not For Sale
            </p>
          )}

          {/* Share via WhatsApp & Payment methods */}
          <div className="mt-8 space-y-4">
            <a
              href={`https://wa.me/2348184720215?text=${encodeURIComponent(
                `Hi! I'm interested in "${product.name}" at Tunmis Closet. Check it out: ${window.location.origin}/product/${product.slug}`
              )}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-stone hover:text-gold-dark transition-colors"
            >
              <Share2 size={16} />
              Share on WhatsApp
            </a>

            <div className="border-t border-stone/10 pt-4">
              <p className="label-track text-xs text-stone/60 mb-2">We Accept</p>
              <div className="flex items-center gap-4">
                {/* Paystack logo */}
                <svg viewBox="0 0 100 24" className="h-5 text-stone/70" fill="currentColor">
                  <path d="M28.5 5.5h-3.3v12h3.3zm6.6 0h-3.3v12h3.3zm12.1 0H44l-3.3 5.2v6.8h3.3v-5.1l2.2-3.5 2.2 3.5v5.1h3.3v-6.8zm8.8 0h-3.3v12h3.3zm12.2 0H59l-3.3 5.2v6.8H59v-5.1l2.2-3.5 2.2 3.5v5.1h3.3v-6.8zM13.4 5.5C10.8 5.5 8.5 6.8 7 9.1c-1.1 1.7-1.7 3.8-1.7 5.9 0 2.1.6 4.1 1.7 5.9 1.5 2.3 3.8 3.6 6.4 3.6 3.6 0 6.8-2.2 8.1-5.6l-2.9-1.2c-.7 1.8-2.4 2.9-5.2 2.9-2.4 0-4.4-1.2-5.3-3.2h14.3c.1-.5.1-1 .1-1.5 0-2.1-.6-4.1-1.7-5.9-1.5-2.3-3.8-3.6-6.4-3.6zM8.5 13.6c.6-2.1 2.4-3.2 4.9-3.2s4.3 1.1 4.9 3.2z"/>
                </svg>
                <span className="text-xs text-stone/50">|</span>
                <span className="text-xs text-stone/60">Bank Transfer</span>
                <span className="text-xs text-stone/50">|</span>
                <span className="text-xs text-stone/60">USSD</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reviews */}
      <div className="mt-20 max-w-2xl">
        <h2 className="font-display text-2xl mb-6">Reviews</h2>
        {user ? (
          <form onSubmit={handleReviewSubmit} className="mb-10 border border-stone/20 p-6">
            <p className="label-track text-xs mb-3">Your Rating</p>
            <div className="flex gap-1 mb-4">
              {[1, 2, 3, 4, 5].map((n) => (
                <button type="button" key={n} onClick={() => setReviewForm({ ...reviewForm, rating: n })} aria-label={`${n} star${n === 1 ? "" : "s"}`}>
                  <Star size={20} className={n <= reviewForm.rating ? "text-gold fill-gold" : "text-stone/40"} />
                </button>
              ))}
            </div>
            <textarea
              value={reviewForm.comment}
              onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
              placeholder="Share your thoughts on this piece…"
              className="w-full border border-stone/40 p-3 text-sm mb-4 focus:outline-none focus:border-gold-dark"
              rows={3}
            />
            <button type="submit" className="btn btn-primary">
              Submit Review
            </button>
            <p className="text-xs text-stone mt-3">Reviews are checked by the studio before appearing publicly.</p>
          </form>
        ) : (
          <p className="text-sm text-stone mb-10 border border-stone/20 p-6">
            <Link to="/login" className="text-gold-dark underline">Sign in</Link> to leave a review.
          </p>
        )}

        <div className="space-y-6">
          {reviewsError ? (
            <p className="text-stone text-sm">Reviews could not load right now.</p>
          ) : reviews.length === 0 ? (
            <p className="text-stone text-sm">No reviews yet — be the first.</p>
          ) : null}
          {reviews.map((r) => (
            <div key={r.id} className="border-b border-stone/15 pb-5">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={14} className={i < r.rating ? "text-gold fill-gold" : "text-stone/30"} />
                ))}
                <span className="text-sm font-medium ml-2">{r.user_name}</span>
                {r.is_verified_purchase && (
                  <span className="inline-flex items-center gap-1 text-[10px] label-track text-green-700">
                    <BadgeCheck size={13} /> Verified purchase
                  </span>
                )}
                {!r.is_approved && (
                  <span className="text-[10px] label-track text-stone">Pending approval</span>
                )}
              </div>
              <p className="text-sm text-stone">{r.comment}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
