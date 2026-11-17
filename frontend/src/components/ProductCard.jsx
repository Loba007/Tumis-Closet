import { useState } from "react";
import { Link } from "react-router-dom";
import { Heart, Star } from "lucide-react";

export default function ProductCard({ product, onWishlist, wishlistActionLabel }) {
  const [imageFailed, setImageFailed] = useState(false);
  const price = Number(product.current_price ?? product.price).toLocaleString("en-NG", {
    style: "currency",
    currency: "NGN",
    maximumFractionDigits: 0,
  });

  return (
    <div className="group">
      <Link to={`/product/${product.slug}`} className="block relative aspect-[3/4] bg-porcelain-deep overflow-hidden">
        {product.primary_image && !imageFailed ? (
          <img
            src={product.primary_image}
            alt={product.name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
            decoding="async"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-stone label-track text-xs">
            No Image
          </div>
        )}
        {!product.is_portfolio_only && !product.in_stock && (
          <span className="absolute top-3 left-3 bg-ink/85 text-porcelain text-[10px] label-track px-2 py-1">
            Sold Out
          </span>
        )}
        {onWishlist && (
          <button
            onClick={(e) => {
              e.preventDefault();
              onWishlist(product);
            }}
            className="absolute top-3 right-3 bg-porcelain/90 rounded-full p-2 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity"
            aria-label={wishlistActionLabel || `Add ${product.name} to wishlist`}
          >
            <Heart size={16} />
          </button>
        )}
      </Link>
      <div className="mt-3">
        <p className="text-xs label-track text-stone">{product.category_name}</p>
        <Link to={`/product/${product.slug}`} className="font-display font-medium text-lg hover:text-gold-dark transition-colors">
          {product.name}
        </Link>
        {product.is_portfolio_only ? (
          <p className="text-xs label-track text-stone mt-1">Portfolio Piece</p>
        ) : (
          <div className="flex items-center justify-between mt-1 gap-2">
            <p className="text-sm">{price}</p>
            {Number(product.average_rating) > 0 && (
              <span className="inline-flex items-center gap-1 text-xs text-stone">
                <Star size={12} className="text-gold fill-gold" />
                {Number(product.average_rating).toFixed(1)}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
