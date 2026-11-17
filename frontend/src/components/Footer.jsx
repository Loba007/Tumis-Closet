import { Link } from "react-router-dom";
import logo from "../assets/logo.jpg";
import GoldFlourish from "./GoldFlourish";

export default function Footer() {
  return (
    <footer className="bg-ink text-porcelain mt-28">
      <div className="max-w-7xl mx-auto px-5 md:px-8 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-12">
          <div>
            <img
              src={logo}
              alt="Tunmis Closet"
              className="h-14 w-14 object-contain rounded-full bg-porcelain p-1 border border-gold-dark/70 mb-5"
            />
            <p className="font-display italic text-base text-gold-light mb-3">Fashion is the Language</p>
            <p className="text-sm text-stone max-w-xs leading-relaxed">
              Considered pieces from our Lagos studio, designed to be worn,
              not just looked at.
            </p>
          </div>
          <div>
            <p className="label-track text-xs text-porcelain/70 mb-5">Explore</p>
            <ul className="space-y-3 text-sm text-stone">
              <li><Link to="/shop" className="hover:text-gold-light transition-colors">Shop</Link></li>
              <li><Link to="/portfolio" className="hover:text-gold-light transition-colors">Portfolio</Link></li>
              <li><Link to="/size-guide" className="hover:text-gold-light transition-colors">Size Guide</Link></li>
              <li><Link to="/faq" className="hover:text-gold-light transition-colors">FAQ</Link></li>
              <li><Link to="/contact" className="hover:text-gold-light transition-colors">Contact</Link></li>
            </ul>
          </div>
          <div>
            <p className="label-track text-xs text-porcelain/70 mb-5">Account</p>
            <ul className="space-y-3 text-sm text-stone">
              <li><Link to="/account" className="hover:text-gold-light transition-colors">My Account</Link></li>
              <li><Link to="/orders" className="hover:text-gold-light transition-colors">My Orders</Link></li>
              <li><Link to="/wishlist" className="hover:text-gold-light transition-colors">Wishlist</Link></li>
              <li><Link to="/login" className="hover:text-gold-light transition-colors">Sign In</Link></li>
              <li><Link to="/register" className="hover:text-gold-light transition-colors">Create Account</Link></li>
            </ul>
          </div>
          <div>
            <p className="label-track text-xs text-porcelain/70 mb-5">Help</p>
            <ul className="space-y-3 text-sm text-stone">
              <li><Link to="/returns" className="hover:text-gold-light transition-colors">Returns & Exchanges</Link></li>
              <li><Link to="/terms" className="hover:text-gold-light transition-colors">Terms of Service</Link></li>
              <li><Link to="/privacy" className="hover:text-gold-light transition-colors">Privacy Policy</Link></li>
              <li>
                <a href="https://wa.me/2348184720215" target="_blank" rel="noopener noreferrer" className="hover:text-gold-light transition-colors">
                  WhatsApp Us
                </a>
              </li>
            </ul>
          </div>
        </div>
        <GoldFlourish className="text-ink-line my-10" />
        <p className="text-xs text-stone">© {new Date().getFullYear()} Tunmis Closet. All rights reserved.</p>
      </div>
    </footer>
  );
}
