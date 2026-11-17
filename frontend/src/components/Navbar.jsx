import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Heart, LogOut, Menu, ShoppingBag, User, X } from "lucide-react";
import logo from "../assets/logo.jpg";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

const links = [
  { to: "/shop", label: "Shop" },
  { to: "/portfolio", label: "Portfolio" },
  { to: "/about", label: "About" },
  { to: "/faq", label: "FAQ" },
  { to: "/contact", label: "Contact" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const { cart } = useCart() || {};

  return (
    <header className="sticky top-0 z-50 bg-ink text-porcelain border-b border-ink-line">
      <div className="max-w-7xl mx-auto px-5 md:px-8 flex items-center justify-between h-24">
        <Link to="/" className="flex items-center gap-4 shrink-0">
          <img
            src={logo}
            alt="Tunmis Closet"
            className="h-11 w-11 object-contain rounded-full bg-porcelain p-1 border border-gold-dark/70"
          />
          <span className="hidden sm:block font-display italic text-lg text-gold-light tracking-wide">
            Fashion is the Language
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-12 label-track text-xs">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `pb-1 border-b transition-colors ${
                  isActive
                    ? "text-gold-light border-gold-light"
                    : "text-porcelain border-transparent hover:text-gold-light hover:border-gold-dark"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-5">
          <Link to="/wishlist" aria-label="Wishlist" className="hover:text-gold-light transition-colors">
            <Heart size={19} />
          </Link>
          <Link to="/cart" aria-label="Cart" className="relative hover:text-gold-light transition-colors">
            <ShoppingBag size={19} />
            {cart?.item_count > 0 && (
              <span className="absolute -top-2 -right-2 bg-gold text-ink text-[10px] font-medium rounded-full w-4 h-4 flex items-center justify-center">
                {cart.item_count}
              </span>
            )}
          </Link>
          {user ? (
            <>
              <Link to="/account" aria-label="My account" className="hover:text-gold-light transition-colors">
                <User size={19} />
              </Link>
              <button onClick={logout} aria-label="Log out" className="hidden sm:block hover:text-gold-light transition-colors">
                <LogOut size={19} />
              </button>
            </>
          ) : (
            <Link to="/login" aria-label="Log in" className="hover:text-gold-light transition-colors">
              <User size={19} />
            </Link>
          )}
          <button className="md:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu">
            {open ? <X size={21} /> : <Menu size={21} />}
          </button>
        </div>
      </div>

      {open && (
        <nav className="md:hidden border-t border-ink-line px-5 py-5 flex flex-col gap-5 label-track text-xs">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className="hover:text-gold-light">
              {l.label}
            </NavLink>
          ))}
          <NavLink to="/size-guide" onClick={() => setOpen(false)} className="hover:text-gold-light">
            Size Guide
          </NavLink>
          {user ? (
            <>
              <NavLink to="/account" onClick={() => setOpen(false)} className="hover:text-gold-light">
                My Account
              </NavLink>
              <NavLink to="/orders" onClick={() => setOpen(false)} className="hover:text-gold-light">
                My Orders
              </NavLink>
              <button
                onClick={() => {
                  setOpen(false);
                  logout();
                }}
                className="text-left hover:text-gold-light"
              >
                Log Out
              </button>
            </>
          ) : (
            <NavLink to="/login" onClick={() => setOpen(false)} className="hover:text-gold-light">
              Sign In
            </NavLink>
          )}
        </nav>
      )}
    </header>
  );
}
