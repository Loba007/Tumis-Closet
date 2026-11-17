import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import toast from "react-hot-toast";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as cartApi from "../api/cart";
import { useAuth } from "./AuthContext";
import { CartProvider, useCart } from "./CartContext";

vi.mock("react-hot-toast", () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));
vi.mock("../api/cart", () => ({
  fetchCart: vi.fn(),
  addToCart: vi.fn(),
  updateCartItem: vi.fn(),
  removeCartItem: vi.fn(),
}));
vi.mock("./AuthContext", () => ({ useAuth: vi.fn() }));

function Consumer() {
  const { cart, cartLoading, addItem } = useCart();
  return (
    <div>
      <span data-testid="count">{cart ? cart.items.length : "none"}</span>
      <span data-testid="loading">{String(cartLoading)}</span>
      <button onClick={() => addItem(7)}>Add</button>
    </div>
  );
}

function renderCart() {
  return render(
    <CartProvider>
      <Consumer />
    </CartProvider>
  );
}

describe("CartContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("does not fetch a cart for anonymous users", async () => {
    useAuth.mockReturnValue({ user: null });
    renderCart();
    await waitFor(() => expect(screen.getByTestId("loading")).toHaveTextContent("false"));
    expect(cartApi.fetchCart).not.toHaveBeenCalled();
    expect(screen.getByTestId("count")).toHaveTextContent("none");
  });

  it("loads the cart and appends an item", async () => {
    useAuth.mockReturnValue({ user: { id: 1 } });
    cartApi.fetchCart.mockResolvedValue({ items: [{ id: 1 }] });
    cartApi.addToCart.mockResolvedValue({ items: [{ id: 1 }, { id: 2 }] });

    renderCart();
    await waitFor(() => expect(screen.getByTestId("count")).toHaveTextContent("1"));

    await userEvent.click(screen.getByRole("button", { name: "Add" }));

    await waitFor(() => expect(screen.getByTestId("count")).toHaveTextContent("2"));
    expect(cartApi.addToCart).toHaveBeenCalledWith(7, 1);
    expect(toast.success).toHaveBeenCalledWith("Added to bag");
  });
});
