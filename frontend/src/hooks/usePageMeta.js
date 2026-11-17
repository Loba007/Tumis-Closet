import { useEffect } from "react";

const DEFAULT_DESCRIPTION =
  "Considered, well-made fashion from Tunmis Closet — ready-to-wear and bespoke pieces from our Lagos studio.";

function setMeta(attribute, key, value) {
  if (!value) return;
  let tag = document.head.querySelector(`meta[${attribute}="${key}"]`);
  if (!tag) {
    tag = document.createElement("meta");
    tag.setAttribute(attribute, key);
    document.head.appendChild(tag);
  }
  tag.setAttribute("content", value);
}

function removeMeta(attribute, key) {
  const tag = document.head.querySelector(`meta[${attribute}="${key}"]`);
  if (tag) tag.remove();
}

function setCanonical(url) {
  let tag = document.head.querySelector('link[rel="canonical"]');
  if (!tag) {
    tag = document.createElement("link");
    tag.setAttribute("rel", "canonical");
    document.head.appendChild(tag);
  }
  tag.setAttribute("href", url);
}

export default function usePageMeta({ title, description, image, type = "website", noIndex = false }) {
  useEffect(() => {
    const fullTitle = title ? `${title} — Tunmis Closet` : "Tunmis Closet — Fashion is the Language";
    const desc = description || DEFAULT_DESCRIPTION;
    const canonicalUrl = `${window.location.origin}${window.location.pathname}`;
    document.title = fullTitle;
    setMeta("name", "description", desc);
    setMeta("name", "robots", noIndex ? "noindex, nofollow" : "index, follow");
    setMeta("property", "og:title", fullTitle);
    setMeta("property", "og:description", desc);
    setMeta("property", "og:type", type);
    setMeta("property", "og:url", canonicalUrl);
    setCanonical(canonicalUrl);
    if (image) {
      setMeta("property", "og:image", image);
      setMeta("name", "twitter:image", image);
    } else {
      removeMeta("property", "og:image");
      removeMeta("name", "twitter:image");
    }
    setMeta("name", "twitter:card", image ? "summary_large_image" : "summary");
    setMeta("name", "twitter:title", fullTitle);
    setMeta("name", "twitter:description", desc);
  }, [title, description, image, type, noIndex]);
}
