import { render, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import usePageMeta from "./usePageMeta";

function Page({ title, description, noIndex }) {
  usePageMeta({ title, description, noIndex });
  return <h1>{title}</h1>;
}

describe("usePageMeta", () => {
  it("sets the document title, description, robots and canonical URL", async () => {
    render(<Page title="Shop" description="Browse the collection" />);

    await waitFor(() => {
      expect(document.title).toBe("Shop — Tunmis Closet");
    });
    expect(
      document.querySelector('meta[name="description"]').getAttribute("content")
    ).toBe("Browse the collection");
    expect(
      document.querySelector('meta[name="robots"]').getAttribute("content")
    ).toBe("index, follow");
    expect(
      document.querySelector('meta[property="og:title"]').getAttribute("content")
    ).toBe("Shop — Tunmis Closet");
    expect(document.querySelector('link[rel="canonical"]')).toHaveAttribute(
      "href",
      expect.stringContaining("/")
    );
  });

  it("marks private pages as noindex", async () => {
    render(<Page title="Orders" noIndex />);

    await waitFor(() => {
      expect(
        document.querySelector('meta[name="robots"]').getAttribute("content")
      ).toBe("noindex, nofollow");
    });
  });
});
