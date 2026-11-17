import GoldFlourish from "../components/GoldFlourish";
import usePageMeta from "../hooks/usePageMeta";

const rows = [
  ["XS", "31–32", "24–25", "34–35", "79–81", "61–64", "86–89"],
  ["S", "33–34", "26–27", "36–37", "84–86", "66–69", "91–94"],
  ["M", "35–36", "28–29", "38–39", "89–91", "71–74", "97–99"],
  ["L", "37–39", "30–32", "40–42", "94–99", "76–81", "102–107"],
  ["XL", "40–42", "33–35", "43–45", "102–107", "84–89", "109–114"],
  ["XXL", "43–45", "36–38", "46–48", "109–114", "91–97", "117–122"],
];

export default function SizeGuide() {
  usePageMeta({
    title: "Size Guide",
    description: "Measurements in inches and centimetres to help you choose the right Tunmis Closet fit.",
  });

  return (
    <div className="max-w-4xl mx-auto px-5 md:px-8 py-14">
      <div className="text-center mb-10">
        <p className="label-track text-xs text-gold-dark mb-2">Find Your Fit</p>
        <h1 className="font-display text-4xl mb-4">Size Guide</h1>
        <p className="text-stone text-sm max-w-lg mx-auto">
          Measure against your body, not over clothing. If you are between sizes, size up
          or message us on WhatsApp — we will help you choose.
        </p>
      </div>
      <GoldFlourish className="text-stone mb-10" />

      <div className="overflow-x-auto border border-stone/20">
        <table className="w-full text-sm">
          <thead className="bg-porcelain-deep label-track text-[10px] text-stone">
            <tr>
              <th className="px-4 py-3 text-left">Size</th>
              <th className="px-4 py-3 text-left">Bust (in)</th>
              <th className="px-4 py-3 text-left">Waist (in)</th>
              <th className="px-4 py-3 text-left">Hips (in)</th>
              <th className="px-4 py-3 text-left">Bust (cm)</th>
              <th className="px-4 py-3 text-left">Waist (cm)</th>
              <th className="px-4 py-3 text-left">Hips (cm)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row[0]} className="border-t border-stone/15">
                {row.map((cell, i) => (
                  <td key={i} className={`px-4 py-3 ${i === 0 ? "font-medium" : "text-stone"}`}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-10 text-sm text-stone space-y-3">
        <p><strong className="text-ink">Bespoke pieces:</strong> send your measurements on WhatsApp after ordering and we will tailor to you.</p>
        <p><strong className="text-ink">Still unsure?</strong> Message +234 818 472 0215 or email hello@tunmiscloset.com.</p>
      </div>
    </div>
  );
}
