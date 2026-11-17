import GoldFlourish from "../components/GoldFlourish";
import usePageMeta from "../hooks/usePageMeta";

const faqs = [
  {
    q: "Do you deliver outside Lagos?",
    a: "Yes! We deliver to all 36 states in Nigeria. Delivery within Lagos takes 1–3 business days, while inter-state delivery (Abuja, PH, Ibadan, Kano, etc.) takes 3–7 business days depending on your location. We use trusted courier partners.",
  },
  {
    q: "How much is delivery?",
    a: "Delivery within Lagos (Lekki, VI, Ikoyi, Ikeja, Surulere, Yaba) is ₦2,500. Other Lagos zones are ₦3,500. Inter-state delivery starts at ₦5,000 depending on distance. You'll see the exact fee at checkout. Studio pickup in Igbogbo, Ikorodu is always free.",
  },
  {
    q: "Can I pick up from your studio?",
    a: "Absolutely. Our studio is in Igbogbo, Ikorodu, Lagos. Select 'Studio Pickup' at checkout and we'll confirm a time within 24 hours. Same-day pickup is available for in-stock items if you order before 12pm.",
  },
  {
    q: "How long does it take to get my order?",
    a: "Ready-to-wear pieces ship within 3–5 business days. Made-to-order pieces typically take 10–14 business days. You'll see the estimated timeline on each product page before you add to bag.",
  },
  {
    q: "Do you do bespoke/tailoring?",
    a: "Yes! We take custom orders for individual clients. Send a message on WhatsApp or email us with your style reference, measurements, and fabric preference. Lead time is 2–4 weeks depending on complexity.",
  },
  {
    q: "What payment methods do you accept?",
    a: "Online checkout is securely handled by Paystack (card, bank transfer, and USSD). Contact the studio on WhatsApp before ordering if you need a special payment arrangement.",
  },
  {
    q: "Can I return or exchange?",
    a: "We accept returns within 7 days of delivery for unworn, unwashed items with tags intact. Custom/bespoke pieces are final sale. For exchanges, contact us on WhatsApp and we'll process size swaps subject to availability.",
  },
  {
    q: "Do you have a physical store?",
    a: "Our primary studio is in Igbogbo, Ikorodu, Lagos. We also pop up at selected events and markets — follow us on Instagram @tunmiscloset for pop-up announcements.",
  },
  {
    q: "How do I know my size?",
    a: "Check our Size Guide page for detailed measurements in inches and cm. If you're between sizes or unsure, chat with us on WhatsApp — we're happy to help you pick the right fit.",
  },
  {
    q: "What fabrics do you use?",
    a: "We work with a range of high-quality fabrics including Ankara (African wax print), Aso Oke (handwoven Yoruba textile), Adire (tie-dye), lace, Guinea brocade, silk, and cotton. Each product page lists the fabric composition.",
  },
];

export default function FAQ() {
  usePageMeta({
    title: "FAQ",
    description: "Delivery, payment, sizing, returns, and bespoke order questions answered by Tunmis Closet.",
  });

  return (
    <div className="max-w-3xl mx-auto px-5 md:px-8 py-14">
      <div className="text-center mb-12">
        <p className="label-track text-xs text-gold-dark mb-2">You Ask, We Answer</p>
        <h1 className="font-display text-4xl mb-4">Frequently Asked Questions</h1>
        <p className="text-stone max-w-md mx-auto">
          Everything you need to know about ordering from Tunmis Closet —{" "}
          <em className="text-gold-dark">if we missed anything, just WhatsApp us!</em>
        </p>
      </div>

      <GoldFlourish className="text-stone mb-10" />

      <div className="space-y-6">
        {faqs.map((faq, i) => (
          <details key={i} className="group border border-stone/20 open:border-gold-dark/40 transition-colors">
            <summary className="flex items-center justify-between px-6 py-5 cursor-pointer list-none text-sm font-medium hover:text-gold-dark transition-colors">
              {faq.q}
              <span className="shrink-0 ml-4 text-gold-dark group-open:rotate-45 transition-transform text-lg leading-none">+</span>
            </summary>
            <div className="px-6 pb-5 text-sm text-stone leading-relaxed">
              {faq.a}
            </div>
          </details>
        ))}
      </div>

      <div className="mt-16 text-center border border-stone/20 p-8">
        <p className="font-display text-xl mb-2">Still no answer?</p>
        <p className="text-stone text-sm mb-5">
          Abeg, just send us a message on WhatsApp — we reply fast!
        </p>
        <a
          href="https://wa.me/2348184720215?text=Hi%20Tunmis%20Closet!%20I%20have%20a%20question%20about..."
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          Chat on WhatsApp
        </a>
      </div>
    </div>
  );
}
