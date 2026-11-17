import usePageMeta from "../hooks/usePageMeta";

const policies = {
  terms: {
    title: "Terms of Service",
    intro: "By placing an order with Tunmis Closet you agree to the terms below.",
    sections: [
      ["Orders", "Orders are confirmed once payment is received. We may cancel and refund an order if a piece is unavailable or a price was listed in error."],
      ["Pricing", "All prices are in Nigerian Naira (NGN). Shipping is calculated at checkout based on your delivery location or studio pickup."],
      ["Bespoke work", "Made-to-order and bespoke pieces are produced to the measurements and details confirmed with you. Please review sizing carefully before checkout."],
      ["Contact", "Questions about these terms can be sent to hello@tunmiscloset.com or +234 818 472 0215."],
    ],
  },
  privacy: {
    title: "Privacy Policy",
    intro: "We collect only what we need to process your order and support you.",
    sections: [
      ["What we collect", "Account details (name, email, phone), delivery addresses, order history, and payment confirmations. Card details are handled by Paystack and never stored on our servers."],
      ["How we use it", "To process orders, arrange delivery, provide support, send order updates, and prevent fraud. We do not sell your personal data."],
      ["Your choices", "You may request access, correction, or deletion of your account data by emailing hello@tunmiscloset.com."],
      ["Security", "Access tokens are used for sign-in and payment data is transmitted over encrypted connections in production."],
    ],
  },
  returns: {
    title: "Returns & Exchanges",
    intro: "We want you to love your piece. Here is how returns work.",
    sections: [
      ["Ready-to-wear", "Unworn, unwashed items with tags intact may be returned within 7 days of delivery. Contact us first for a return authorisation."],
      ["Exchanges", "Size exchanges are subject to availability. Any price difference and return shipping are handled case by case."],
      ["Bespoke and made-to-order", "Custom pieces are final sale unless they arrive damaged or materially different from what was agreed."],
      ["Refunds", "Approved refunds are returned to the original payment method within 5–10 business days after we receive the item."],
    ],
  },
};

export default function PolicyPage({ kind }) {
  const policy = policies[kind] || policies.terms;
  usePageMeta({ title: policy.title, description: policy.intro });

  return (
    <div className="max-w-3xl mx-auto px-5 md:px-8 py-14">
      <p className="label-track text-xs text-gold-dark mb-2">Tunmis Closet</p>
      <h1 className="font-display text-4xl mb-4">{policy.title}</h1>
      <p className="text-stone mb-10">{policy.intro}</p>
      <div className="space-y-8">
        {policy.sections.map(([heading, body]) => (
          <section key={heading}>
            <h2 className="font-display text-2xl mb-2">{heading}</h2>
            <p className="text-sm text-stone leading-relaxed">{body}</p>
          </section>
        ))}
      </div>
    </div>
  );
}
