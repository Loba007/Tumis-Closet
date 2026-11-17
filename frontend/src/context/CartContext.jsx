import { createContext, useContext, useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import * as cartApi from "../api/cart";
import { useAuth } from "./AuthContext";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(null);
  const [cartLoading, setCartLoading] = useState(true);
  const [cartError, setCartError] = useState("");
  const refreshId = useRef(0);

  const refresh = async () => {
    const requestId = ++refreshId.current;
    if (!user) {
      setCart(null);
      setCartError("");
      setCartLoading(false);
      return;
    }

    setCartLoading(true);
    setCartError("");
    try {
      const data = await cartApi.fetchCart();
      if (requestId === refreshId.current) setCart(data);
    } catch (err) {
      if (requestId === refreshId.current) {
        setCartError(err.response?.data?.detail || "Could not load your bag. Please try again.");
      }
    } finally {
      if (requestId === refreshId.current) setCartLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const addItem = async (variantId, quantity = 1) => {
    try {
      const data = await cartApi.addToCart(variantId, quantity);
      setCart(data);
      toast.success("Added to bag");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not add to bag");
    }
  };

  const updateItem = async (itemId, quantity) => {
    try {
      const data = await cartApi.updateCartItem(itemId, quantity);
      setCart(data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not update your bag.");
    }
  };

  const removeItem = async (itemId) => {
    try {
      const data = await cartApi.removeCartItem(itemId);
      setCart(data);
    } catch {
      toast.error("Could not remove that item.");
    }
  };

  return (
    <CartContext.Provider
      value={{ cart, cartLoading, cartError, refresh, addItem, updateItem, removeItem }}
    >
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
