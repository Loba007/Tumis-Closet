import { useState } from "react";
import toast from "react-hot-toast";
import GoldFlourish from "../components/GoldFlourish";
import usePageMeta from "../hooks/usePageMeta";
import { sendContactMessage } from "../api/contact";

const initialForm = { name: "", email: "", subject: "", message: "" };
const addressQuery = "44 Yusuf Street, Selewu, Igbogbo, Ikorodu, Lagos, Nigeria";

export default function Contact() {
  const [form, setForm] = useState(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  usePageMeta({
    title: "Contact",
    description: "Message the Tunmis Closet studio in Lagos about bespoke orders, sizing, or an existing order.",
  });

  const update = (field) => (event) => setForm({ ...form, [field]: event.target.value });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await sendContactMessage(form);
      setSent(true);
      setForm(initialForm);
      toast.success("Message sent — we will reply shortly.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(detail || "Could not send your message. Please try WhatsApp or email.");
    } finally {
      setSubmitting(false);
    }
  };

  const input =
    "w-full border border-stone/40 px-4 py-3 text-sm focus:outline-none focus:border-gold-dark";

  return (
    <div className="max-w-5xl mx-auto px-5 md:px-8 py-14">
      <div className="text-center mb-12">
        <p className="label-track text-xs text-gold-dark mb-2">Get in Touch</p>
        <h1 className="font-display text-4xl mb-4">Contact Us</h1>
        <p className="text-stone max-w-md mx-auto">
          We&rsquo;d love to hear from you — whether it&rsquo;s a custom order enquiry,
          a question about a piece, or just to say hello.
        </p>
      </div>

      <GoldFlourish className="text-stone mb-12" />

      <div className="grid md:grid-cols-2 gap-12">
        <div className="space-y-8">
          <div>
            <p className="label-track text-xs text-gold-dark mb-2">Studio Address</p>
            <p className="text-sm leading-relaxed text-stone">
              44 Yusuf Street, Selewu,<br />
              Igbogbo, Ikorodu, Lagos,<br />
              Nigeria.
            </p>
          </div>

          <div>
            <p className="label-track text-xs text-gold-dark mb-2">Phone / WhatsApp</p>
            <a
              href="https://wa.me/2348184720215"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-ink hover:text-gold-dark transition-colors"
            >
              +234 818 472 0215
            </a>
          </div>

          <div>
            <p className="label-track text-xs text-gold-dark mb-2">Email</p>
            <a
              href="mailto:hello@tunmiscloset.com"
              className="text-sm text-ink hover:text-gold-dark transition-colors"
            >
              hello@tunmiscloset.com
            </a>
          </div>

          <div>
            <p className="label-track text-xs text-gold-dark mb-2">Social</p>
            <div className="flex gap-4">
              <a
                href="https://instagram.com/tunmiscloset"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-ink hover:text-gold-dark transition-colors"
              >
                Instagram
              </a>
              <a
                href="https://tiktok.com/@tunmiscloset"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-ink hover:text-gold-dark transition-colors"
              >
                TikTok
              </a>
            </div>
          </div>

          <div>
            <p className="label-track text-xs text-gold-dark mb-2">Studio Hours</p>
            <p className="text-sm leading-relaxed text-stone">
              Monday – Friday: 10am – 6pm<br />
              Saturday: 11am – 4pm<br />
              Sunday: By appointment only
            </p>
          </div>
        </div>

        <div className="border border-stone/20 p-8">
          <p className="font-display text-xl mb-6">Send an Enquiry</p>
          {sent ? (
            <div>
              <p className="text-sm text-stone mb-6">
                Thank you — your message is with the studio. We usually reply within one business day.
              </p>
              <button onClick={() => setSent(false)} className="btn btn-outline">Send another</button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <label className="sr-only" htmlFor="contact-name">Your name</label>
                <input
                  id="contact-name"
                  required
                  type="text"
                  placeholder="Your name"
                  value={form.name}
                  onChange={update("name")}
                  className={input}
                />
                <label className="sr-only" htmlFor="contact-email">Email address</label>
                <input
                  id="contact-email"
                  required
                  type="email"
                  placeholder="Email address"
                  value={form.email}
                  onChange={update("email")}
                  className={input}
                />
              </div>
              <label className="sr-only" htmlFor="contact-subject">Subject</label>
              <input
                id="contact-subject"
                type="text"
                placeholder="Subject"
                value={form.subject}
                onChange={update("subject")}
                className={input}
              />
              <label className="sr-only" htmlFor="contact-message">Message</label>
              <textarea
                id="contact-message"
                required
                rows={5}
                placeholder="Tell us what you need — custom order, sizing help, general enquiry..."
                value={form.message}
                onChange={update("message")}
                className={input}
              />
              <button type="submit" disabled={submitting} className="btn btn-primary w-full">
                {submitting ? "Sending…" : "Send Message"}
              </button>
              <p className="text-xs text-stone text-center mt-2">
                Prefer a faster reply?{" "}
                <a
                  href="https://wa.me/2348184720215"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gold-dark underline"
                >
                  Chat on WhatsApp
                </a>
              </p>
            </form>
          )}
        </div>
      </div>

      <div className="mt-16">
        <p className="label-track text-xs text-gold-dark mb-3">Find Us</p>
        <div className="border border-stone/20 overflow-hidden">
          <iframe
            title="Tunmis Closet studio location"
            src={`https://www.google.com/maps?q=${encodeURIComponent(addressQuery)}&output=embed`}
            className="w-full h-72 border-0"
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        </div>
        <a
          href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(addressQuery)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block text-xs text-gold-dark underline mt-3"
        >
          Open in Google Maps
        </a>
      </div>
    </div>
  );
}
