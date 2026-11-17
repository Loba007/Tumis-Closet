/** The brand's signature divider: a thin gold rule, a nod to the
 * crescent swoosh in the Tunmis Closet mark. Use sparingly. */
export default function GoldFlourish({ className = "" }) {
  return (
    <div className={`gold-flourish ${className}`}>
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" className="shrink-0">
        <path
          d="M18 4C14 3 8 5 6 9C4 13 7 18 12 18"
          stroke="currentColor"
          strokeWidth="1.4"
          strokeLinecap="round"
          className="text-gold"
        />
      </svg>
    </div>
  );
}
