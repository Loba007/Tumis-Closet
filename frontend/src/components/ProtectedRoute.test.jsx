import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuth } from "../context/AuthContext";
import ProtectedRoute from "./ProtectedRoute";

vi.mock("../context/AuthContext", () => ({ useAuth: vi.fn() }));

function renderProtected() {
  return render(
    <MemoryRouter initialEntries={["/orders"]}>
      <Routes>
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <div>Private orders</div>
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<div>Login page</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    useAuth.mockReset();
  });

  it("redirects anonymous visitors to login", () => {
    useAuth.mockReturnValue({ user: null, loading: false });
    renderProtected();
    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("renders nothing while the session is loading", () => {
    useAuth.mockReturnValue({ user: null, loading: true });
    const { container } = renderProtected();
    expect(container).toBeEmptyDOMElement();
  });

  it("renders children for authenticated users", () => {
    useAuth.mockReturnValue({ user: { id: 1 }, loading: false });
    renderProtected();
    expect(screen.getByText("Private orders")).toBeInTheDocument();
  });
});
