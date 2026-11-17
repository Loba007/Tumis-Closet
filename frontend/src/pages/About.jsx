import GoldFlourish from "../components/GoldFlourish";
import logo from "../assets/logo.jpg";
import usePageMeta from "../hooks/usePageMeta";

export default function About() {
  usePageMeta({
    title: "About",
    description: "Meet Tunmis Closet — a Lagos fashion house working with Nigerian textiles, bespoke tailoring, and ready-to-wear pieces.",
  });

  return (
    <div className="max-w-4xl mx-auto px-5 md:px-8 py-20">
      <div className="flex justify-center mb-10">
        <img src={logo} alt="Tunmis Closet" className="w-28 object-contain rounded-full bg-porcelain-deep p-4 border border-gold-dark/60" />
      </div>
      <h1 className="font-display italic text-4xl text-center mb-6 text-gold-dark">Fashion is the Language</h1>
      <GoldFlourish className="text-stone mb-10 max-w-xs mx-auto" />
      <div className="text-stone leading-relaxed space-y-5 text-sm md:text-base">
        <p>
          Tunmis Closet is a Lagos-based fashion house built on one idea: what you wear
          says something before you do. Every piece is designed to carry that statement —
          considered fabric, deliberate cuts, and finishing that holds up to real, everyday wear.
        </p>
        <p>
          From one-off runway pieces in our portfolio to ready-to-wear drops in the shop,
          the studio works across both — because a wardrobe should hold pieces you love to
          look at and ones you actually live in. Owambe, Sunday service, Detty December,
          or a quiet Thursday in the office — <em className="text-gold-dark">your outfit says it before you do.</em>
        </p>
        <p>
          Based in Ikorodu, Lagos, we work with Nigerian textiles — Ankara, Aso Oke, Adire, lace,
          Guinea brocade — alongside global fabrics, always with the finishing and fit that
          makes a piece unmistakably Tunmis.
        </p>
        <p className="text-gold-dark text-center pt-4 font-medium">
          "No wahala — we fit style you for any occasion." 🇳🇬
        </p>
      </div>
    </div>
  );
}
